# class Settings(models.Model):
#     """Модель для налаштувань системи"""
#     uid = models.UUIDField(
#         verbose_name=_("UUID"),
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         help_text=_("Unique Identifier UUID"),
#     )
#     user = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name='settings',
#         verbose_name=_("Користувач")
#     )

#     # Налаштування сповіщень
#     email_notifications = models.BooleanField(_("Email сповіщення"), default=True)
#     in_app_notifications = models.BooleanField(_("Сповіщення в додатку"), default=True)

#     # Налаштування інтерфейсу
#     theme = models.CharField(_("Тема"), max_length=20, default='light')
#     language = models.CharField(_("Мова"), max_length=10, default='uk')

#     # Налаштування системи
#     default_taxpayer = models.ForeignKey(
#         'taxpayers.Taxpayer',
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         related_name='settings',
#         verbose_name=_("ФОП за замовчуванням")
#     )

#     created_at = models.DateTimeField(_("Створено"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Оновлено"), auto_now=True)

#     class Meta:
#         verbose_name = _("Налаштування")
#         verbose_name_plural = _("Налаштування")

#     def __str__(self):
#         return f"Налаштування для {self.user.username}"