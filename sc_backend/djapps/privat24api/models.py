import datetime
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from privat24api.constants import (
    STATEMENT_DOC_TYPES,
    STATEMENT_STATES,
    STATEMENT_TYPES,
    TRANTYPE_CREDIT,
    TRANTYPE_DEBIT,
)


class P24ApiSessionManager(models.Manager):
    def get_last_session(self, date=None):
        """simple method for get cource for 1 USD"""
        if date is None:
            now = timezone.now()
        else:
            now = date
        qs = self.get_queryset().filter(created_at__lte=now)
        return qs.order_by('-created_at').first()


class P24ApiSession(models.Model):
    token = models.CharField(_('Token'), max_length=40, db_index=True)

    roles = models.TextField(_('roles'))

    expires_in = models.CharField(_('expires_in str'), max_length=20)
    expires_at = models.DateTimeField(_('expires at'), db_index=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = P24ApiSessionManager()

    _ROLES_SEPARATOR = "|"

    class Meta:
        verbose_name = _('P24 Api Session')
        verbose_name_plural = _('P24 Api Sessions')

    def __str__(self):
        return str(self.token)

    def set_expires_in_value(self, expires_in):
        self.expires_in = expires_in
        self.expires_at = datetime.datetime.fromtimestamp(expires_in)

    def get_roles_list(self):
        return self.roles.split(self._ROLES_SEPARATOR)

    def set_roles_value(self, roles_list):
        self.roles = self._ROLES_SEPARATOR.join(roles_list)


class Statement(models.Model):
    """
    Account Statement from bank API

    Represents a financial transaction with details about sender,
    recipient, amount, and transaction metadata.
    """
    btid = models.CharField(verbose_name=_('bank id'), max_length=20, db_index=True, help_text=_("bank transaction id"), blank=True, null=True)
    info_number = models.CharField(
        verbose_name=_('number'),
        max_length=40,
        db_index=True,
        help_text=_("payment number"),
    )
    info_postdate = models.DateTimeField(
        verbose_name=_('postdate'), null=True, help_text=_("date and time of posting")
    )
    info_customerdate = models.DateTimeField(
        verbose_name=_('customerdate'), null=True, help_text=_("client date and time")
    )
    info_ref = models.CharField(
        verbose_name=_('ref'),
        max_length=40,
        db_index=True,
        help_text=_("banking reference"),
    )
    info_state = models.CharField(
        verbose_name=_('state of statement'),
        max_length=20,
        blank=True,
        null=True,
        choices=STATEMENT_STATES,
        help_text=_("document state"),
    )
    info_flinfo = models.CharField(
        verbose_name=_('type of statement'),
        max_length=20,
        blank=True,
        null=True,
        choices=STATEMENT_TYPES,
        help_text=_("statement type"),
    )

    info_doctype = models.CharField(
        verbose_name=_('type of document'),
        max_length=20,
        blank=True,
        null=True,
        choices=STATEMENT_DOC_TYPES,
        help_text=_("document type"),
    )
    trantype = models.CharField(
        verbose_name=_('trantype'),
        max_length=1,
        default=TRANTYPE_CREDIT,
        help_text=_("transaction type debit or credit: D or C"),
    )
    curency_iso = models.CharField(
        verbose_name=_('currency iso'),
        max_length=3,
        default='UAH',
        help_text=_("currency code"),
    )
    currency_exchange_at = models.DateField(verbose_name=_('currency exchanged'), null=True)
    amount_amt = models.DecimalField(
        verbose_name=_('amount'),
        max_digits=17,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("amount of payment"),
    )
    amount_amt_uah = models.DecimalField(
        verbose_name=_('amount UAH'),
        max_digits=17,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("amount of payment in native currency"),
    )
    amount_ccy = models.CharField(
        verbose_name=_('ccy'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_("payment currency"),
    )

    daccount_name = models.CharField(
        verbose_name=_('name of the customer'), max_length=255, blank=True, null=True
    )
    daccount_number = models.CharField(
        verbose_name=_('customer acc number'), max_length=30, blank=True, null=True
    )

    daccount_customer_crf = models.CharField(
        verbose_name=_('customer crf'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_("TIN / EDRPOU code of the customer"),
    )
    daccount_customer_bank_code = models.CharField(
        verbose_name=_('customer bank code'), max_length=20, blank=True, null=True
    )
    daccount_customer_bank_name = models.CharField(
        verbose_name=_('customer bank name'), max_length=255, blank=True, null=True
    )

    caccount_name = models.CharField(
        verbose_name=_('receiver name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("recipient's name"),
    )
    caccount_number = models.CharField(
        verbose_name=_('receiver acc number'),
        max_length=30,
        blank=True,
        null=True,
        help_text=_("beneficiary's account"),
    )
    caccount_customer_crf = models.CharField(
        verbose_name=_('receiver crf'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_("TIN / EDRPOU code of the recipient"),
    )
    caccount_customer_bank_code = models.CharField(
        verbose_name=_('receiver bank code'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_("MFI of the beneficiary's bank"),
    )
    caccount_customer_bank_name = models.CharField(
        verbose_name=_('recipient bank name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("the name of the recipient's bank"),
    )

    purpose = models.TextField(
        verbose_name=_('purpose'),
        blank=True,
        null=True,
        help_text=_("purpose of payment"),
    )

    is_find_invoice = models.BooleanField(
        verbose_name=_('find invoice'),
        default=False,
        help_text=_("invoice number in purpose is founded"),
    )

    class Meta:
        verbose_name = _('Statement')
        verbose_name_plural = _('Statements')

    def __str__(self):
        return self.purpose

    @property
    def is_credit(self):
        """Check if transaction is credit"""
        return self.trantype == TRANTYPE_CREDIT

    @property
    def is_debit(self):
        """Check if transaction is debit"""
        return self.trantype == TRANTYPE_DEBIT

class CurrencyRateHistory(models.Model):
    """
    B – купівля;
    S – продаж;
    date – дата курсу;
    rate – курс;
    rate_delta – зміна курсу;
    nbuRate – курс НБУ.
    """

    iso_code = models.CharField(
        verbose_name=_('iso code'),
        help_text=_("Currency Code (ISO 4217)"),
        max_length=3,
    )
    rate_datetime = models.DateTimeField(
        verbose_name=_("rate datetime"), help_text=_("Datetime of the rate")
    )
    rate_type = models.CharField(
        verbose_name=_('Curency rate'),
        help_text=_("Bank Rate type: B - buy, S - sell"),
        max_length=1,
    )
    rate = models.DecimalField(
        verbose_name=_('Curency rate'),
        help_text=_("Bank Rate"),
        max_digits=15,
        decimal_places=7,
    )
    rate_delta = models.DecimalField(
        verbose_name=_('rate delta'),
        help_text=_("Bank Rate"),
        max_digits=15,
        decimal_places=7,
    )
    rate_nbu = models.DecimalField(
        verbose_name=_('rate NBU'),
        help_text=_("Technical National Bank Rate"),
        max_digits=15,
        decimal_places=7,
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Currency Rate")
        verbose_name_plural = _("Currency Rates")

    def __str__(self):
        return self.iso_code
