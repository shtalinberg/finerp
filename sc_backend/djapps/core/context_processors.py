
from django.utils import timezone

from taxpayers.models import Taxpayer

from .models import Notification


def notifications(request):
    """
    Контекстний процесор для сповіщень

    Додає в контекст шаблонів непрочитані сповіщення для поточного користувача
    """
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')[:5]  # Обмежуємо до 5 останніх сповіщень

        unread_count = unread_notifications.count()

        return {
            'unread_notifications': unread_notifications,
            'unread_notifications_count': unread_count
        }

    return {}

def taxpayers(request):
    """
    Контекстний процесор для платників податків

    Додає в контекст шаблонів список ФОП користувача
    """
    if request.user.is_authenticated:
        taxpayers_list = Taxpayer.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('full_name')

        # Отримуємо вибраного платника податків
        selected_taxpayer_id = request.GET.get('taxpayer')
        if selected_taxpayer_id:
            try:
                selected_taxpayer = Taxpayer.objects.get(id=selected_taxpayer_id, user=request.user)
            except Taxpayer.DoesNotExist:
                selected_taxpayer = taxpayers_list.first() if taxpayers_list.exists() else None
        else:
            # Беремо першого доступного платника податків
            selected_taxpayer = taxpayers_list.first() if taxpayers_list.exists() else None

        return {
            'taxpayers_list': taxpayers_list,
            'selected_taxpayer': selected_taxpayer
        }

    return {}

def current_date(request):
    """
    Контекстний процесор для поточної дати

    Додає в контекст шаблонів поточну дату
    """
    now = timezone.now()

    return {
        'current_date': now,
        'current_year': now.year,
        'current_month': now.month,
        'current_day': now.day,
        'current_quarter': (now.month - 1) // 3 + 1
    }