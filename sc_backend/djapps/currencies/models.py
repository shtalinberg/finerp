from django.db import models

# Create your models here.
from django.utils.translation import gettext_lazy as _


class Currency(models.Model):
    iso_code = models.CharField(
        verbose_name=_('iso code'),
        help_text=_("Currency Code (ISO 4217)"),
        max_length=5,
        unique=True,
    )
    iso_numeric = models.IntegerField(
        verbose_name=_("iso numeric"), help_text=_("Currency Numeric Code (ISO 4217).")
    )
    name = models.CharField(verbose_name=_('Name'), max_length=30)
    symbol = models.CharField(
        verbose_name=_('Symbol'),
        help_text=_("Currency sign, to be used for printing amounts"),
        max_length=5,
    )
    position = models.CharField(
        verbose_name=_('Symbol Position'), max_length=10, default='after')
    is_active = models.BooleanField(verbose_name=_('Active'), default=True)
    unit_label = models.CharField(verbose_name=_('Currency Unit'), max_length=30)
    subunit_label = models.CharField(verbose_name=_('Currency Subunit'), max_length=30)
    # is_current_company_currency = models.BooleanField(verbose_name=_('Is current company currency'), default=False)

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self):
        return self.iso_code


class CurrencyRate(models.Model):
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="rates",
        verbose_name=_("currency"),
    )
    rate_date = models.DateField(
        verbose_name=_("rate date"), help_text=_("Date of the rate")
    )
    rate_nbu = models.DecimalField(
        verbose_name=_('rate NBU'),
        help_text=_("Technical National Bank Rate"),
        max_digits=14,
        decimal_places=7,
    )
    created_at = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Currency Rate")
        verbose_name_plural = _("Currency Rates")

    def __str__(self):
        return self.currency.iso_code
