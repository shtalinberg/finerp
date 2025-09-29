
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
    """Сервіс для синхронізації фінансових операцій з ПриватБанку"""

    def __init__(self, token=None):
        self.client = P24ApiAutoClient(token=token)

    def sync_finops(self,
                   taxpayer: Taxpayer,
                   bank_account: BankAccount,
                   start_date: datetime.date,
                   end_date: datetime.date) -> Tuple[int, int]:
        """
        Синхронізація фінансових операцій з ПриватБанку за вказаний період

        Args:
            taxpayer: Екземпляр Taxpayer
            bank_account: Екземпляр BankAccount
            start_date: Початкова дата
            end_date: Кінцева дата

        Returns:
            Кортеж, що містить (кількість нових операцій, кількість оновлених операцій)
        """
        if not bank_account.acc_iban:
            logger.error(f"Банківський рахунок {bank_account} не має IBAN.")
            return 0, 0

        # Отримуємо транзакції з ПриватБанку
        response = self.client.get_transactions(
            start_date=start_date,
            end_date=end_date,
            acc=bank_account.acc_iban
        )

        if response.get('status') != 'SUCCESS':
            logger.error(f"Не вдалося отримати транзакції: {response.get('errorMessage', 'Невідома помилка')}")
            return 0, 0

        # Обробляємо транзакції
        transactions = response.get('transactions', [])
        new_count, updated_count = self._process_transactions(taxpayer, bank_account, transactions)

        # Обробка пагінації, якщо потрібно
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
        """Обробка транзакцій з API ПриватБанку"""
        new_count = 0
        updated_count = 0

        for bank_trans in transactions:
            # Витягуємо дані транзакції
            bank_id = bank_trans.get('id')
            amount = Decimal(str(bank_trans.get('amount', '0')))
            amount_uah = amount  # За замовчуванням така ж сума, якщо в гривнях

            # Обробка конвертації валюти, якщо потрібно
            currency = bank_trans.get('currency', 'UAH')
            if currency != 'UAH':
                # Імплементація логіки конвертації валюти
                amount_uah = Decimal(str(bank_trans.get('amountNat', '0')))

            # Визначаємо тип операції
            op_type = 'income' if amount > 0 else 'expense'

            # Отримуємо існуючу операцію або створюємо нову
            finop, created = Finop.objects.update_or_create(
                bank_operation_id=bank_id,
                bank_account=bank_account,
                defaults={
                    'taxpayer': taxpayer,
                    'operation_date': datetime.datetime.fromisoformat(bank_trans.get('dateTime')),
                    'amount': abs(amount),
                    'amount_uah': abs(amount_uah),
                    'description': bank_trans.get('description', ''),
                    'operation_type': op_type,
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