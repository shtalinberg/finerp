
import csv
import datetime
import io
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple

from django.db import transaction
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from income_book.constants import INCOME_TYPES
from taxpayers.models import Taxpayer

from .models import IncomeRecord


class IncomeBookService:
    """Сервіс для роботи з книгою доходів"""

    @staticmethod
    def generate_quarterly_report(taxpayer: Taxpayer, year: int, quarter: int) -> Dict:
        """
        Сформувати квартальний звіт про доходи

        Args:
            taxpayer: Об'єкт платника податків
            year: Рік
            quarter: Квартал (1-4)

        Returns:
            Словник з даними звіту
        """
        # Визначаємо дати кварталу
        if quarter == 1:
            start_date = datetime.date(year, 1, 1)
            end_date = datetime.date(year, 3, 31)
        elif quarter == 2:
            start_date = datetime.date(year, 4, 1)
            end_date = datetime.date(year, 6, 30)
        elif quarter == 3:
            start_date = datetime.date(year, 7, 1)
            end_date = datetime.date(year, 9, 30)
        else:
            start_date = datetime.date(year, 10, 1)
            end_date = datetime.date(year, 12, 31)

        # Отримуємо записи доходів за квартал
        records = IncomeRecord.objects.filter(
            taxpayer=taxpayer,
            date__gte=start_date,
            date__lte=end_date,
            status='active'
        ).order_by('date')

        # Загальна сума доходів
        total_income = records.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Розбивка по місяцях
        months = []
        for month in range(3):
            month_number = (quarter - 1) * 3 + month + 1
            month_records = records.filter(date__month=month_number)
            month_total = month_records.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            months.append({
                'number': month_number,
                'name': datetime.date(year, month_number, 1).strftime('%B'),
                'records': month_records,
                'total': month_total
            })

        # Розрахунок податків
        tax_rate = taxpayer.tax_rate / 100
        income_tax = total_income * Decimal(str(tax_rate))
        military_tax = total_income * Decimal('0.015')  # 1.5% військовий збір

        return {
            'taxpayer': taxpayer,
            'year': year,
            'quarter': quarter,
            'start_date': start_date,
            'end_date': end_date,
            'records': records,
            'months': months,
            'total_income': total_income,
            'income_tax': income_tax,
            'military_tax': military_tax,
            'total_tax': income_tax + military_tax
        }

    @staticmethod
    def export_to_csv(taxpayer: Taxpayer, start_date: datetime.date, end_date: datetime.date) -> str:
        """
        Експортувати записи книги доходів у форматі CSV

        Args:
            taxpayer: Об'єкт платника податків
            start_date: Початкова дата
            end_date: Кінцева дата

        Returns:
            CSV-дані як рядок
        """
        # Отримуємо записи доходів
        records = IncomeRecord.objects.filter(
            taxpayer=taxpayer,
            date__gte=start_date,
            date__lte=end_date,
            status='active'
        ).order_by('date')

        # Створюємо CSV-файл
        output = io.StringIO()
        writer = csv.writer(output)

        # Заголовок
        writer.writerow([
            _('Дата'),
            _('Номер документа'),
            _('Сума'),
            _('Тип доходу'),
            _('Опис'),
            _('Примітки')
        ])

        # Дані
        for record in records:
            writer.writerow([
                record.date.strftime('%d.%m.%Y'),
                record.document_number,
                str(record.amount),
                dict(INCOME_TYPES).get(record.income_type, record.income_type),
                record.description,
                record.notes or ''
            ])

        return output.getvalue()

    @staticmethod
    @transaction.atomic
    def import_from_csv(taxpayer: Taxpayer, csv_data: str) -> Tuple[int, List[str]]:
        """
        Імпортувати записи книги доходів з CSV-файлу

        Args:
            taxpayer: Об'єкт платника податків
            csv_data: Дані CSV-файлу

        Returns:
            Кортеж (кількість імпортованих записів, список помилок)
        """
        input_file = io.StringIO(csv_data)
        reader = csv.reader(input_file)

        # Пропускаємо заголовок
        next(reader, None)

        imported_count = 0
        errors = []

        for row_num, row in enumerate(reader, start=2):
            try:
                if len(row) < 4:
                    errors.append(f"Рядок {row_num}: недостатньо даних")
                    continue

                # Розбираємо дані
                date_str, document_number, amount_str, income_type = row[:4]
                description = row[4] if len(row) > 4 else ''
                notes = row[5] if len(row) > 5 else None

                # Парсимо дату
                try:
                    day, month, year = map(int, date_str.split('.'))
                    date = datetime.date(year, month, day)
                except (ValueError, TypeError):
                    errors.append(f"Рядок {row_num}: неправильний формат дати (очікується ДД.ММ.РРРР)")
                    continue

                # Парсимо суму
                try:
                    amount = Decimal(amount_str.replace(',', '.'))
                except (ValueError, TypeError, InvalidOperation):
                    errors.append(f"Рядок {row_num}: неправильний формат суми")
                    continue

                # Знаходимо код типу доходу
                income_type_code = None
                for code, label in INCOME_TYPES:
                    if income_type.lower() == label.lower():
                        income_type_code = code
                        break

                if not income_type_code:
                    income_type_code = 'other'

                # Створюємо запис
                IncomeRecord.objects.create(
                    taxpayer=taxpayer,
                    date=date,
                    document_number=document_number,
                    amount=amount,
                    income_type=income_type_code,
                    description=description,
                    notes=notes
                )

                imported_count += 1

            except Exception as e:
                errors.append(f"Рядок {row_num}: {str(e)}")

        return imported_count, errors