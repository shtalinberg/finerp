
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Category, Finop, Tag


@admin.register(Finop)
class FinopAdmin(admin.ModelAdmin):
    list_display = (
        'operation_date', 'taxpayer', 'operation_type', 'amount', 'bank_account',
        'get_category', 'processing_status', 'created_at'
    )
    list_filter = (
        'operation_type', 'processing_status', 'operation_status',
        'is_taxable', 'source', 'created_at'
    )
    search_fields = (
        'description', 'sender_name', 'recipient_name',
        'notes', 'tags', 'reference'
    )
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'operation_date'

    fieldsets = (
        (_('Основна інформація'), {
            'fields': (
                'taxpayer', 'bank_account', 'operation_date',
                'amount', 'amount_uah', 'description'
            )
        }),
        (_('Класифікація'), {
            'fields': (
                'operation_type', 'operation_status',
                'income_category', 'expense_category',
                'is_taxable', 'tags'
            )
        }),
        (_('Джерело та обробка'), {
            'fields': (
                'source', 'processing_status',
                'bank_operation_id', 'reference'
            )
        }),
        (_('Деталі переказу'), {
            'fields': (
                'sender_name', 'sender_account',
                'recipient_name', 'recipient_account',
                'notes'
            ),
            'classes': ('collapse',)
        }),
        (_('Метадані'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_category(self, obj):
        """Отримати категорію операції"""
        if obj.operation_type == 'income' and obj.income_category:
            for code, label in obj.INCOME_CATEGORIES:
                if code == obj.income_category:
                    return label
        elif obj.operation_type == 'expense' and obj.expense_category:
            for code, label in obj.EXPENSE_CATEGORIES:
                if code == obj.expense_category:
                    return label
        return "-"
    get_category.short_description = _("Категорія")

    actions = ['mark_as_processed', 'mark_as_ignored']

    def mark_as_processed(self, request, queryset):
        """Позначити вибрані операції як оброблені"""
        updated = queryset.update(processing_status='processed')
        self.message_user(request, _(f"Позначено {updated} операцій як оброблені"))
    mark_as_processed.short_description = _("Позначити як оброблені")

    def mark_as_ignored(self, request, queryset):
        """Позначити вибрані операції як проігноровані"""
        updated = queryset.update(processing_status='ignored')
        self.message_user(request, _(f"Позначено {updated} операцій як проігноровані"))
    mark_as_ignored.short_description = _("Позначити як проігноровані")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('taxpayer', 'bank_account')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'taxpayer', 'category_type', 'is_default', 'is_active', 'order')
    list_filter = ('category_type', 'is_default', 'is_active', 'taxpayer')
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_active')

    fieldsets = (
        (_('Основна інформація'), {
            'fields': ('taxpayer', 'name', 'category_type', 'description')
        }),
        (_('Налаштування'), {
            'fields': ('is_default', 'is_active', 'order', 'color', 'icon')
        }),
    )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'taxpayer', 'color', 'created_at')
    list_filter = ('taxpayer',)
    search_fields = ('name',)