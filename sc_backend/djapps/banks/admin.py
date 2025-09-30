from django.contrib import admin

from .models import Bank, BankAccount


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'ifi_mfo', 'bank_type', 'city', 'swift_code', 'is_deleted')
    list_filter = ('bank_type', 'is_deleted')
    search_fields = ('name', 'ifi_mfo', 'swift_code')
    fieldsets = (
        (
            'Основна інформація',
            {'fields': ('name', 'ifi_mfo', 'bank_type', 'city', 'address')},
        ),
        (
            'SWIFT інформація',
            {
                'fields': ('swift_code', 'swift_name', 'swift_address'),
                'classes': ('collapse',),
            },
        ),
        (
            'Кореспондентська інформація',
            {
                'fields': ('corr_name', 'corr_address', 'corr_swift', 'corr_account'),
                'classes': ('collapse',),
            },
        ),
        (
            'Системна інформація',
            {
                'fields': ('is_deleted',),
                'classes': ('collapse',),
            },
        ),
    )


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        'acc_iban',
        'bank',
        'account_type',
        'currency',
        'account_status',
        'is_main',
        'is_default',
        'is_deleted',
    )
    list_filter = (
        'account_type',
        'account_status',
        'is_main',
        'is_default',
        'is_deleted',
    )
    search_fields = ('acc_iban', 'bank__name')
    fieldsets = (
        (
            'Основна інформація',
            {'fields': ('acc_iban', 'bank', 'account_type', 'currency')},
        ),
        (
            'Статус',
            {
                'fields': ('account_status', 'is_main', 'is_default'),
            },
        ),
        (
            'Системна інформація',
            {
                'fields': ('is_deleted',),
                'classes': ('collapse',),
            },
        ),
    )
