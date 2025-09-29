from django.core import serializers
from django.core.management.base import BaseCommand

from privat24api.models import CurrencyRateHistory


class Command(BaseCommand):
    help = 'Creates a fixture from CurrencyRateHistory model data'
    """
    This command creates a fixture from the CurrencyRateHistory model data.

    Usage:
        python manage.py create_currency_history_fixture --output <output_file> --limit <limit> --iso <iso_code>
        python manage.py create_currency_history_fixture --output=my_fixture.json
        python manage.py create_currency_history_fixture --output=my_fixture.json --limit=1000 --iso=USD
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            dest='output',
            default='currency_rate_history_fixture.json',
            help='Output file name for the fixture',
        )
        parser.add_argument(
            '--limit',
            type=int,
            dest='limit',
            default=None,
            help='Limit the number of records to export',
        )
        parser.add_argument(
            '--iso',
            dest='iso_code',
            default=None,
            help='Filter by ISO code (e.g., USD)',
        )

    def handle(self, *args, **options):
        output_file = options['output']
        limit = options['limit']
        iso_code = options['iso_code']

        # Отримуємо дані з бази
        queryset = CurrencyRateHistory.objects.all()

        # Застосовуємо фільтри, якщо вказані
        if iso_code:
            queryset = queryset.filter(iso_code=iso_code)

        # Обмежуємо кількість записів, якщо вказано
        if limit:
            queryset = queryset[:limit]

        # Серіалізуємо дані
        data = serializers.serialize('json', queryset)

        # Зберігаємо у файл
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(data)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created fixture with {queryset.count()} records in {output_file}'
            )
        )
