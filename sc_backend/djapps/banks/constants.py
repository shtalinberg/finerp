
from django.utils.translation import gettext_lazy as _

# Типи банківських установ
BANK_TYPE_COMMERCIAL = 'commercial'
BANK_TYPE_STATE = 'state'
BANK_TYPE_FOREIGN = 'foreign'
BANK_TYPE_INTERNATIONAL = 'international'

BANK_TYPES = (
    (BANK_TYPE_COMMERCIAL, _('Комерційний')),
    (BANK_TYPE_STATE, _('Державний')),
    (BANK_TYPE_FOREIGN, _('Іноземний')),
    (BANK_TYPE_INTERNATIONAL, _('Міжнародний')),
)

# Статуси банківського рахунку
ACCOUNT_STATUS_ACTIVE = 'active'
ACCOUNT_STATUS_INACTIVE = 'inactive'
ACCOUNT_STATUS_BLOCKED = 'blocked'
ACCOUNT_STATUS_CLOSED = 'closed'

ACCOUNT_STATUSES = (
    (ACCOUNT_STATUS_ACTIVE, _('Активний')),
    (ACCOUNT_STATUS_INACTIVE, _('Неактивний')),
    (ACCOUNT_STATUS_BLOCKED, _('Заблокований')),
    (ACCOUNT_STATUS_CLOSED, _('Закритий')),
)

# Типи банківських рахунків
ACCOUNT_TYPE_CURRENT = 'current'
ACCOUNT_TYPE_CARD = 'card'
ACCOUNT_TYPE_DEPOSIT = 'deposit'
ACCOUNT_TYPE_CREDIT = 'credit'
ACCOUNT_TYPE_SAVINGS = 'savings'

ACCOUNT_TYPES = (
    (ACCOUNT_TYPE_CURRENT, _('Поточний')),
    (ACCOUNT_TYPE_CARD, _('Картковий')),
    (ACCOUNT_TYPE_DEPOSIT, _('Депозитний')),
    (ACCOUNT_TYPE_CREDIT, _('Кредитний')),
    (ACCOUNT_TYPE_SAVINGS, _('Ощадний')),
)


# STATEMENT_TYPE_REAL = 'r'  # - реальний,
# STATEMENT_TYPE_INFO = 'i'  # - інформаційний

# STATEMENT_TYPES = ((STATEMENT_TYPE_REAL, 'real'), (STATEMENT_TYPE_INFO, 'information'))

# STATEMENT_STATE_R = 'r'  # проведено
# STATEMENT_STATE_T = 't'  # сторнований

# STATEMENT_STATES = (
#     (STATEMENT_STATE_R, 'проведено'),  # - проведено,
#     (STATEMENT_STATE_T, 'сторнований'),  # - сторнований
# )

# STATEMENT_DOC_TYPE_P = 'p'  # доручення
# STATEMENT_DOC_TYPE_T = 't'  # вимога
# STATEMENT_DOC_TYPE_M = 'm'  # меморіальний ордер
# STATEMENT_DOC_TYPE_X = 'x'  # сторнований
# STATEMENT_DOC_TYPE_R = 'r'  # сторнований

# STATEMENT_DOC_TYPES = (
#     (STATEMENT_DOC_TYPE_P, 'доручення'),
#     (STATEMENT_DOC_TYPE_T, 'вимога'),
#     (STATEMENT_DOC_TYPE_M, 'меморіальний ордер'),
#     (STATEMENT_DOC_TYPE_X, 'прибутковий ордер'),
#     (STATEMENT_DOC_TYPE_R, 'видатковий ордер'),
# )