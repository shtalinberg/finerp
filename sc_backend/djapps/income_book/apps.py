from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IncomeBookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'income_book'
    verbose_name = _('Книга доходів')

    def ready(self):
        """Підключення сигналів при завантаженні додатку"""
        import income_book.signals  # noqa pylint: disable=unused-import