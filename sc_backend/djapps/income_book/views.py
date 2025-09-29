
import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from finops.constants import OPERATION_TYPE_INCOME
from finops.models import Finop
from taxpayers.models import Taxpayer

from .forms import IncomeRecordForm
from .models import IncomeRecord


class IncomeBookListView(LoginRequiredMixin, ListView):
    """Список записів книги доходів"""
    model = IncomeRecord
    template_name = 'income_book/income_book_list.html'
    context_object_name = 'records'
    paginate_by = 25

    def get_queryset(self):
        # Спочатку отримуємо вибраного платника податків
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                taxpayer = Taxpayer.objects.get(id=taxpayer_id, user=self.request.user)
            except Taxpayer.DoesNotExist:
                # Беремо першого доступного платника податків
                taxpayers = Taxpayer.objects.filter(user=self.request.user, is_active=True)
                taxpayer = taxpayers.first() if taxpayers.exists() else None
        else:
            # Беремо першого доступного платника податків
            taxpayers = Taxpayer.objects.filter(user=self.request.user, is_active=True)
            taxpayer = taxpayers.first() if taxpayers.exists() else None

        if not taxpayer:
            return IncomeRecord.objects.none()

        queryset = IncomeRecord.objects.filter(taxpayer=taxpayer)

        # Застосовуємо фільтри
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        income_type = self.request.GET.get('income_type')
        if income_type:
            queryset = queryset.filter(income_type=income_type)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(description__icontains=search)

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        else:
            # За замовчуванням показуємо тільки активні записи
            queryset = queryset.filter(status='active')

        return queryset.select_related('taxpayer', 'finop')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отримуємо вибраного платника податків
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                selected_taxpayer = Taxpayer.objects.get(id=taxpayer_id, user=self.request.user)
            except Taxpayer.DoesNotExist:
                selected_taxpayer = None
        else:
            taxpayers = Taxpayer.objects.filter(user=self.request.user, is_active=True)
            selected_taxpayer = taxpayers.first() if taxpayers.exists() else None

        context['selected_taxpayer'] = selected_taxpayer

        # Отримуємо загальну суму для відфільтрованих записів
        queryset = self.get_queryset()
        total_income = queryset.aggregate(total=Sum('amount'))['total'] or 0
        context['total_income'] = total_income

        # Додаємо інформацію про квартали
        if selected_taxpayer:
            now = timezone.now()
            current_year = now.year
            quarters = []

            for q in range(1, 5):
                if q == 1:
                    q_start = datetime.date(current_year, 1, 1)
                    q_end = datetime.date(current_year, 3, 31)
                elif q == 2:
                    q_start = datetime.date(current_year, 4, 1)
                    q_end = datetime.date(current_year, 6, 30)
                elif q == 3:
                    q_start = datetime.date(current_year, 7, 1)
                    q_end = datetime.date(current_year, 9, 30)
                else:
                    q_start = datetime.date(current_year, 10, 1)
                    q_end = datetime.date(current_year, 12, 31)

                q_total = IncomeRecord.objects.filter(
                    taxpayer=selected_taxpayer,
                    date__gte=q_start,
                    date__lte=q_end,
                    status='active'
                ).aggregate(total=Sum('amount'))['total'] or 0

                quarters.append({
                    'number': q,
                    'start_date': q_start,
                    'end_date': q_end,
                    'total': q_total,
                    'is_current': (q - 1) == now.month // 3
                })

            context['quarters'] = quarters
            context['current_year'] = current_year

        return context

class IncomeRecordDetailView(LoginRequiredMixin, DetailView):
    """Детальний перегляд запису книги доходів"""
    model = IncomeRecord
    template_name = 'income_book/income_record_detail.html'
    context_object_name = 'record'

    def get_queryset(self):
        # Обмежуємо доступ до записів тільки власним платникам податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user)
        return IncomeRecord.objects.filter(taxpayer__in=taxpayers).select_related('taxpayer', 'finop', 'original_record')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Додаємо інформацію про коригувальні записи, якщо вони є
        record = self.get_object()
        if record.adjustments.exists():
            context['adjustments'] = record.adjustments.all().order_by('-created_at')

        return context

