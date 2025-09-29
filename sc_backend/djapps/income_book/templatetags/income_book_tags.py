
from django import template
from django.db.models import Sum
from django.utils import timezone
from django.utils.safestring import mark_safe

from income_book.constants import INCOME_TYPES, RECORD_STATUSES
from income_book.models import IncomeRecord

register = template.Library()

@register.simple_tag
def get_income_summary(taxpayer, year=None, quarter=None):
    """
    Отримати підсумок доходів для платника податків за вказаний період

    Args:
        taxpayer: Об'єкт платника податків
        year: Рік (за замовчуванням - поточний)
        quarter: Квартал (1-4, якщо не вказано - весь рік)

    Returns:
        Загальна сума доходів за період
    """
    if not year:
        year = timezone.now().year

    queryset = IncomeRecord.objects.filter(
        taxpayer=taxpayer,
        date__year=year,
        status='active'
    )

    if quarter:
        if quarter == 1:
            queryset = queryset.filter(date__month__in=[1, 2, 3])
        elif quarter == 2:
            queryset = queryset.filter(date__month__in=[4, 5, 6])
        elif quarter == 3:
            queryset = queryset.filter(date__month__in=[7, 8, 9])
        elif quarter == 4:
            queryset = queryset.filter(date__month__in=[10, 11, 12])

    return queryset.aggregate(total=Sum('amount'))['total'] or 0

@register.filter
def income_type_color(income_type):
    """
    Отримати колір CSS для типу доходу

    Args:
        income_type: Код типу доходу

    Returns:
        Клас CSS для кольору
    """
    colors = {
        'goods': 'primary',
        'services': 'success',
        'royalty': 'info',
        'interest': 'warning',
        'other': 'secondary'
    }

    return colors.get(income_type, 'secondary')

@register.filter
def status_badge(status):
    """
    Сформувати HTML-код для значка статусу

    Args:
        status: Код статусу запису

    Returns:
        HTML-код для значка
    """
    colors = {
        'active': 'success',
        'cancelled': 'danger',
        'adjusted': 'warning'
    }

    labels = dict(RECORD_STATUSES)

    color = colors.get(status, 'secondary')
    label = labels.get(status, status)

    return mark_safe(f'<span class="badge bg-{color}">{label}</span>')
