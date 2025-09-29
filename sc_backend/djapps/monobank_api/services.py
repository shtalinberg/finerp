
import datetime
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from django.db import transaction

from banks.models import BankAccount
from finops.models import Finop
from monobank_api.api_client import MonoBankClient
from taxpayers.models import Taxpayer

logger = logging.getLogger(__name__)

class MonoBankSyncService:
    """Service to synchronize transactions from MonoBank"""

    def __init__(self, token=None):
        self.client = MonoBankClient(token=token)

    def get_account_id(self, bank_account: BankAccount) -> Optional[str]:
        """
        Get MonoBank account ID by IBAN

        Args:
            bank_account: BankAccount instance

        Returns:
            MonoBank account ID or None if not found
        """
        client_info = self.client.get_client_info()

        if 'accounts' not in client_info:
            logger.error("Failed to get MonoBank accounts")
            return None

        for account in client_info['accounts']:
            if account.get('iban') == bank_account.acc_iban:
                return account.get('id')

        logger.error(f"MonoBank account with IBAN {bank_account.acc_iban} not found")
        return None

    def sync_transactions(self,
                          taxpayer: Taxpayer,
                          bank_account: BankAccount,
                          start_date: datetime.date,
                          end_date: datetime.date) -> Tuple[int, int]:
        """
        Synchronize transactions from MonoBank for the given period

        Args:
            taxpayer: Taxpayer instance
            bank_account: BankAccount instance
            start_date: Start date for transactions
            end_date: End date for transactions

        Returns:
            Tuple containing (number of new transactions, number of updated transactions)
        """
        if not bank_account.acc_iban:
            logger.error(f"Bank account {bank_account} has no IBAN.")
            return 0, 0

        # Get MonoBank account ID
        account_id = self.get_account_id(bank_account)
        if not account_id:
            return 0, 0

        # Convert dates to Unix timestamps
        from_time = int(datetime.datetime.combine(start_date, datetime.time.min).timestamp())
        to_time = int(datetime.datetime.combine(end_date, datetime.time.max).timestamp())

        # Fetch transactions from MonoBank
        transactions = self.client.get_statement(account_id, from_time, to_time)

        if not transactions:
            logger.error("No transactions found or error occurred")
            return 0, 0

        # Process transactions
        new_count, updated_count = self._process_transactions(taxpayer, bank_account, transactions)

        return new_count, updated_count

    @transaction.atomic
    def _process_transactions(self,
                              taxpayer: Taxpayer,
                              bank_account: BankAccount,
                              transactions: List[Dict]) -> Tuple[int, int]:
        """Process transactions from MonoBank API"""
        new_count = 0
        updated_count = 0

        for bank_trans in transactions:
            # Extract transaction data
            bank_id = str(bank_trans.get('id'))
            amount = Decimal(str(bank_trans.get('amount', '0'))) / 100  # MonoBank returns amount in kopecks

            # Currency conversion for non-UAH accounts
            currency_code = bank_trans.get('currencyCode', 980)  # 980 is UAH
            amount_uah = amount

            if currency_code != 980:
                # Implement currency conversion logic if needed
                # MonoBank provides exchangeRate for currency conversions
                if 'operationAmount' in bank_trans:
                    amount_uah = Decimal(str(bank_trans.get('operationAmount', '0'))) / 100

            # Determine transaction type
            if bank_trans.get('amount', 0) > 0:
                trans_type = 'income'
            else:
                trans_type = 'expense'

            # Process transaction datetime
            trans_time = datetime.datetime.fromtimestamp(bank_trans.get('time', 0))

            # Description and counterpart info
            description = bank_trans.get('description', '')
            mcc = bank_trans.get('mcc', 0)  # Merchant Category Code

            # Get existing transaction or create new one
            trans, created = Finop.objects.update_or_create(
                bank_transaction_id=bank_id,
                bank_account=bank_account,
                defaults={
                    'taxpayer': taxpayer,
                    'transaction_date': trans_time,
                    'amount': abs(amount),
                    'amount_uah': abs(amount_uah),
                    'description': description,
                    'transaction_type': trans_type,
                    # MonoBank doesn't provide sender/recipient details in the same way as PrivatBank
                    'is_processed': False
                }
            )

            if created:
                new_count += 1
            else:
                updated_count += 1

        return new_count, updated_count