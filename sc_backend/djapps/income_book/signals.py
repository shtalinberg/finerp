
from django.db.models.signals import post_save
from django.dispatch import receiver

# from notifications.services import NotificationService
from tax_reports.models import TaxReport

from .models import IncomeRecord

# from django.utils import timezone




@receiver(post_save, sender=IncomeRecord)
def income_record_saved(sender, instance, created, **kwargs):
    """
    Обробка події створення/зміни запису книги доходів

    - Створення сповіщення
    - Перерахунок податкового звіту, якщо він існує
    """
    # # Створюємо сповіщення для користувача
    # if created:
    #     # Створення нового запису
    #     NotificationService.send_notification(
    #         user=instance.taxpayer.user,
    #         title="Новий запис доходу",
    #         message=f"Додано новий запис доходу на суму {instance.amount} грн.",
    #         theme='success',
    #         notification_type='income'
    #     )
    # else:
    #     # Оновлення існуючого запису
    #     if instance.status == 'cancelled':
    #         # Скасування запису
    #         NotificationService.send_notification(
    #             user=instance.taxpayer.user,
    #             title="Запис доходу скасовано",
    #             message=f"Запис доходу від {instance.date} на суму {instance.amount} грн. скасовано.",
    #             theme='warning',
    #             notification_type='income'
    #         )
    #     elif instance.status == 'adjusted':
    #         # Коригування запису
    #         NotificationService.send_notification(
    #             user=instance.taxpayer.user,
    #             title="Запис доходу скориговано",
    #             message=f"Запис доходу від {instance.date} на суму {instance.amount} грн. скориговано.",
    #             theme='warning',
    #             notification_type='income'
    #         )

    # Перевіряємо чи змінився запис під час події save()
    if not created and not hasattr(instance, '_no_recalculate'):
        # Визначаємо квартал запису
        year = instance.date.year
        quarter = (instance.date.month - 1) // 3 + 1

        # Шукаємо податковий звіт за цей квартал
        try:
            tax_report = TaxReport.objects.get(
                taxpayer=instance.taxpayer,
                period__year=year,
                period__quarter=quarter
            )

            # Перераховуємо податки, якщо звіт у статусі 'calculated'
            if tax_report.status == 'calculated':
                tax_report.calculate_taxes()

                # NotificationService.send_notification(
                #     user=instance.taxpayer.user,
                #     title="Податковий звіт оновлено",
                #     message=f"Податковий звіт за {quarter} квартал {year} року автоматично оновлено.",
                #     theme='info',
                #     notification_type='tax'
                # )
        except TaxReport.DoesNotExist:
            # Звіт ще не створено, нічого не робимо
            pass