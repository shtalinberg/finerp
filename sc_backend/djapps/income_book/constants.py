
from django.utils.translation import gettext_lazy as _

# Типи доходу
INCOME_TYPE_GOODS = 'goods'
INCOME_TYPE_SERVICES = 'services'
INCOME_TYPE_ROYALTY = 'royalty'
INCOME_TYPE_INTEREST = 'interest'
INCOME_TYPE_OTHER = 'other'

INCOME_TYPES = (
    (INCOME_TYPE_GOODS, _('Товари')),
    (INCOME_TYPE_SERVICES, _('Послуги')),
    (INCOME_TYPE_ROYALTY, _('Роялті')),
    (INCOME_TYPE_INTEREST, _('Відсотки')),
    (INCOME_TYPE_OTHER, _('Інше')),
)

# Статуси проведених записів
RECORD_STATUS_ACTIVE = 'active'
RECORD_STATUS_CANCELLED = 'cancelled'
RECORD_STATUS_ADJUSTED = 'adjusted'

RECORD_STATUSES = (
    (RECORD_STATUS_ACTIVE, _('Активний')),
    (RECORD_STATUS_CANCELLED, _('Скасований')),
    (RECORD_STATUS_ADJUSTED, _('Скоригований')),
)