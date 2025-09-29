
from django.contrib.auth import get_user_model
from django.utils import timezone

# from notifications.constants import NOTIFICATION_THEME_INFO, NOTIFICATION_TYPE_SYSTEM

# from .models import Notification

User = get_user_model()


# def send_notification(user, title, message, theme=NOTIFICATION_THEME_INFO, notification_type=NOTIFICATION_TYPE_SYSTEM):
#     """
#     Надіслати сповіщення користувачу

#     Args:
#         user: Користувач (об'єкт User або ID)
#         title: Заголовок сповіщення
#         message: Текст сповіщення
#         theme: Тема сповіщення (info, success, warning, error)
#         notification_type: Тип сповіщення (system, tax, income, finance)

#     Returns:
#         Створене сповіщення
#     """
#     if isinstance(user, int):
#         try:
#             user = User.objects.get(id=user)
#         except User.DoesNotExist:
#             return None

#     notification = Notification.objects.create(
#         user=user,
#         title=title,
#         message=message,
#         theme=theme,
#         notification_type=notification_type
#     )

#     # Додати логіку для надсилання email, якщо це налаштовано в профілі користувача

#     return notification

def get_current_quarter():
    """
    Отримати поточний квартал

    Returns:
        Кортеж (рік, квартал, початкова_дата, кінцева_дата)
    """
    now = timezone.now()
    year = now.year
    month = now.month

    if month <= 3:
        quarter = 1
        start_date = timezone.datetime(year, 1, 1)
        end_date = timezone.datetime(year, 3, 31, 23, 59, 59)
    elif month <= 6:
        quarter = 2
        start_date = timezone.datetime(year, 4, 1)
        end_date = timezone.datetime(year, 6, 30, 23, 59, 59)
    elif month <= 9:
        quarter = 3
        start_date = timezone.datetime(year, 7, 1)
        end_date = timezone.datetime(year, 9, 30, 23, 59, 59)
    else:
        quarter = 4
        start_date = timezone.datetime(year, 10, 1)
        end_date = timezone.datetime(year, 12, 31, 23, 59, 59)

    return (year, quarter, start_date, end_date)

def get_quarter_dates(year, quarter):
    """
    Отримати дати початку та кінця кварталу

    Args:
        year: Рік
        quarter: Квартал (1-4)

    Returns:
        Кортеж (початкова_дата, кінцева_дата)
    """
    if quarter == 1:
        start_date = timezone.datetime(year, 1, 1)
        end_date = timezone.datetime(year, 3, 31, 23, 59, 59)
    elif quarter == 2:
        start_date = timezone.datetime(year, 4, 1)
        end_date = timezone.datetime(year, 6, 30, 23, 59, 59)
    elif quarter == 3:
        start_date = timezone.datetime(year, 7, 1)
        end_date = timezone.datetime(year, 9, 30, 23, 59, 59)
    else:
        start_date = timezone.datetime(year, 10, 1)
        end_date = timezone.datetime(year, 12, 31, 23, 59, 59)

    return (start_date, end_date)