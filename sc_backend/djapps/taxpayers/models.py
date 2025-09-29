
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .constants import (
    ESV_RATE_22,
    ESV_RATE_CHOICES,
    TAX_GROUP_1,
    TAX_GROUP_2,
    TAX_GROUP_3,
    TAX_GROUP_CHOICES,
    TAX_RATE_1_CHOICES,
    TAX_RATE_2_CHOICES,
    TAX_RATE_3_CHOICES,
    TAX_SYSTEM_SIMPLIFIED,
    TAX_SYSTEMS,
)

User = get_user_model()


class Address(models.Model):
    """Модель для адреси"""
    # Django автоматично створює id = models.AutoField(primary_key=True)

    # Додаткове поле UUID для публічної ідентифікації
    uid = models.UUIDField(
        verbose_name=_("UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    street = models.CharField(_("Вулиця"), max_length=255)
    house_number = models.CharField(_("Номер будинку"), max_length=20)
    apartment = models.CharField(_("Квартира/офіс"), max_length=20, blank=True, null=True)
    city = models.CharField(_("Місто"), max_length=100)
    region = models.CharField(_("Область"), max_length=100)
    postal_code = models.CharField(_("Поштовий індекс"), max_length=10)

    # Метадані
    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Адреса")
        verbose_name_plural = _("Адреси")

    def __str__(self):
        apartment_str = f", кв./офіс {self.apartment}" if self.apartment else ""
        return f"{self.postal_code}, {self.region}, {self.city}, вул. {self.street}, {self.house_number}{apartment_str}"

class Taxpayer(models.Model):
    """Модель для платника податків (ФОП)"""
    # Django автоматично створює id = models.AutoField(primary_key=True)

    # Додаткове поле UUID для публічної ідентифікації
    uid = models.UUIDField(
        verbose_name=_("UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='taxpayers',
        verbose_name=_("Користувач")
    )
    full_name = models.CharField(_("Повне ім'я"), max_length=255)
    tax_number = models.CharField(_("Податковий номер (ІПН)"), max_length=10, unique=True)
    registration_number = models.CharField(_("Реєстраційний номер"), max_length=20, blank=True, null=True)
    registration_date = models.DateField(_("Дата реєстрації"))

    # Адреса юридична
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='taxpayers',
        verbose_name=_("Юридична адреса")
    )

    # Система оподаткування
    tax_system = models.CharField(
        _("Система оподаткування"),
        max_length=20,
        choices=TAX_SYSTEMS,
        default=TAX_SYSTEM_SIMPLIFIED
    )

    # Група платника єдиного податку
    tax_group = models.IntegerField(
        _("Група платника єдиного податку"),
        choices=TAX_GROUP_CHOICES,
        default=TAX_GROUP_3,
        blank=True,
        null=True
    )

    # Ставка податку
    tax_rate = models.FloatField(
        _("Ставка податку"),
        default=5.0,
        help_text=_("Ставка податку у відсотках")
    )

    # Ставка ЄСВ
    esv_rate = models.FloatField(
        _("Ставка ЄСВ"),
        choices=ESV_RATE_CHOICES,
        default=ESV_RATE_22,
        help_text=_("Ставка ЄСВ у відсотках")
    )

    # ПДВ платник статус
    is_vat_payer = models.BooleanField(_("Платник ПДВ"), default=False)
    vat_registration_number = models.CharField(_("Номер свідоцтва ПДВ"), max_length=12, blank=True, null=True)

    # Статус
    is_active = models.BooleanField(_("Активний"), default=True)

    # Метадані
    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Платник податків")
        verbose_name_plural = _("Платники податків")
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.tax_number})"

    def get_absolute_url(self):
        return reverse('taxpayer_detail', kwargs={'pk': self.pk})

    def clean(self):
        # Перевірка та встановлення правильної ставки податку в залежності від групи та системи
        if self.tax_system == TAX_SYSTEM_SIMPLIFIED:
            if self.tax_group == TAX_GROUP_3:
                if self.tax_rate not in [rate[0] for rate in TAX_RATE_3_CHOICES]:
                    self.tax_rate = 5.0
            elif self.tax_group == TAX_GROUP_2:
                if self.tax_rate not in [rate[0] for rate in TAX_RATE_2_CHOICES]:
                    self.tax_rate = 20.0
            elif self.tax_group == TAX_GROUP_1:
                if self.tax_rate not in [rate[0] for rate in TAX_RATE_1_CHOICES]:
                    self.tax_rate = 10.0
        else:  # Загальна система
            self.tax_rate = 18.0
            self.tax_group = None

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class TaxpayerSettings(models.Model):
    """Модель для додаткових налаштувань платника податків"""
    # Django автоматично створює id = models.AutoField(primary_key=True)

    taxpayer = models.OneToOneField(
        Taxpayer,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name=_("Платник податків")
    )

    # Налаштування автоматизації
    auto_categorize = models.BooleanField(
        _("Автоматична категоризація"),
        default=True,
        help_text=_("Автоматично визначати категорії фінансових операцій")
    )

    auto_process_income = models.BooleanField(
        _("Автоматична обробка доходів"),
        default=False,
        help_text=_("Автоматично створювати записи книги доходів для доходів")
    )

    # Налаштування податків
    tax_reminder_days = models.IntegerField(
        _("Днів до нагадування про податки"),
        default=7,
        help_text=_("За скільки днів нагадувати про сплату податків")
    )

    # Налаштування синхронізації
    sync_frequency_days = models.IntegerField(
        _("Частота синхронізації (днів)"),
        default=1,
        help_text=_("Частота автоматичної синхронізації банківських операцій (в днях)")
    )

    last_sync_date = models.DateTimeField(
        _("Дата останньої синхронізації"),
        blank=True,
        null=True
    )

    # Інші налаштування
    notes = models.TextField(_("Примітки"), blank=True, null=True)

    class Meta:
        verbose_name = _("Налаштування платника податків")
        verbose_name_plural = _("Налаштування платників податків")

    def __str__(self):
        return f"Налаштування для {self.taxpayer}"

class TaxpayerDocument(models.Model):
    """Модель для документів платника податків"""
    # Django автоматично створює id = models.AutoField(primary_key=True)

    taxpayer = models.ForeignKey(
        Taxpayer,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_("Платник податків")
    )

    title = models.CharField(_("Назва"), max_length=255)
    document_type = models.CharField(_("Тип документа"), max_length=100)
    file = models.FileField(_("Файл"), upload_to='taxpayer_documents/%Y/%m/')
    issue_date = models.DateField(_("Дата видачі"), blank=True, null=True)
    expiry_date = models.DateField(_("Дата закінчення дії"), blank=True, null=True)

    notes = models.TextField(_("Примітки"), blank=True, null=True)
    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)

    class Meta:
        verbose_name = _("Документ платника податків")
        verbose_name_plural = _("Документи платників податків")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.taxpayer}"

    def get_absolute_url(self):
        return reverse('taxpayer_document_detail', kwargs={'pk': self.pk})