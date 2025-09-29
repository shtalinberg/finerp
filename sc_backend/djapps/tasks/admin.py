
from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'due_date', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'
    list_per_page = 20

    actions = ['mark_as_completed', 'mark_as_pending']

    def mark_as_completed(self, request, queryset):
        """Позначити вибрані задачі як виконані"""
        for task in queryset:
            task.complete()

        self.message_user(request, f"Позначено {queryset.count()} задач як виконані")
    mark_as_completed.short_description = "Позначити вибрані задачі як виконані"

    def mark_as_pending(self, request, queryset):
        """Позначити вибрані задачі як очікуючі"""
        queryset.update(status='pending', completed_at=None)
        self.message_user(request, f"Позначено {queryset.count()} задач як очікуючі")
    mark_as_pending.short_description = "Позначити вибрані задачі як очікуючі"