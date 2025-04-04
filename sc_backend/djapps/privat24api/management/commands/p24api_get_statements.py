"""
Management command to fetch and process bank statements from Privat24 API.
"""
import json
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.mail import mail_admins
from django.core.management import BaseCommand
from django.db import transaction

from privat24api import signals
from privat24api.api_autoclient import P24ApiAutoClient
from privat24api.models import Statement

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Command to fetch transaction statements from Privat24 API.

    Retrieves transaction data for the specified time period
    and creates Statement records in the database.
    python sc_backend/manage.py p24api_get_statements --account=ВАШ_НОМЕР_РАХУНКУ
    python sc_backend/manage.py p24api_get_statements --start-date=01-01-2023 --end-date=31-12-2023 --debug
    """

    help = "Fetch and process transaction statements from Privat24 API"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_debug_mode = False
        self.api_client = None
        self.success_count = 0
        self.error_count = 0
        self.skipped_count = 0

    def add_arguments(self, parser):
        """
        Add command-line arguments.
        """
        parser.add_argument(
            '--debug',
            action='store_true',
            default=False,
            help='Enable debug mode with verbose output',
        )
        parser.add_argument(
            '--days',
            type=int,
            dest="days_before",
            default=14,
            help='Number of days before today to fetch data for (default: 14)',
        )
        parser.add_argument(
            '--interim',
            action='store_true',
            default=False,
            help='Include interim (pending) transactions',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of transactions to fetch per API call (max 500)',
        )
        parser.add_argument(
            '--account',
            dest='account',
            help='Specific account number to fetch transactions for',
        )
        parser.add_argument(
            '--start-date',
            dest='start_date',
            help='Start date for fetching transactions (format: DD-MM-YYYY)',
        )
        parser.add_argument(
            '--end-date',
            dest='end_date',
            help='End date for fetching transactions (format: DD-MM-YYYY)',
        )

    def handle(self, *args, **options):
        """
        Main command execution method.

        Fetches statements from the API and processes them.
        """
        # Process command options
        self.is_debug_mode = options.get('debug', False)
        days_before = int(options.get('days_before', 14))
        interim = options.get('interim', False)
        batch_size = min(options.get('batch_size', 100), 500)  # API max is 500
        account = options.get('account')

        # Parse custom date range if provided
        start_date = None
        end_date = None

        if options.get('start_date'):
            try:
                start_date = datetime.strptime(options.get('start_date'), '%d-%m-%Y').date()
            except ValueError:
                self.stderr.write(self.style.ERROR("Invalid start date format. Use DD-MM-YYYY."))
                return

        if options.get('end_date'):
            try:
                end_date = datetime.strptime(options.get('end_date'), '%d-%m-%Y').date()
            except ValueError:
                self.stderr.write(self.style.ERROR("Invalid end date format. Use DD-MM-YYYY."))
                return

        # Set default dates if not provided
        if not end_date:
            end_date = date.today()

        if not start_date:
            start_date = end_date - timedelta(days=days_before)

        # Validate date range
        if start_date > end_date:
            self.stderr.write(self.style.ERROR("Start date cannot be after end date"))
            return

        # Setup API client
        self.api_client = P24ApiAutoClient()

        # Check API availability
        if not self._check_api_availability():
            self.stderr.write(self.style.ERROR('Cannot connect to Privat24 API'))
            return

        # Process statements in smaller time chunks to avoid API limits
        self._process_statements_in_chunks(start_date, end_date, interim, batch_size, account)

        # Show summary of operations
        self._display_summary()

    def _build_transactions_resource(
        self,
        interim: bool = False,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        follow_id: Optional[str] = None,
        acc: Optional[str] = None
    ) -> str:
        """
        Build the API resource URL for transactions.

        Args:
            interim: Whether to get interim (pending) transactions
            start_date: Start date for transactions
            end_date: End date for transactions
            limit: Maximum number of transactions to return
            follow_id: ID for pagination from next_page_id
            acc: Account number

        Returns:
            Formatted resource URL for API request
        """
        resource = 'statements/transactions'
        if interim:
            resource = f'{resource}/interim'

        # Build query parameters
        resource = f'{resource}?limit={min(limit, 500)}'  # Ensure limit is within bounds

        if acc:
            resource = f'{resource}&acc={acc}'

        if follow_id:
            resource = f'{resource}&followId={follow_id}'

        if start_date and end_date:
            start_date_str = start_date.strftime('%d-%m-%Y')
            end_date_str = end_date.strftime('%d-%m-%Y')
            resource = f'{resource}&startDate={start_date_str}&endDate={end_date_str}'

        return resource

    def _check_api_availability(self) -> bool:
        """
        Check if the API is available by getting server time.

        Returns:
            True if API is available, False otherwise
        """
        try:
            resp = self.api_client.get_server_time()
            if resp.status_code != 200:
                self.stderr.write(self.style.ERROR(f'API returned status code {resp.status_code}'))
                return False

            jdata = json.loads(resp.content)
            if jdata.get('status') != 'SUCCESS':
                self.stderr.write(self.style.ERROR(f'API returned error: {jdata.get("errorMessage")}'))
                self._notify_admins_about_api_failure()
                return False

            return True

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error checking API availability: {e}'))
            return False

    def _process_statements_in_chunks(
        self,
        start_date: date,
        end_date: date,
        interim: bool,
        batch_size: int,
        account: Optional[str] = None
    ):
        """
        Process statements in time chunks to avoid API limitations.

        The API has a limit of 15 days per request, so we break down longer
        periods into multiple requests.

        Args:
            start_date: Start date for statements
            end_date: End date for statements
            interim: Whether to include interim transactions
            batch_size: Number of transactions per request
            account: Optional account number to filter by
        """
        MAX_DAYS_PER_CHUNK = 15  # API limitation

        self.stdout.write(f"Fetching statements from {start_date} to {end_date}")

        if account:
            self.stdout.write(f"Filtering for account: {account}")

        # Process in chunks of MAX_DAYS_PER_CHUNK days
        current_start = start_date
        while current_start <= end_date:
            # Calculate end of current chunk
            current_end = min(current_start + timedelta(days=MAX_DAYS_PER_CHUNK-1), end_date)

            if self.is_debug_mode:
                self.stdout.write(f"Processing chunk from {current_start} to {current_end}")

            # Fetch and process statements for current chunk
            self._fetch_and_process_statements(
                current_start,
                current_end,
                interim,
                batch_size,
                account
            )

            # Move to next chunk
            current_start = current_end + timedelta(days=1)

    def _fetch_and_process_statements(
        self,
        start_date: date,
        end_date: date,
        interim: bool,
        batch_size: int,
        account: Optional[str] = None
    ):
        """
        Fetch statements for a specific date range and process them.

        Args:
            start_date: Start date for statements
            end_date: End date for statements
            interim: Whether to include interim transactions
            batch_size: Number of transactions per request
            account: Optional account number to filter by
        """
        try:
            # Handle pagination
            follow_id = None
            has_more = True
            total_processed = 0

            while has_more:
                # Fetch transactions with pagination info from API
                response_data = self.api_client.get_transactions(
                    interim=interim,
                    start_date=start_date,
                    end_date=end_date,
                    limit=batch_size,
                    follow_id=follow_id,
                    acc=account
                )

                # Check if response was successful
                if response_data.get('status') != 'SUCCESS':
                    self.stderr.write(self.style.ERROR(f"API returned error: {response_data.get('errorMessage', 'Unknown error')}"))
                    break

                # Get transactions from response
                transactions = response_data.get('transactions', [])

                if not transactions:
                    has_more = False
                    if self.is_debug_mode and total_processed == 0:
                        self.stdout.write("No transactions found for this period")
                    break

                # Track for pagination based on API response
                total_processed += len(transactions)

                # Check if we need to fetch more pages based on API response
                has_more = response_data.get('exist_next_page', False)

                # Get next_page_id for pagination
                if has_more:
                    follow_id = response_data.get('next_page_id')
                    if self.is_debug_mode:
                        self.stdout.write(f"Next page ID: {follow_id}")

                # Process each transaction
                for transaction in transactions:
                    try:
                        self._process_transaction(transaction)
                    except Exception as e:
                        self.error_count += 1
                        logger.exception(f"Error processing transaction: {e}")
                        if self.is_debug_mode:
                            self.stderr.write(self.style.ERROR(f"Error processing transaction: {e}"))

                if self.is_debug_mode:
                    self.stdout.write(f"Processed {total_processed} transactions so far")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error fetching transactions: {e}"))
            logger.exception(f"Error fetching transactions: {e}")

    @transaction.atomic
    def _process_transaction(self, tr_item: Dict[str, Any]):
        """
        Process a single transaction item from the API.

        Args:
            tr_item: Transaction data from API
        """
        # Extract key identifiers for statement
        btid = tr_item.get('ID')  # ID транзакції
        info_ref = tr_item.get('REF')  # Референс проводки
        info_number = tr_item.get('NUM_DOC')  # Номер документа

        if not all([btid, info_ref, info_number]):
            self.skipped_count += 1
            if self.is_debug_mode:
                self.stdout.write("Skipping transaction with missing key identifiers")
            return

        # Check if statement already exists
        existing_statement = Statement.objects.filter(
            btid=btid,
            info_ref=info_ref,
            info_number=info_number,
        ).first()

        if existing_statement:
            self.skipped_count += 1
            if self.is_debug_mode:
                self.stdout.write(f"Statement already exists: {btid} {info_ref}")
            return

        # Debug output
        if self.is_debug_mode:
            self.stdout.write("=" * 20)
            self.stdout.write(f"Processing transaction: {tr_item.get('DATE_TIME_DAT_OD_TIM_P')}")
            self.stdout.write(f"ID: {btid}, REF: {info_ref}")

        # Create new statement
        try:
            statement = self._create_statement_from_transaction(tr_item)

            # Send signal that statement was created
            signals.p24statement_was_created.send(
                sender=Statement,
                instance=statement,
            )

            self.success_count += 1

            if self.is_debug_mode:
                self.stdout.write(self.style.SUCCESS(f"Created statement: {statement}"))

        except Exception as e:
            self.error_count += 1
            logger.exception(f"Error creating statement from transaction: {e}")
            if self.is_debug_mode:
                self.stderr.write(self.style.ERROR(f"Error creating statement: {e}"))
            raise

    def _create_statement_from_transaction(self, tr_item: Dict[str, Any]) -> Statement:
        """
        Create a Statement object from transaction data.

        Args:
            tr_item: Transaction data from API

        Returns:
            Created Statement object
        """
        # Parse dates from API format
        dt_mask = '%d.%m.%Y %H:%M:%S'
        d_mask = '%d.%m.%Y'

        # Handle potentially missing or malformed dates
        try:
            postdate = datetime.strptime(tr_item.get('DATE_TIME_DAT_OD_TIM_P', ''), dt_mask)
        except (ValueError, TypeError):
            postdate = None

        try:
            customerdate = datetime.strptime(tr_item.get('DAT_KL', ''), d_mask)
        except (ValueError, TypeError):
            customerdate = None

        try:
            currency_exchange_at = datetime.strptime(tr_item.get('DAT_OD', ''), d_mask)
        except (ValueError, TypeError):
            currency_exchange_at = None

        # Handle potentially missing numeric values
        try:
            amount_amt = Decimal(tr_item.get('SUM', 0))
        except (ValueError, TypeError):
            amount_amt = Decimal('0.00')

        try:
            amount_amt_uah = Decimal(tr_item.get('SUM_E', 0))
        except (ValueError, TypeError):
            amount_amt_uah = Decimal('0.00')

        # Create statement with all extracted data
        return Statement.objects.create(
            btid=tr_item.get('ID'),  # ID транзакції
            info_number=tr_item.get('NUM_DOC'),
            info_postdate=postdate,
            info_customerdate=customerdate,
            info_ref=tr_item.get('REF'),
            info_state=tr_item.get('PR_PR'),  # Стан p-проводиться, t-сторнирована, r-проведена, n-забракована
            info_flinfo=tr_item.get('FL_REAL'),  # Ознака реальності проводки(r,i)
            info_doctype=tr_item.get('DOC_TYP'),
            amount_amt=amount_amt,
            amount_amt_uah=amount_amt_uah,
            caccount_name=tr_item.get('AUT_MY_NAM'),  # Назва отримувача
            caccount_number=tr_item.get('AUT_MY_ACC'),  # Рахунок отримувача
            caccount_customer_crf=tr_item.get('AUT_MY_CRF'),  # ЄДРПОУ отримувача
            caccount_customer_bank_code=tr_item.get('AUT_MY_MFO'),  # МФО отримувача
            caccount_customer_bank_name=tr_item.get('AUT_MY_MFO_NAME'),  # Банк отримувача
            trantype=tr_item.get('TRANTYPE'),  # Тип транзакції дебет/кредит (D, C)
            curency_iso=tr_item.get('CCY', 'UAH'),  # Код валюти
            currency_exchange_at=currency_exchange_at,  # дата валютування
            daccount_name=tr_item.get('AUT_CNTR_NAM'),  # Назва контрагента,
            daccount_number=tr_item.get('AUT_CNTR_ACC'),  # Рахунок контрагента
            daccount_customer_crf=tr_item.get('AUT_CNTR_CRF'),  # ЄДРПОУ контрагента
            daccount_customer_bank_code=tr_item.get('AUT_CNTR_MFO'),  # МФО контрагента
            daccount_customer_bank_name=tr_item.get('AUT_CNTR_MFO_NAME'),  # Назва банка контрагента
            purpose=tr_item.get('OSND'),  # Підстава платежу
        )

    def _notify_admins_about_api_failure(self):
        """
        Send notification email to admins about API authentication failure.
        """
        mail_admins(
            subject='Privat24 API Authentication Failed',
            message="""
                The management command failed to authenticate with the Privat24 API.
                Please check the API credentials and try again.

                This is an automated message from the system.
            """,
        )

    def _display_summary(self):
        """
        Display summary of processed statements.
        """
        self.stdout.write("\nOperation completed")
        self.stdout.write("-" * 40)
        self.stdout.write(f"Statements successfully created: {self.success_count}")
        self.stdout.write(f"Statements skipped (already exist): {self.skipped_count}")
        self.stdout.write(f"Errors encountered: {self.error_count}")
        self.stdout.write("-" * 40)

        if self.error_count > 0:
            self.stdout.write(self.style.WARNING("There were errors. Check the logs for details."))
        else:
            self.stdout.write(self.style.SUCCESS("All operations completed successfully."))