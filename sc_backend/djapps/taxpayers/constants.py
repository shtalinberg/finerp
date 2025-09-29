
from django.utils.translation import gettext_lazy as _

# Системи оподаткування
TAX_SYSTEM_SIMPLIFIED = 'simplified'
TAX_SYSTEM_GENERAL = 'general'

TAX_SYSTEMS = (
    (TAX_SYSTEM_SIMPLIFIED, _("Єдиний податок (спрощена система)")),
    (TAX_SYSTEM_GENERAL, _("Загальна система")),
)

# Групи платників єдиного податку
TAX_GROUP_1 = 1
TAX_GROUP_2 = 2
TAX_GROUP_3 = 3

TAX_GROUP_CHOICES = (
    (TAX_GROUP_1, _("1-а група")),
    (TAX_GROUP_2, _("2-а група")),
    (TAX_GROUP_3, _("3-я група")),
)

# Ставки податку для 3-ї групи
TAX_RATE_3_CHOICES = (
    (2.0, _("2%")),
    (3.0, _("3%")),
    (5.0, _("5%")),
)

# Ставки податку для 2-ї групи
TAX_RATE_2_CHOICES = (
    (17.0, _("17%")),
    (18.0, _("18%")),
    (19.0, _("19%")),
    (20.0, _("20%")),
)

# Ставки податку для 1-ї групи
TAX_RATE_1_CHOICES = (
    (7.0, _("7%")),
    (8.0, _("8%")),
    (9.0, _("9%")),
    (10.0, _("10%")),
)

# Ставки ЄСВ
ESV_RATE_0 = 0.0
ESV_RATE_22 = 22.0

ESV_RATE_CHOICES = (
    (ESV_RATE_0, _("0%")),
    (ESV_RATE_22, _("22%")),
)