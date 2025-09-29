
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Address, Taxpayer, TaxpayerDocument, TaxpayerSettings


class AddressAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'city', 'region', 'postal_code')
    search_fields = ('street', 'city', 'region', 'postal_code')
    list_filter = ('region', 'city')

class TaxpayerSettingsInline(admin.StackedInline):
    model = TaxpayerSettings
    can_delete = False
    verbose_name_plural = _('Налаштування')

class TaxpayerDocumentInline(admin.TabularInline):
    model = TaxpayerDocument
    extra = 0
    verbose_name_plural = _('Документи')

@admin.register(Taxpayer)
class TaxpayerAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'tax_number', 'tax_system', 'tax_group',
        'tax_rate', 'is_vat_payer', 'is_active', 'user'
    )
    list_filter = ('tax_system', 'tax_group', 'is_vat_payer', 'is_active')
    search_fields = ('full_name', 'tax_number', 'registration_number')
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('Основна інформація'), {
            'fields': ('user', 'full_name', 'tax_number', 'registration_number',
                      'registration_date', 'address')
        }),
        (_('Податкова інформація'), {
            'fields': ('tax_system', 'tax_group', 'tax_rate', 'esv_rate',
                      'is_vat_payer', 'vat_registration_number')
        }),
        (_('Статус'), {
            'fields': ('is_active',)
        }),
        (_('Метадані'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
    inlines = [TaxpayerSettingsInline, TaxpayerDocumentInline]

    def save_model(self, request, obj, form, change):
        # Створюємо налаштування при створенні нового платника податків
        is_new = not change
        super().save_model(request, obj, form, change)

        if is_new:
            TaxpayerSettings.objects.get_or_create(taxpayer=obj)

@admin.register(TaxpayerDocument)
class TaxpayerDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'taxpayer', 'document_type', 'issue_date', 'expiry_date', 'created_at')
    list_filter = ('document_type', 'taxpayer')
    search_fields = ('title', 'notes', 'taxpayer__full_name')
    date_hierarchy = 'created_at'

# Реєструємо моделі в адмін-панелі
admin.site.register(Address, AddressAdmin)