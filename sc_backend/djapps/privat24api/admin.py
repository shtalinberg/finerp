from django.contrib import admin

# Register your models here.
from .models import CurrencyRateHistory, P24ApiSession, Statement


@admin.register(P24ApiSession)
class P24ApiSessionAdmin(admin.ModelAdmin):
    pass


@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'info_number',
        # 'info_ref',
        'info_state',
        'info_postdate',
        'trantype',
        'amount_amt',
        'curency_iso',
        'amount_amt_uah',
        'currency_exchange_at',
        'purpose',
        'daccount_name',
        'daccount_number',
        'is_find_invoice',
    )
    list_display_links = (
        'id',
        'info_number',
    )
    list_filter = (
        'trantype',
        'is_find_invoice',
        'info_state',
        'info_flinfo',
        'info_doctype',
        'daccount_number',
    )
    list_select_related = False
    list_per_page = 100
    list_max_show_all = 200
    ordering = ('-info_postdate',)
    search_fields = (
        'daccount_name',
        'purpose',
    )
    date_hierarchy = 'info_postdate'


#                 info_number=line['info']['@number'],
#                 info_postdate=postdate,
#                 info_customerdate=customerdate,
#                 info_ref=line['info']['@ref'],
#                 info_state=line['info']['@state'],
#                 info_flinfo=line['info']['@flinfo'],
#                 info_doctype=line['info']['@doctype'],
#                 amount_amt=D(line['amount']['@amt']),
#
#                 daccount_name=line['debet']['account']['@name'],
#                 daccount_number=line['debet']['account']['@number'],
#                 daccount_customer_crf=line['debet']['account']['customer']['@crf'],
#                 daccount_customer_bank_code=line['debet']['account']['customer']['bank']['@code'],
#                 daccount_customer_bank_name=line['debet']['account']['customer']['bank']['#text'],
#
#                 caccount_name=line['credit']['account']['@name'],
#                 caccount_number=line['credit']['account']['@number'],
#                 caccount_customer_crf=line['credit']['account']['customer']['@crf'],
#                 caccount_customer_bank_code=line['credit']['account']['customer']['bank']['@code'],
#                 caccount_customer_bank_name=line['credit']['account']['customer']['bank']['#text'],
#
#                 purpose=line['purpose'],

@admin.register(CurrencyRateHistory)
class CurrencyRateHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'iso_code',
        'rate_datetime',
        'rate_nbu',
        'rate_type',
        'rate',
        'rate_delta',
        'created_at',
    )
    list_display_links = (
        'id',
        'iso_code',
    )
    list_filter = (
        'rate_type',
        'iso_code',
        'created_at',
    )
    date_hierarchy = 'rate_datetime'
    list_per_page = 50
    list_max_show_all = 200
    ordering = ('-rate_datetime',)

