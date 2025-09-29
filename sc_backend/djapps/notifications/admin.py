
from django.contrib import admin

from .models import Notification, Settings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'theme', 'notification_type', 'is_read', 'created_at')
    list_filter = ('theme', 'notification_type', 'is_read')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'
    list_per_page = 20

    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        """Позначити вибрані сповіщення як прочитані"""
        for notification in queryset:
            notification.mark_as_read()

        self.message_user(request, f"Позначено {queryset.count()} сповіщень як прочитані")
    mark_as_read.short_description = "Позначити вибрані сповіщення як прочитані"

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'language', 'email_notifications', 'in_app_notifications')
    list_filter = ('theme', 'language', 'email_notifications', 'in_app_notifications')
    search_fields = ('user__username',)