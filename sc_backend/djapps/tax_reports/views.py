
import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

from income_book.models import IncomeRecord
from tax_reports.models import TaxPeriod, TaxReport


class TaxReportListView(LoginRequiredMixin, ListView):
    """List view for tax reports"""
    model = TaxReport
    template_name = 'tax_reports/tax_report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        return TaxReport.objects.filter(taxpayer=self.request.user.taxpayer).select_related('period')

class TaxReportDetailView(LoginRequiredMixin, DetailView):
    """Detail view for tax report"""
    model = TaxReport
    template_name = 'tax_reports/tax_report_detail.html'
    context_object_name = 'report'

    def get_queryset(self):
        return TaxReport.objects.filter(taxpayer=self.request.user.taxpayer)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get income records for the period
        report = self.get_object()
        context['income_records'] = IncomeRecord.objects.filter(
            taxpayer=self.request.user.taxpayer,
            date__gte=report.period.start_date,
            date__lte=report.period.end_date
        ).order_by('date')

        return context

class TaxReportPreviewView(LoginRequiredMixin, TemplateView):
    """Preview view for tax report before creating"""
    template_name = 'tax_reports/tax_report_preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get quarter from URL
        quarter = int(self.kwargs.get('quarter', 1))
        if quarter < 1 or quarter > 4:
            quarter = 1

        # Get year from URL or use current year
        year = int(self.kwargs.get('year', timezone.now().year))

        # Define period dates
        if quarter == 1:
            start_date = datetime.date(year, 1, 1)
            end_date = datetime.date(year, 3, 31)
        elif quarter == 2:
            start_date = datetime.date(year, 4, 1)
            end_date = datetime.date(year, 6, 30)
        elif quarter == 3:
            start_date = datetime.date(year, 7, 1)
            end_date = datetime.date(year, 9, 30)
        else:
            start_date = datetime.date(year, 10, 1)
            end_date = datetime.date(year, 12, 31)

        # Get or create tax period
        period, _ = TaxPeriod.objects.get_or_create(
            year=year,
            quarter=quarter,
            defaults={
                'start_date': start_date,
                'end_date': end_date
            }
        )

        # Check if report already exists
        try:
            report = TaxReport.objects.get(
                taxpayer=self.request.user.taxpayer,
                period=period
            )
            context['existing_report'] = report
        except TaxReport.DoesNotExist:
            pass

        # Get income for the period
        income_records = IncomeRecord.objects.filter(
            taxpayer=self.request.user.taxpayer,
            date__gte=start_date,
            date__lte=end_date
        )

        total_income = income_records.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Calculate taxes
        single_tax = total_income * Decimal('0.05')  # 5% Single tax
        military_tax = total_income * Decimal('0.01')  # 1% Military tax

        # Get ESV amount (fixed by law)
        # Note: This would need to be updated based on current legislation
        esv_amount = Decimal('1474.00')  # Example value for 2023

        context.update({
            'period': period,
            'income_records': income_records,
            'total_income': total_income,
            'single_tax': single_tax,
            'military_tax': military_tax,
            'esv_amount': esv_amount,
            'year': year,
            'quarter': quarter
        })

        return context

def post(self, request, *args, **kwargs):
        """Create tax report"""
        context = self.get_context_data(**kwargs)

        period = context['period']
        total_income = context['total_income']
        single_tax = context['single_tax']
        military_tax = context['military_tax']
        esv_amount = context['esv_amount']

        # Create or update tax report
        tax_report, created = TaxReport.objects.update_or_create(
            taxpayer=request.user.taxpayer,
            period=period,
            defaults={
                'total_income': total_income,
                'single_tax_amount': single_tax,
                'military_tax_amount': military_tax,
                'esv_amount': esv_amount,
                'status': 'calculated'
            }
        )

        if created:
            messages.success(request, f"Податковий звіт за {period} успішно створено")
        else:
            messages.success(request, f"Податковий звіт за {period} успішно оновлено")

        return redirect('tax_report_detail', pk=tax_report.pk)

class TaxReportMarkPaidView(LoginRequiredMixin, DetailView):
    """View to mark taxes as paid"""
    model = TaxReport
    http_method_names = ['post']

    def get_queryset(self):
        return TaxReport.objects.filter(taxpayer=self.request.user.taxpayer)

    def post(self, request, *args, **kwargs):
        tax_report = self.get_object()

        # Update paid status
        if 'single_tax' in request.POST:
            tax_report.single_tax_paid = True
        if 'military_tax' in request.POST:
            tax_report.military_tax_paid = True
        if 'esv' in request.POST:
            tax_report.esv_paid = True

        # Check if all taxes are paid
        if tax_report.single_tax_paid and tax_report.military_tax_paid and tax_report.esv_paid:
            tax_report.status = 'paid'

        tax_report.save()

        if request.headers.get('HX-Request'):
            return render(request, 'tax_reports/partials/tax_status.html', {'report': tax_report})
        else:
            return redirect('tax_report_detail', pk=tax_report.pk)

class TaxReportSubmitView(LoginRequiredMixin, DetailView):
    """View to mark tax report as submitted"""
    model = TaxReport
    http_method_names = ['post']

    def get_queryset(self):
        return TaxReport.objects.filter(taxpayer=self.request.user.taxpayer)

    def post(self, request, *args, **kwargs):
        tax_report = self.get_object()

        submission_date = request.POST.get('submission_date')
        submission_number = request.POST.get('submission_number')

        if submission_date and submission_number:
            tax_report.submission_date = datetime.datetime.strptime(submission_date, '%Y-%m-%d').date()
            tax_report.submission_number = submission_number
            tax_report.status = 'submitted'
            tax_report.save()

            messages.success(request, "Звіт успішно позначено як поданий")
        else:
            messages.error(request, "Вкажіть дату та номер подання")

        return redirect('tax_report_detail', pk=tax_report.pk)