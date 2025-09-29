
from django.db import models
from django.utils.translation import gettext_lazy as _

import django_filters

from .models import IncomeRecord


class IncomeRecordFilter(django_filters.FilterSet):
    """Фільтр для записів книги доходів"""
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte', label=_('З дати'))
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte', label=_('До дати'))
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte', label=_('Мінімальна сума'))
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte', label=_('Максимальна сума'))
    search = django_filters.CharFilter(method='filter_search', label=_('Пошук'))

    class Meta:
        model = IncomeRecord
        fields = ['date_from', 'date_to', 'income_type', 'status', 'amount_min', 'amount_max', 'search']

    def filter_search(self, queryset, name, value):
        """Пошук по різних полях"""
        return queryset.filter(
            models.Q(document_number__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(notes__icontains=value)
        )