
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Task


class TaskListView(LoginRequiredMixin, ListView):
    """Список задач"""
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)

        # Фільтр за статусом
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Фільтр за пріоритетом
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Фільтр за ФОП
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            queryset = queryset.filter(taxpayer_id=taxpayer_id)

