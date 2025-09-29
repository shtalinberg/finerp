
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .constants import (
    TASK_PRIORITIES,
    TASK_PRIORITY_NORMAL,
    TASK_STATUS_PENDING,
    TASK_STATUSES,
)

User = get_user_model()


class Task(models.Model):
    """Модель для задач системи"""
    uid = models.UUIDField(
        verbose_name=_("UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique Identifier UUID"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_("Користувач")
    )
    title = models.CharField(_("Назва"), max_length=200)
    description = models.TextField(_("Опис"), blank=True, null=True)

    status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=TASK_STATUSES,
        default=TASK_STATUS_PENDING
    )

    priority = models.CharField(
        _("Пріоритет"),
        max_length=20,
        choices=TASK_PRIORITIES,
        default=TASK_PRIORITY_NORMAL
    )

    # taxpayer = models.ForeignKey(
    #     'taxpayers.Taxpayer',
    #     on_delete=models.SET_NULL,
    #     related_name='tasks',
    #     null=True,
    #     blank=True,
    #     verbose_name=_("ФОП")
    # )

    due_date = models.DateTimeField(_("Термін виконання"), blank=True, null=True)
    completed_at = models.DateTimeField(_("Завершено"), null=True, blank=True)

    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Задача")
        verbose_name_plural = _("Задачі")
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})

    def complete(self):
        """Позначити задачу як виконану"""
        from django.utils import timezone

        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()