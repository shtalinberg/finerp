
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import IncomeRecord


class IncomeRecordAdmin(admin.ModelAdmin):
    list_display = ('date', 'taxpayer', 'document_number', 'amount', 'income_type', 'status', 'created_at')
    list_filter = ('status', 'income_type', 'taxpayer', 'date')
    search_fields = ('document_number', 'description', 'notes')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Основна інформація'), {
            'fields': ('taxpayer', 'date', 'document_number', 'amount', 'income_type')
        }),
        (_('Деталі'), {
            'fields': ('description', 'notes', 'finop')
        }),
        (_('Статус'), {
            'fields': ('status', 'original_record')
        }),
        (_('Метадані'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['cancel_records']

    def cancel_records(self, request, queryset):
        """Дія для скасування вибраних записів"""
        updated = 0
        for record in queryset:
            if record.status == 'active':
                record.cancel()
                updated += 1

        self.message_user(request, _(f"Скасовано {updated} записів"))
    cancel_records.short_description = _("Скасувати вибрані записи")

    def get_queryset(self, request):
        """Додаємо prefetch_related для платників податків"""
        return super().get_queryset(request).select_related('taxpayer')

admin.site.register(IncomeRecord, IncomeRecordAdmin)