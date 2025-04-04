
import json
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal as D

from django.core.management import BaseCommand

from privat24api import signals
from privat24api.api_autoclient import P24ApiAutoClient
from privat24api.models import CurrencyRateHistory

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Отримання курсів валют"

    args = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            dest="debug",
            action='store_true',
            default=False,
            help='Debug mode',
        )
        parser.add_argument(
            '--days', dest="days_before", default=14, help='days before today'
        )

    def handle(self, *args, **options):
        MAX_DAYS = 15
        # Перетворюємо days_before з рядка у ціле число
        days_before = int(options.get('days_before', 14))
        self.is_debug_mode = options.get('debug')
        p24_client = P24ApiAutoClient()

        resp = p24_client.get_server_time()
        if resp.status_code != 200:
            print('Cannot receive data from API')
        else:
            jdata = json.loads(resp.content)
            if jdata['status'] == 'SUCCESS':
                end_date = date.today()
                start_date = end_date - timedelta(days=days_before)

                # Розбиваємо великий період на частини по MAX_DAYS днів
                current_start_date = start_date

                while current_start_date <= end_date:
                    # Визначаємо поточний кінцевий день періоду
                    current_end_date = min(
                        current_start_date + timedelta(days=MAX_DAYS-1),  # -1 щоб включити сам день
                        end_date
                    )

                    if self.is_debug_mode:
                        print(f"Fetching data from {current_start_date} to {current_end_date}")

                    # Отримуємо дані для поточного періоду
                    response_dict = p24_client.get_currency_history(
                        start_date=current_start_date,
                        end_date=current_end_date
                    )

                    # Тут обробіть отримані дані
                    if self.is_debug_mode:
                        print('=' * 20)
                        print(response_dict)

                    if response_dict:
                        cache_info = response_dict.get('cache_info', {})
                        from_cache = cache_info.get('from_cache', False)

                        for history_item in response_dict['data']['history']:
                            self.process_item(history_item, from_cache=from_cache)

                    # Переміщуємо початкову дату для наступної ітерації
                    current_start_date = current_end_date + timedelta(days=1)


    def process_item(self, ch_item, from_cache=False):
        """
        from_cache – ознака кешування даних;
        cache_time – час кешування (в мілісекундах);
        server_time – поточний час сервера (в мілісекундах);
        B – купівля;
        S – продаж;
        date – дата курсу;
        rate – курс;
        rate_delta – зміна курсу;
        nbuRate – курс НБУ.
        """

        if self.is_debug_mode:
            print('=' * 20)
            print(ch_item)

        # dt_mask = '%d-%m-%Y %H:%M:%S'
        d_mask = '%d-%m-%Y'

        cur_iso=ch_item.get('currencyCode')
        for rate_type in ['B', 'S']:
            rate_date = datetime.strptime(ch_item.get('date'), d_mask)
            rate_nbu = D(ch_item.get('nbuRate'))

            if rate_type == 'B':
                if ch_item.get('rate_b') is None:
                    logger.warning(
                        f"Currency rate for {cur_iso} not found for date {rate_date}"
                    )
                    continue
                rate = D(ch_item.get('rate_b'))
                rate_delta = D(ch_item.get('rate_b_delta'))
            else:
                if ch_item.get('rate_s') is None:
                    logger.warning(
                        f"Currency rate for {cur_iso} not found for date {rate_date}"
                    )
                    continue
                rate = D(ch_item.get('rate_s'))
                rate_delta = D(ch_item.get('rate_s_delta'))

            crh_obj, crh_created = CurrencyRateHistory.objects.get_or_create(
                iso_code=cur_iso,
                rate_datetime__date=rate_date,
                rate=rate,
                rate_delta=rate_delta,
                rate_nbu=rate_nbu,
                rate_type=rate_type,
                defaults={"rate_datetime": rate_date}
            )
            if crh_created:
                logger.info(
                    f"Created new CurrencyRateHistory for {cur_iso}: {crh_obj}"
                )
                signals.p24curency_history_was_created.send(
                    sender=crh_obj.__class__, instance=crh_obj
                )
