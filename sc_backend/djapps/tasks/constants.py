
from django.utils.translation import gettext_lazy as _

# Статуси задач
TASK_STATUS_PENDING = 'pending'
TASK_STATUS_IN_PROGRESS = 'in_progress'
TASK_STATUS_COMPLETED = 'completed'
TASK_STATUS_FAILED = 'failed'

TASK_STATUSES = (
    (TASK_STATUS_PENDING, _('Очікує')),
    (TASK_STATUS_IN_PROGRESS, _('В процесі')),
    (TASK_STATUS_COMPLETED, _('Завершено')),
    (TASK_STATUS_FAILED, _('Помилка')),
)

# Пріоритети задач
TASK_PRIORITY_LOW = 'low'
TASK_PRIORITY_NORMAL = 'normal'
TASK_PRIORITY_HIGH = 'high'

TASK_PRIORITIES = (
    (TASK_PRIORITY_LOW, _('Низький')),
    (TASK_PRIORITY_NORMAL, _('Звичайний')),
    (TASK_PRIORITY_HIGH, _('Високий')),
)