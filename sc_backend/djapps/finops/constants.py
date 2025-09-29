
from django.utils.translation import gettext_lazy as _

# Типи фінансових операцій
OPERATION_TYPE_INCOME = 'income'
OPERATION_TYPE_EXPENSE = 'expense'
OPERATION_TYPE_TRANSFER = 'transfer'
OPERATION_TYPE_OTHER = 'other'

OPERATION_TYPES = (
    (OPERATION_TYPE_INCOME, _("Дохід")),
    (OPERATION_TYPE_EXPENSE, _("Витрата")),
    (OPERATION_TYPE_TRANSFER, _("Переказ")),
    (OPERATION_TYPE_OTHER, _("Інше")),
)

# Статуси обробки операцій
PROCESSING_STATUS_NEW = 'new'
PROCESSING_STATUS_PROCESSED = 'processed'
PROCESSING_STATUS_IGNORED = 'ignored'
PROCESSING_STATUS_ERROR = 'error'

PROCESSING_STATUSES = (
    (PROCESSING_STATUS_NEW, _("Новий")),
    (PROCESSING_STATUS_PROCESSED, _("Оброблено")),
    (PROCESSING_STATUS_IGNORED, _("Ігноровано")),
    (PROCESSING_STATUS_ERROR, _("Помилка")),
)

# Джерела операцій
SOURCE_PRIVATBANK = 'privatbank'
SOURCE_MONOBANK = 'monobank'
SOURCE_MANUAL = 'manual'
SOURCE_IMPORT = 'import'

OPERATION_SOURCES = (
    (SOURCE_PRIVATBANK, _("ПриватБанк")),
    (SOURCE_MONOBANK, _("Монобанк")),
    (SOURCE_MANUAL, _("Ручне введення")),
    (SOURCE_IMPORT, _("Імпорт")),
)

# Категорії операцій
# Категорії доходів
INCOME_CATEGORY_SALES = 'sales'
INCOME_CATEGORY_SERVICES = 'services'
INCOME_CATEGORY_REFUND = 'refund'
INCOME_CATEGORY_INTEREST = 'interest'
INCOME_CATEGORY_OTHER_INCOME = 'other_income'

INCOME_CATEGORIES = (
    (INCOME_CATEGORY_SALES, _("Продаж товарів")),
    (INCOME_CATEGORY_SERVICES, _("Послуги")),
    (INCOME_CATEGORY_REFUND, _("Повернення коштів")),
    (INCOME_CATEGORY_INTEREST, _("Відсотки")),
    (INCOME_CATEGORY_OTHER_INCOME, _("Інші доходи")),
)

# Категорії витрат
EXPENSE_CATEGORY_PURCHASE = 'purchase'
EXPENSE_CATEGORY_RENT = 'rent'
EXPENSE_CATEGORY_UTILITIES = 'utilities'
EXPENSE_CATEGORY_SALARY = 'salary'
EXPENSE_CATEGORY_TAX = 'tax'
EXPENSE_CATEGORY_TRANSPORT = 'transport'
EXPENSE_CATEGORY_MARKETING = 'marketing'
EXPENSE_CATEGORY_OFFICE = 'office'
EXPENSE_CATEGORY_SERVICES = 'services_expense'
EXPENSE_CATEGORY_EQUIPMENT = 'equipment'
EXPENSE_CATEGORY_OTHER_EXPENSE = 'other_expense'

EXPENSE_CATEGORIES = (
    (EXPENSE_CATEGORY_PURCHASE, _("Закупівля товарів")),
    (EXPENSE_CATEGORY_RENT, _("Оренда")),
    (EXPENSE_CATEGORY_UTILITIES, _("Комунальні послуги")),
    (EXPENSE_CATEGORY_SALARY, _("Зарплата")),
    (EXPENSE_CATEGORY_TAX, _("Податки та збори")),
    (EXPENSE_CATEGORY_TRANSPORT, _("Транспорт")),
    (EXPENSE_CATEGORY_MARKETING, _("Маркетинг та реклама")),
    (EXPENSE_CATEGORY_OFFICE, _("Офісні витрати")),
    (EXPENSE_CATEGORY_SERVICES, _("Послуги")),
    (EXPENSE_CATEGORY_EQUIPMENT, _("Обладнання")),
    (EXPENSE_CATEGORY_OTHER_EXPENSE, _("Інші витрати")),
)

# Статуси операцій
OPERATION_STATUS_PENDING = 'pending'
OPERATION_STATUS_COMPLETED = 'completed'
OPERATION_STATUS_FAILED = 'failed'
OPERATION_STATUS_CANCELLED = 'cancelled'

OPERATION_STATUSES = (
    (OPERATION_STATUS_PENDING, _("В очікуванні")),
    (OPERATION_STATUS_COMPLETED, _("Завершено")),
    (OPERATION_STATUS_FAILED, _("Не виконано")),
    (OPERATION_STATUS_CANCELLED, _("Скасовано")),
)