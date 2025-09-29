
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

import django_filters

from .constants import OPERATION_TYPES, PROCESSING_STATUSES
from .models import Category, Finop


class FinopFilter(django_filters.FilterSet):
    """Фільтр для фінансових операцій"""
    date_from = django_filters.DateFilter(field_name='operation_date', lookup_expr='gte', label=_('З дати'))
    date_to = django_filters.DateFilter(field_name='operation_date', lookup_expr='lte', label=_('До дати'))

    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte', label=_('Мінімальна сума'))
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte', label=_('Максимальна сума'))

    bank_account = django_filters.ModelChoiceFilter(
        field_name='bank_account',
        label=_('Банківський рахунок')
    )

    operation_type = django_filters.ChoiceFilter(
        field_name='operation_type',
        choices=OPERATION_TYPES,
        label=_('Тип операції')
    )

    processing_status = django_filters.ChoiceFilter(
        field_name='processing_status',
        choices=PROCESSING_STATUSES,
        label=_('Статус обробки')
    )

    search = django_filters.CharFilter(method='filter_search', label=_('Пошук'))

    category = django_filters.CharFilter(method='filter_category', label=_('Категорія'))

    tags = django_filters.CharFilter(method='filter_tags', label=_('Теги'))

    class Meta:
        model = Finop
        fields = [
            'date_from', 'date_to', 'operation_type', 'processing_status',
            'bank_account', 'amount_min', 'amount_max', 'search', 'category',
            'tags'
        ]

    def __init__(self, *args, **kwargs):
        # Витягуємо платника податків з kwargs
        self.taxpayer = kwargs.pop('taxpayer', None)

        super().__init__(*args, **kwargs)

    def filter_search(self, queryset, name, value):
        """Пошук за різними полями"""
        return queryset.filter(
            Q(description__icontains=value) |
            Q(sender_name__icontains=value) |
            Q(recipient_name__icontains=value) |
            Q(notes__icontains=value)
        )

    def filter_category(self, queryset, name, value):
        """Фільтр за категорією"""
        if not value:
            return queryset

        # Перевіряємо тип категорії
        if value.startswith('income_'):
            # Стандартна категорія доходу
            category_code = value.replace('income_', '', 1)
            return queryset.filter(income_category=category_code)

        elif value.startswith('expense_'):
            # Стандартна категорія витрат
            category_code = value.replace('expense_', '', 1)
            return queryset.filter(expense_category=category_code)

        elif value.startswith('custom_income_'):
            # Користувацька категорія доходу
            category_id = value.replace('custom_income_', '', 1)
            try:
                category = Category.objects.get(id=category_id)
                # Тут потрібно реалізувати логіку, як саме ви зв'язуєте користувацькі категорії
                # з фінансовими операціями
                return queryset
            except Category.DoesNotExist:
                return queryset.none()

        elif value.startswith('custom_expense_'):
            # Користувацька категорія витрат
            category_id = value.replace('custom_expense_', '', 1)
            try:
                category = Category.objects.get(id=category_id)
                # Тут потрібно реалізувати логіку, як саме ви зв'язуєте користувацькі категорії
                # з фінансовими операціями
                return queryset
            except Category.DoesNotExist:
                return queryset.none()

        return queryset

    def filter_tags(self, queryset, name, value):
        """Фільтр за тегами"""
        if not value:
            return queryset

        # Розділяємо теги комами
        tags = [tag.strip() for tag in value.split(',')]
        q_objects = Q()

        for tag in tags:
            q_objects |= Q(tags__icontains=tag)

        return queryset.filter(q_objects)