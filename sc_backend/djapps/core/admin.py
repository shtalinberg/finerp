from django.contrib import admin

from .models import Settings


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'language', 'email_notifications', 'in_app_notifications')
    list_filter = ('theme', 'language', 'email_notifications', 'in_app_notifications')
    search_fields = ('user__username',)