class IncomeRecordCreateView(LoginRequiredMixin, CreateView):
    """Створення нового запису книги доходів"""
    model = IncomeRecord
    form_class = IncomeRecordForm
    template_name = 'income_book/income_record_form.html'

    def get_success_url(self):
        return reverse_lazy('income_book_list') + f'?taxpayer={self.object.taxpayer.id}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Отримати вибраного платника податків або передати список платників
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                kwargs['taxpayer'] = Taxpayer.objects.get(id=taxpayer_id, user=self.request.user)
            except Taxpayer.DoesNotExist:
                kwargs['taxpayers'] = Taxpayer.objects.filter(user=self.request.user, is_active=True)
        else:
            kwargs['taxpayers'] = Taxpayer.objects.filter(user=self.request.user, is_active=True)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отримуємо фінансову операцію, якщо її ID передано
        finop_id = self.request.GET.get('finop')
        if finop_id:
            try:
                # Використовуємо тільки фінансові операції платників податків користувача
                taxpayers = Taxpayer.objects.filter(user=self.request.user)
                context['finop'] = Finop.objects.get(
                    id=finop_id,
                    taxpayer__in=taxpayers,
                    operation_type=OPERATION_TYPE_INCOME
                )
            except Finop.DoesNotExist:
                pass

        # Якщо немає конкретної фінансової операції, додаємо список останніх
        if 'finop' not in context:
            taxpayer_id = self.request.GET.get('taxpayer')
            if taxpayer_id:
                try:
                    taxpayer = Taxpayer.objects.get(id=taxpayer_id, user=self.request.user)
                    context['recent_finops'] = Finop.objects.filter(
                        taxpayer=taxpayer,
                        operation_type=OPERATION_TYPE_INCOME,
                        is_processed=False
                    ).order_by('-operation_date')[:10]
                except Taxpayer.DoesNotExist:
                    pass

        return context

    def form_valid(self, form):
        with transaction.atomic():
            # Зберігаємо запис
            response = super().form_valid(form)

            # Якщо є пов'язана фінансова операція, позначаємо її як оброблену
            finop = form.cleaned_data.get('finop')
            if finop:
                finop.is_processed = True
                finop.save()

            messages.success(self.request, _("Запис успішно створено"))
            return response

class IncomeRecordUpdateView(LoginRequiredMixin, UpdateView):
    """Редагування запису книги доходів"""
    model = IncomeRecord
    form_class = IncomeRecordForm
    template_name = 'income_book/income_record_form.html'

    def get_success_url(self):
        return reverse_lazy('income_book_list') + f'?taxpayer={self.object.taxpayer.id}'

    def get_queryset(self):
        # Обмежуємо доступ до записів тільки власним платникам податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user)
        return IncomeRecord.objects.filter(taxpayer__in=taxpayers)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['taxpayer'] = self.get_object().taxpayer
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Запис успішно оновлено"))
        return super().form_valid(form)

class IncomeRecordDeleteView(LoginRequiredMixin, DeleteView):
    """Видалення запису книги доходів"""
    model = IncomeRecord
    template_name = 'income_book/income_record_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('income_book_list') + f'?taxpayer={self.object.taxpayer.id}'

    def get_queryset(self):
        # Обмежуємо доступ до записів тільки власним платникам податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user)
        return IncomeRecord.objects.filter(taxpayer__in=taxpayers)

    def delete(self, request, *args, **kwargs):
        """Замість фізичного видалення, позначаємо запис як скасований"""
        self.object = self.get_object()
        success_url = self.get_success_url()

        self.object.cancel()
        messages.success(request, _("Запис успішно скасовано"))

        return redirect(success_url)

class CreateAdjustmentView(LoginRequiredMixin, UpdateView):
    """Створення коригування для існуючого запису"""
    model = IncomeRecord
    template_name = 'income_book/create_adjustment.html'
    fields = ['amount', 'description']

    def get_queryset(self):
        # Обмежуємо доступ до записів тільки власним платникам податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user)
        return IncomeRecord.objects.filter(taxpayer__in=taxpayers, status='active')

    def form_valid(self, form):
        original_record = self.get_object()
        new_amount = form.cleaned_data['amount']
        new_description = form.cleaned_data.get('description')

        # Створюємо коригувальний запис
        with transaction.atomic():
            adjustment = original_record.create_adjustment(new_amount, new_description)
            messages.success(self.request, _("Коригування успішно створено"))

            return redirect('income_record_detail', pk=adjustment.pk)

class FillFromFinopView(LoginRequiredMixin, DetailView):
    """Заповнення форми даними з фінансової операції"""
    model = Finop

    def get_queryset(self):
        # Обмежуємо доступ до фінансових операцій тільки власним платникам податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user)
        return Finop.objects.filter(taxpayer__in=taxpayers)

    def get(self, request, *args, **kwargs):
        finop = self.get_object()

        data = {
            'amount': finop.amount,
            'description': finop.description,
            'finop': finop.id,
            'date': finop.operation_date.strftime('%Y-%m-%d'),
            'document_number': f"Рах.№{finop.bank_operation_id}" if finop.bank_operation_id else f"Банк-{finop.id}"
        }

        return JsonResponse(data)