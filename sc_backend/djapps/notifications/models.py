import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import (
    NOTIFICATION_THEME_INFO,
    NOTIFICATION_THEMES,
    NOTIFICATION_TYPE_SYSTEM,
    NOTIFICATION_TYPES,
)

User = get_user_model()

class Notification(models.Model):
    """Модель для сповіщень користувачів"""
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
        related_name='notifications',
        verbose_name=_("Користувач")
    )
    title = models.CharField(_("Заголовок"), max_length=200)
    message = models.TextField(_("Повідомлення"))

    theme = models.CharField(
        _("Тема"),
        max_length=20,
        choices=NOTIFICATION_THEMES,
        default=NOTIFICATION_THEME_INFO
    )

    notification_type = models.CharField(
        _("Тип сповіщення"),
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default=NOTIFICATION_TYPE_SYSTEM
    )

    is_read = models.BooleanField(_("Прочитано"), default=False)
    read_at = models.DateTimeField(_("Прочитано у"), blank=True, null=True)

    created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Сповіщення")
        verbose_name_plural = _("Сповіщення")
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def mark_as_read(self):
        """Позначити сповіщення як прочитане"""
        from django.utils import timezone

        self.is_read = True
        self.read_at = timezone.now()
        self.save()