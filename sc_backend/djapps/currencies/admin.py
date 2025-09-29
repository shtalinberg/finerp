from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Currency, CurrencyRate

# Register your models here.


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Адміністративна панель для валюти"""

    list_display = ('code', 'name', 'symbol', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    ordering = ('code',)
    fieldsets = (
        (_('Основна інформація'), {'fields': ('code', 'name', 'symbol')}),
        (_('Статус'), {'fields': ('is_active',)}),
    )


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    """Адміністративна панель для курсу валюти"""

    list_display = ('currency', 'rate', 'date')
    list_filter = ('currency',)
    search_fields = ('currency__code', 'currency__name')
    ordering = ('-date',)
    date_hierarchy = 'date'
    fieldsets = ((_('Основна інформація'), {'fields': ('currency', 'rate', 'date')}),)

    def rate(self, obj):
        return obj.rate_nbu
