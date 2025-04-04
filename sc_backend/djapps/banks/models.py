import uuid

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# from banks.managers import BankAccountManager, BankManager

STATEMENT_TYPE_REAL = 'r'  # - реальний,
STATEMENT_TYPE_INFO = 'i'  # - інформаційний

STATEMENT_TYPES = ((STATEMENT_TYPE_REAL, 'real'), (STATEMENT_TYPE_INFO, 'information'))

STATEMENT_STATE_R = 'r'  # проведено
STATEMENT_STATE_T = 't'  # сторнований

STATEMENT_STATES = (
    (STATEMENT_STATE_R, 'проведено'),  # - проведено,
    (STATEMENT_STATE_T, 'сторнований'),  # - сторнований
)

STATEMENT_DOC_TYPE_P = 'p'  # доручення
STATEMENT_DOC_TYPE_T = 't'  # вимога
STATEMENT_DOC_TYPE_M = 'm'  # меморіальний ордер
STATEMENT_DOC_TYPE_X = 'x'  # сторнований
STATEMENT_DOC_TYPE_R = 'r'  # сторнований

STATEMENT_DOC_TYPES = (
    (STATEMENT_DOC_TYPE_P, 'доручення'),
    (STATEMENT_DOC_TYPE_T, 'вимога'),
    (STATEMENT_DOC_TYPE_M, 'меморіальний ордер'),
    (STATEMENT_DOC_TYPE_X, 'прибутковий ордер'),
    (STATEMENT_DOC_TYPE_R, 'видатковий ордер'),
)



class Bank(models.Model):
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name='ID',
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(_("bank name"), max_length=100)
    ifi_mfo = models.CharField(
        _("bank code"),
        max_length=10,
        validators=[MinLengthValidator(6)],
        null=True,
        blank=True,
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
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name='ID',
        default=uuid.uuid4,
        editable=False,
    )
    acc_iban = models.CharField(_("account IBAN"), max_length=29)
    bank = models.ForeignKey(
        "banks.Bank",
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


class Statement(models.Model):
    """
    BankAccount Statement
    """

    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name='ID',
        default=uuid.uuid4,
        editable=False,
    )

    doctype = models.CharField(
        verbose_name=_('type of document'),
        max_length=20,
        blank=True,
        null=True,
        choices=STATEMENT_DOC_TYPES,
        help_text=_("document type"),
    )

    purpose = models.TextField(
        verbose_name=_('purpose'),
        blank=True,
        null=True,
        help_text=_("purpose of payment"),
    )
