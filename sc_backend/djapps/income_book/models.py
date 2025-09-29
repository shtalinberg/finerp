
import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from finops.models import Finop
from taxpayers.models import Taxpayer

from .constants import (
    INCOME_TYPE_SERVICES,
    INCOME_TYPES,
    RECORD_STATUS_ACTIVE,
    RECORD_STATUS_ADJUSTED,
    RECORD_STATUS_CANCELLED,
    RECORD_STATUSES,
)


class IncomeRecord(models.Model):
    """Модель для записів книги доходів"""
    # Додаткове поле UUID для публічної ідентифікації
    uid = models.UUIDField(
        verbose_name=_("UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    taxpayer = models.ForeignKey(
        Taxpayer,
        on_delete=models.CASCADE,
        related_name='income_records',
        verbose_name=_("Платник податків")
    )
    date = models.DateField(_("Дата"))
    document_number = models.CharField(_("Номер документа"), max_length=50)
    amount = models.DecimalField(_("Сума"), max_digits=18, decimal_places=2)

    # Тип доходу
    income_type = models.CharField(
        _("Тип доходу"),
        max_length=20,
        choices=INCOME_TYPES,
        default=INCOME_TYPE_SERVICES
    )

    # Опціональний зв'язок з фінансовою операцією
    finop = models.ForeignKey(
        Finop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='income_records',
        verbose_name=_("Фінансова операція")
    )

    # Статус запису
    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=RECORD_STATUSES,
        default=RECORD_STATUS_ACTIVE
    )

    description = models.TextField(_("Опис"))
    notes = models.TextField(_("Примітки"), blank=True, null=True)

    # Метадані
    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    # Для обробки коригувань
    original_record = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adjustments',
        verbose_name=_("Оригінальний запис")
    )

    class Meta:
        verbose_name = _("Запис книги доходів")
        verbose_name_plural = _("Записи книги доходів")
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['taxpayer', 'date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.date} - {self.amount} - {self.description[:50]}"

    def get_absolute_url(self):
        return reverse('income_record_detail', kwargs={'pk': self.pk})

    def cancel(self):
        """Скасувати запис"""
        self.status = RECORD_STATUS_CANCELLED
        self.save()

    def create_adjustment(self, new_amount, new_description=None):
        """Створити коригувальний запис"""
        # Помічаємо поточний запис як скоригований
        self.status = RECORD_STATUS_ADJUSTED
        self.save()

        # Створюємо новий запис з посиланням на оригінал
        adjustment = IncomeRecord.objects.create(
            taxpayer=self.taxpayer,
            date=self.date,
            document_number=f"{self.document_number}-К",  # К - коригування
            amount=new_amount,
            income_type=self.income_type,
            finop=self.finop,
            description=new_description or self.description,
            notes=f"Коригування запису №{self.id} від {self.date}",
            original_record=self
        )

        return adjustment