
import uuid
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from taxpayers.models import Taxpayer


class TaxPeriod(models.Model):
    """Model for tax reporting periods (quarters)"""
    uid = models.UUIDField(
        verbose_name=_("UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique Identifier UUID")
    )
    year = models.IntegerField(_("Year"))

    QUARTER_CHOICES = (
        (1, _("1st Quarter")),
        (2, _("2nd Quarter")),
        (3, _("3rd Quarter")),
        (4, _("4th Quarter")),
    )
    quarter = models.IntegerField(_("Quarter"), choices=QUARTER_CHOICES)

    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))

    class Meta:
        verbose_name = _("Tax Period")
        verbose_name_plural = _("Tax Periods")
        unique_together = ('year', 'quarter')
        ordering = ['-year', '-quarter']

    def __str__(self):
        return f"{self.year} - Q{self.quarter}"

class TaxReport(models.Model):
    """Model for tax reports"""
    uid = models.UUIDField(
        verbose_name=_("UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique Identifier UUID")
    )
    taxpayer = models.ForeignKey(
        Taxpayer,
        on_delete=models.CASCADE,
        related_name='tax_reports',
        verbose_name=_("Taxpayer")
    )
    period = models.ForeignKey(
        TaxPeriod,
        on_delete=models.CASCADE,
        related_name='tax_reports',
        verbose_name=_("Tax Period")
    )

    # Income and tax amounts
    total_income = models.DecimalField(_("Total income"), max_digits=18, decimal_places=2, default=Decimal('0.00'))
    single_tax_amount = models.DecimalField(_("Single tax amount (5%)"), max_digits=18, decimal_places=2, default=Decimal('0.00'))
    military_tax_amount = models.DecimalField(_("Military tax amount (1.5%)"), max_digits=18, decimal_places=2, default=Decimal('0.00'))
    esv_amount = models.DecimalField(_("ESV amount"), max_digits=18, decimal_places=2, default=Decimal('0.00'))

    # Status
    STATUS_CHOICES = (
        ('draft', _("Draft")),
        ('calculated', _("Calculated")),
        ('submitted', _("Submitted")),
        ('paid', _("Paid")),
    )
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')

    # Payment info
    single_tax_paid = models.BooleanField(_("Single tax paid"), default=False)
    military_tax_paid = models.BooleanField(_("Military tax paid"), default=False)
    esv_paid = models.BooleanField(_("ESV paid"), default=False)

    # Submission info
    submission_date = models.DateField(_("Submission date"), null=True, blank=True)
    submission_number = models.CharField(_("Submission number"), max_length=50, null=True, blank=True)

    # Metadata
    notes = models.TextField(_("Notes"), blank=True, null=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Tax Report")
        verbose_name_plural = _("Tax Reports")
        unique_together = ('taxpayer', 'period')
        ordering = ['-period__year', '-period__quarter']

    def __str__(self):
        return f"{self.taxpayer} - {self.period}"

    def calculate_taxes(self):
        """Calculate taxes based on total income"""
        self.single_tax_amount = self.total_income * Decimal('0.05')  # 5% Single tax
        self.military_tax_amount = self.total_income * Decimal('0.01')  # 1% Military tax
        # ESV is a fixed amount per period, would be set elsewhere
        self.status = 'calculated'
        self.save()