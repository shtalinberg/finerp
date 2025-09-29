import uuid

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from currencies.models import Currency

from .constants import (  # STATEMENT_DOC_TYPES,
    ACCOUNT_STATUS_ACTIVE,
    ACCOUNT_STATUSES,
    ACCOUNT_TYPE_CURRENT,
    ACCOUNT_TYPES,
    BANK_TYPE_COMMERCIAL,
    BANK_TYPES,
)

# from banks.managers import BankAccountManager, BankManager

class Bank(models.Model):
    uid = models.UUIDField(
        verbose_name=_("UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique Identifier UUID"),
    )
    name = models.CharField(_("bank name"), max_length=100)
    ifi_mfo = models.CharField(
        _("bank code"),
        max_length=10,
        validators=[MinLengthValidator(6)],
        null=True,
        blank=True,
        help_text=_("bank code (IFI MFO)"),
    )
    bank_type = models.CharField(
        _("Тип банку"), max_length=20, choices=BANK_TYPES, default=BANK_TYPE_COMMERCIAL
    )
    city = models.CharField(_("bank city"), max_length=50, null=True, blank=True)
    address = models.CharField(_("bank address"), max_length=250, null=True, blank=True)

    swift_code = models.CharField(
        _("swift code bank"), max_length=20, null=True, blank=True
    )
    swift_name = models.CharField(
        _("bank name in english"), max_length=50, null=True, blank=True
    )
    swift_address = models.CharField(
        _("bank address in english"), max_length=250, null=True, blank=True
    )

    corr_name = models.CharField(
        _("correspondent bank name"), max_length=50, null=True, blank=True
    )
    corr_address = models.CharField(
        _("correspondent bank address"), max_length=250, null=True, blank=True
    )
    corr_swift = models.CharField(
        _("correspondent swift code"), max_length=20, null=True, blank=True
    )
    corr_account = models.CharField(
        _("correspondent account code"), max_length=50, null=True, blank=True
    )

    is_deleted = models.BooleanField(_("Deleted"), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, editable=False)

    # objects = BankManager()

    class Meta:
        verbose_name = _("Bank")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class BankAccount(models.Model):
    uid = models.UUIDField(
        verbose_name=_("UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique Identifier UUID"),
    )
    acc_iban = models.CharField(_("account IBAN"), max_length=29)
    bank = models.ForeignKey(
        Bank,
        verbose_name=_("bank"),
        related_name='bank_accounts',
        on_delete=models.CASCADE,
    )
    curency_iso = models.CharField(
        verbose_name=_('curency ISO'),
        help_text=_("Currency Code (ISO 4217)"),
        max_length=5,
        unique=True,
    )
    account_type = models.CharField(
        _("Тип рахунку"),
        max_length=20,
        choices=ACCOUNT_TYPES,
        default=ACCOUNT_TYPE_CURRENT,
    )
    currency = models.ForeignKey(
        Currency,
        verbose_name=_('Валюта'),
        on_delete=models.PROTECT,
        related_name='bank_accounts',
    )
    account_status = models.CharField(
        _("Статус рахунку"),
        max_length=20,
        choices=ACCOUNT_STATUSES,
        default=ACCOUNT_STATUS_ACTIVE,
    )
    is_main = models.BooleanField(_('Main'), default=False)
    is_default = models.BooleanField(_("default"), default=False)
    is_deleted = models.BooleanField(_('Deleted'), default=False)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, editable=False)

    # objects = BankAccountManager()

    class Meta:
        verbose_name = _("Bank Account")
        ordering = ['-created_at']

    def __str__(self):
        return self.str_display

    @property
    def str_display(self):
        return f"{self.acc_iban} {self.currency_type} {self.bank.name}".strip()


# class Statement(models.Model):
#     """
#     BankAccount Statement
#     """
#     uid = models.UUIDField(
#         verbose_name=_("UUID"),
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         help_text=_("Unique Identifier UUID"),
#     )

#     doctype = models.CharField(
#         verbose_name=_('type of document'),
#         max_length=20,
#         blank=True,
#         null=True,
#         choices=STATEMENT_DOC_TYPES,
#         help_text=_("document type"),
#     )

#     purpose = models.TextField(
#         verbose_name=_('purpose'),
#         blank=True,
#         null=True,
#         help_text=_("purpose of payment"),
#     )
