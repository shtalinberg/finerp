import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from finops.constants import OPERATION_TYPE_EXPENSE, OPERATION_TYPE_INCOME
from finops.models import Finop
from income_book.models import IncomeRecord
from tax_reports.models import TaxReport
from taxpayers.models import Taxpayer

# from notifications.models import Notification
# from tasks.models import Task
from .utils import get_current_quarter


class DashboardView(LoginRequiredMixin, TemplateView):
    """Представлення для головної сторінки"""
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отримуємо платників податків користувача
        taxpayers = Taxpayer.objects.filter(
            user=self.request.user,
            is_active=True
        )

        # Якщо немає платників податків, повертаємо базовий контекст
        if not taxpayers.exists():
            context['no_taxpayers'] = True
            return context

        # Отримуємо вибраного платника податків
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                selected_taxpayer = Taxpayer.objects.get(id=taxpayer_id, user=self.request.user)
            except Taxpayer.DoesNotExist:
                selected_taxpayer = taxpayers.first()
        else:
            selected_taxpayer = taxpayers.first()

        # Отримуємо поточний квартал та дати
        year, quarter, q_start, q_end = get_current_quarter()

        # Фінансові показники
        # Дохід за поточний квартал
        quarter_income = IncomeRecord.objects.filter(
            taxpayer=selected_taxpayer,
            date__gte=q_start.date(),
            date__lte=q_end.date()
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Дохід за поточний рік
        year_income = IncomeRecord.objects.filter(
            taxpayer=selected_taxpayer,
            date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Транзакції за останній місяць
        last_month_date = timezone.now() - datetime.timedelta(days=30)

        # Доходи за останній місяць
        month_income = Finop.objects.filter(
            taxpayer=selected_taxpayer,
            operation_date__gte=last_month_date,
            operation_type=OPERATION_TYPE_INCOME
        ).aggregate(total=Sum('amount_uah'))['total'] or 0

        # Витрати за останній місяць
        month_expenses = Finop.objects.filter(
            taxpayer=selected_taxpayer,
            operation_date__gte=last_month_date,
            operation_type=OPERATION_TYPE_EXPENSE
        ).aggregate(total=Sum('amount_uah'))['total'] or 0

        # Розрахунок податків
        tax_rate = selected_taxpayer.tax_rate / 100
        esv_rate = selected_taxpayer.esv_rate / 100

        # Податок на дохід
        income_tax = quarter_income * tax_rate

        # Військовий збір (завжди 1.5%)
        military_tax = quarter_income * 0.015

        # ЄСВ (спрощений розрахунок)
        min_wage = 6700  # Мінімальна заробітна плата
        esv_amount = min_wage * esv_rate if esv_rate > 0 else 0

        # Отримуємо останні фінансові операції
        recent_finops = Finop.objects.filter(
            taxpayer=selected_taxpayer
        ).order_by('-operation_date')[:5]

        # Задачі та сповіщення
        # Задачі з терміном виконання на цей тиждень
        # week_end = timezone.now() + datetime.timedelta(days=7)
        # tasks = Task.objects.filter(
        #     user=self.request.user,
        #     due_date__lte=week_end,
        #     status__in=['pending', 'in_progress']
        # ).order_by('due_date')[:5]

        # Отримуємо останні сповіщення
        # notifications = Notification.objects.filter(
        #     user=self.request.user,
        #     is_read=False
        # ).order_by('-created_at')[:5]

        # Перевіряємо чи створено податковий звіт за поточний квартал
        try:
            tax_report = TaxReport.objects.get(
                taxpayer=selected_taxpayer,
                period__year=year,
                period__quarter=quarter
            )
            tax_report_status = tax_report.status
            report_exists = True
        except TaxReport.DoesNotExist:
            tax_report = None
            tax_report_status = None
            report_exists = False

        # Додаємо дані до контексту
        context.update({
            'selected_taxpayer': selected_taxpayer,
            'current_year': year,
            'current_quarter': quarter,
            'quarter_start': q_start.date(),
            'quarter_end': q_end.date(),
            'quarter_income': quarter_income,
            'year_income': year_income,
            'month_income': month_income,
            'month_expenses': month_expenses,
            'income_tax': income_tax,
            'military_tax': military_tax,
            'esv_amount': esv_amount,
            'total_tax': income_tax + military_tax + esv_amount,
            'tax_report': tax_report,
            'tax_report_status': tax_report_status,
            'report_exists': report_exists,
            'recent_finops': recent_finops,
            'tasks': tasks,
            'notifications': notifications
        })

        return context

# Представлення для сторінок помилок
def error_403(request, exception=None):
    return render(request, '403.html', status=403)

def error_404(request, exception=None):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)

def error_503(request, exception=None):
    return render(request, '503.html', status=503)

# Представлення для тестування сторінок помилок (тільки в режимі DEBUG)
def test_error_page(request, error_code):
    template_name = f'{error_code}.html'
    return render(request, template_name, status=int(error_code))