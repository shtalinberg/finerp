
import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from banks.models import BankAccount
from taxpayers.models import Taxpayer

from .constants import (
    EXPENSE_CATEGORIES,
    EXPENSE_CATEGORY_OTHER_EXPENSE,
    INCOME_CATEGORIES,
    INCOME_CATEGORY_OTHER_INCOME,
    OPERATION_SOURCES,
    OPERATION_STATUS_COMPLETED,
    OPERATION_STATUSES,
    OPERATION_TYPE_OTHER,
    OPERATION_TYPES,
    PROCESSING_STATUS_NEW,
    PROCESSING_STATUSES,
    SOURCE_MANUAL,
)


class Finop(models.Model):
    """Модель для фінансових операцій з банківських виписок"""
    # Django автоматично створює id = models.AutoField(primary_key=True)

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
        related_name='finops',
        verbose_name=_("Платник податків")
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='finops',
        verbose_name=_("Банківський рахунок")
    )

    # Інформація про операцію
    operation_date = models.DateTimeField(_("Дата операції"))
    amount = models.DecimalField(_("Сума"), max_digits=18, decimal_places=2)
    amount_uah = models.DecimalField(_("Сума в гривнях"), max_digits=18, decimal_places=2)
    description = models.TextField(_("Опис"))

    # Тип операції
    operation_type = models.CharField(
        _("Тип операції"),
        max_length=20,
        choices=OPERATION_TYPES,
        default=OPERATION_TYPE_OTHER
    )

    # Статус операції
    operation_status = models.CharField(
        _("Статус операції"),
        max_length=20,
        choices=OPERATION_STATUSES,
        default=OPERATION_STATUS_COMPLETED
    )

    # Категорії
    income_category = models.CharField(
        _("Категорія доходу"),
        max_length=50,
        choices=INCOME_CATEGORIES,
        default=INCOME_CATEGORY_OTHER_INCOME,
        blank=True,
        null=True
    )

    expense_category = models.CharField(
        _("Категорія витрат"),
        max_length=50,
        choices=EXPENSE_CATEGORIES,
        default=EXPENSE_CATEGORY_OTHER_EXPENSE,
        blank=True,
        null=True
    )

    # Джерело операції
    source = models.CharField(
        _("Джерело операції"),
        max_length=20,
        choices=OPERATION_SOURCES,
        default=SOURCE_MANUAL
    )

    # Податкові поля
    is_taxable = models.BooleanField(_("Оподатковується"), default=True)

    # Банківські дані
    bank_operation_id = models.CharField(_("ID банківської операції"), max_length=50, blank=True, null=True)
    sender_name = models.CharField(_("Відправник"), max_length=255, blank=True, null=True)
    sender_account = models.CharField(_("Рахунок відправника"), max_length=29, blank=True, null=True)
    recipient_name = models.CharField(_("Одержувач"), max_length=255, blank=True, null=True)
    recipient_account = models.CharField(_("Рахунок одержувача"), max_length=29, blank=True, null=True)

    # Статус обробки
    processing_status = models.CharField(
        _("Статус обробки"),
        max_length=20,
        choices=PROCESSING_STATUSES,
        default=PROCESSING_STATUS_NEW
    )

    # Метадані
    notes = models.TextField(_("Примітки"), blank=True, null=True)
    tags = models.CharField(_("Теги"), max_length=255, blank=True, null=True)
    reference = models.CharField(_("Референс"), max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Фінансова операція")
        verbose_name_plural = _("Фінансові операції")
        ordering = ['-operation_date']
        indexes = [
            models.Index(fields=['taxpayer', 'operation_date']),
            models.Index(fields=['operation_type']),
            models.Index(fields=['processing_status']),
        ]

    def __str__(self):
        return f"{self.operation_date} - {self.amount} - {self.description[:50]}"

    def get_absolute_url(self):
        return reverse('finop_detail', kwargs={'pk': self.pk})

    @property
    def is_income(self):
        return self.operation_type == 'income'

    @property
    def is_expense(self):
        return self.operation_type == 'expense'

    @property
    def is_transfer(self):
        return self.operation_type == 'transfer'

    @property
    def is_processed(self):
        return self.processing_status == 'processed'

    def mark_as_processed(self):
        """Позначити операцію як оброблену"""
        self.processing_status = 'processed'
        self.save(update_fields=['processing_status', 'updated_at'])

    def mark_as_ignored(self):
        """Позначити операцію як проігноровану"""
        self.processing_status = 'ignored'
        self.save(update_fields=['processing_status', 'updated_at'])

    def update_category(self):
        """Автоматичне визначення категорії на основі опису"""
        # Реалізувати алгоритм автоматичної категоризації
        # Наприклад, на основі ключових слів в описі
        pass

    def save(self, *args, **kwargs):
        # Якщо категорія не вказана, встановлюємо її за типом операції
        if self.operation_type == 'income' and not self.income_category:
            self.income_category = INCOME_CATEGORY_OTHER_INCOME
        elif self.operation_type == 'expense' and not self.expense_category:
            self.expense_category = EXPENSE_CATEGORY_OTHER_EXPENSE

        # Встановлюємо amount_uah рівним amount, якщо воно не задано
        if self.amount_uah is None or self.amount_uah == 0:
            self.amount_uah = self.amount

        # Визначення операції як оподатковуваної за замовчуванням, якщо це дохід
        if self.operation_type == 'income' and self.is_taxable is None:
            self.is_taxable = True

        super().save(*args, **kwargs)

class Category(models.Model):
    """Модель для користувацьких категорій фінансових операцій"""

    # Типи категорій
    CATEGORY_TYPE_INCOME = 'income'
    CATEGORY_TYPE_EXPENSE = 'expense'
    CATEGORY_TYPE_BOTH = 'both'

    CATEGORY_TYPES = (
        (CATEGORY_TYPE_INCOME, _("Дохід")),
        (CATEGORY_TYPE_EXPENSE, _("Витрата")),
        (CATEGORY_TYPE_BOTH, _("Обидва")),
    )

    # Django автоматично створює id = models.AutoField(primary_key=True)
    taxpayer = models.ForeignKey(
        Taxpayer,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name=_("Платник податків")
    )
    name = models.CharField(_("Назва"), max_length=100)
    category_type = models.CharField(
        _("Тип категорії"),
        max_length=20,
        choices=CATEGORY_TYPES,
        default=CATEGORY_TYPE_BOTH
    )
    description = models.TextField(_("Опис"), blank=True, null=True)
    is_default = models.BooleanField(_("За замовчуванням"), default=False)
    is_active = models.BooleanField(_("Активна"), default=True)
    order = models.PositiveIntegerField(_("Порядок"), default=0)
    color = models.CharField(_("Колір"), max_length=20, default='primary')
    icon = models.CharField(_("Іконка"), max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Категорія")
        verbose_name_plural = _("Категорії")
        ordering = ['order', 'name']
        unique_together = ['taxpayer', 'name', 'category_type']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})

class Tag(models.Model):
    """Модель для тегів фінансових операцій"""
    # Django автоматично створює id = models.AutoField(primary_key=True)
    taxpayer = models.ForeignKey(
        Taxpayer,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_("Платник податків")
    )
    name = models.CharField(_("Назва"), max_length=50)
    color = models.CharField(_("Колір"), max_length=20, default='primary')
    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)

    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")
        ordering = ['name']
        unique_together = ['taxpayer', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag_detail', kwargs={'pk': self.pk})