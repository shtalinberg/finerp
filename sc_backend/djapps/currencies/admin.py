from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Currency, CurrencyRate

# Register your models here.


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Адміністративна панель для валюти"""

    list_display = ('iso_code', 'name', 'symbol', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('iso_code', 'name')
    ordering = ('iso_code',)
    fieldsets = (
        (_('Основна інформація'), {'fields': ('iso_code', 'name', 'symbol')}),
        (_('Статус'), {'fields': ('is_active',)}),
    )


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    """Адміністративна панель для курсу валюти"""

    list_display = ('currency', 'rate', 'created_at')
    list_filter = ('currency',)
    search_fields = ('currency__iso_code', 'currency__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fieldsets = ((_('Основна інформація'), {'fields': ('currency', 'rate', 'created_at')}),)

    def rate(self, obj):
        return obj.rate_nbu
