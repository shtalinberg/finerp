
import datetime
import logging
from decimal import Decimal
from typing import Dict, List, Tuple

from django.db import transaction

from banks.models import BankAccount
from finops.models import Finop
from privat24api.api_autoclient import P24ApiAutoClient
from taxpayers.models import Taxpayer

logger = logging.getLogger(__name__)

class PrivatBankSyncService:
    """Service to synchronize transactions from PrivatBank"""

    def __init__(self, token=None):
        self.client = P24ApiAutoClient(token=token)

    def sync_transactions(self,
                          taxpayer: Taxpayer,
                          bank_account: BankAccount,
                          start_date: datetime.date,
                          end_date: datetime.date) -> Tuple[int, int]:
        """
        Synchronize transactions from PrivatBank for the given period

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

        # Fetch transactions from PrivatBank
        response = self.client.get_transactions(
            start_date=start_date,
            end_date=end_date,
            acc=bank_account.acc_iban
        )

        if response.get('status') != 'SUCCESS':
            logger.error(f"Failed to get transactions: {response.get('errorMessage', 'Unknown error')}")
            return 0, 0

        # Process transactions
        transactions = response.get('transactions', [])
        new_count, updated_count = self._process_transactions(taxpayer, bank_account, transactions)

        # Handle pagination if needed
        while response.get('exist_next_page', False) and response.get('next_page_id'):
            response = self.client.get_transactions(
                start_date=start_date,
                end_date=end_date,
                acc=bank_account.acc_iban,
                follow_id=response.get('next_page_id')
            )

            if response.get('status') != 'SUCCESS':
                break

            trans_new, trans_updated = self._process_transactions(taxpayer, bank_account, response.get('transactions', []))
            new_count += trans_new
            updated_count += trans_updated

        return new_count, updated_count

    @transaction.atomic
    def _process_transactions(self,
                              taxpayer: Taxpayer,
                              bank_account: BankAccount,
                              transactions: List[Dict]) -> Tuple[int, int]:
        """Process transactions from PrivatBank API"""
        new_count = 0
        updated_count = 0

        for bank_trans in transactions:
            # Extract transaction data
            bank_id = bank_trans.get('id')
            amount = Decimal(str(bank_trans.get('amount', '0')))
            amount_uah = amount  # Default to same amount if in UAH

            # Handle currency conversion if needed
            currency = bank_trans.get('currency', 'UAH')
            if currency != 'UAH':
                # Implement currency conversion logic here
                amount_uah = Decimal(str(bank_trans.get('amountNat', '0')))

            # Determine transaction type
            trans_type = 'income' if amount > 0 else 'expense'

            # Get existing transaction or create new one
            trans, created = Finop.objects.update_or_create(
                bank_transaction_id=bank_id,
                bank_account=bank_account,
                defaults={
                    'taxpayer': taxpayer,
                    'transaction_date': datetime.datetime.fromisoformat(bank_trans.get('dateTime')),
                    'amount': abs(amount),
                    'amount_uah': abs(amount_uah),
                    'description': bank_trans.get('description', ''),
                    'transaction_type': trans_type,
                    'sender_name': bank_trans.get('senderName', ''),
                    'sender_account': bank_trans.get('senderAccount', ''),
                    'recipient_name': bank_trans.get('recipientName', ''),
                    'recipient_account': bank_trans.get('recipientAccount', ''),
                    'is_processed': False
                }
            )

            if created:
                new_count += 1
            else:
                updated_count += 1

        return new_count, updated_count