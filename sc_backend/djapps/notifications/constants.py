
from django.utils.translation import gettext_lazy as _

# Теми сповіщень
NOTIFICATION_THEME_INFO = 'info'
NOTIFICATION_THEME_SUCCESS = 'success'
NOTIFICATION_THEME_WARNING = 'warning'
NOTIFICATION_THEME_ERROR = 'error'

NOTIFICATION_THEMES = (
    (NOTIFICATION_THEME_INFO, _('Інформація')),
    (NOTIFICATION_THEME_SUCCESS, _('Успіх')),
    (NOTIFICATION_THEME_WARNING, _('Попередження')),
    (NOTIFICATION_THEME_ERROR, _('Помилка')),
)

# Типи сповіщень
NOTIFICATION_TYPE_SYSTEM = 'system'
NOTIFICATION_TYPE_TAX = 'tax'
NOTIFICATION_TYPE_INCOME = 'income'
NOTIFICATION_TYPE_FINANCE = 'finance'

NOTIFICATION_TYPES = (
    (NOTIFICATION_TYPE_SYSTEM, _('Системне')),
    (NOTIFICATION_TYPE_TAX, _('Податкове')),
    (NOTIFICATION_TYPE_INCOME, _('Дохід')),
    (NOTIFICATION_TYPE_FINANCE, _('Фінансове')),
)