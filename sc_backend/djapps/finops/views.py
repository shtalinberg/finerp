
import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from banks.models import BankAccount
from monobank_api.services import MonoBankSyncService
from privat24api.services import PrivatBankSyncService
from taxpayers.models import Taxpayer

from .constants import (
    OPERATION_TYPE_EXPENSE,
    OPERATION_TYPE_INCOME,
    PROCESSING_STATUS_NEW,
    SOURCE_MONOBANK,
    SOURCE_PRIVATBANK,
)
from .filters import FinopFilter
from .forms import FinopFilterForm, FinopForm
from .models import Category, Finop


class FinopListView(LoginRequiredMixin, ListView):
    """Перегляд списку фінансових операцій з фільтрацією"""
    model = Finop
    template_name = 'finops/finop_list.html'
    context_object_name = 'finops'
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
            return Finop.objects.none()

        queryset = Finop.objects.filter(taxpayer=taxpayer)

        # Створюємо фільтр
        self.filterset = FinopFilter(
            self.request.GET,
            queryset=queryset,
            taxpayer=taxpayer
        )

        return self.filterset.qs.select_related('bank_account')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Додаємо фільтр
        context['filterset'] = self.filterset

        # Отримуємо вибраного платника податків
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                context['selected_taxpayer'] = Taxpayer.objects.get(id=taxpayer_id, user=self.request.user)
            except Taxpayer.DoesNotExist:
                taxpayers = Taxpayer.objects.filter(user=self.request.user, is_active=True)
                context['selected_taxpayer'] = taxpayers.first() if taxpayers.exists() else None
        else:
            taxpayers = Taxpayer.objects.filter(user=self.request.user, is_active=True)
            context['selected_taxpayer'] = taxpayers.first() if taxpayers.exists() else None

        # Додаємо банківські рахунки для вибраного платника податків
        if context['selected_taxpayer']:
            context['bank_accounts'] = BankAccount.objects.filter(is_deleted=False)

            # Додаємо підсумки за типами операцій
            finops = self.filterset.qs

            # Загальна сума доходів
            total_income = finops.filter(operation_type=OPERATION_TYPE_INCOME).aggregate(
                total=Sum('amount_uah')
            )['total'] or Decimal('0')

            # Загальна сума витрат
            total_expense = finops.filter(operation_type=OPERATION_TYPE_EXPENSE).aggregate(
                total=Sum('amount_uah')
            )['total'] or Decimal('0')

            # Баланс
            balance = total_income - total_expense

            context['total_income'] = total_income
            context['total_expense'] = total_expense
            context['balance'] = balance

            # Додаємо кількість необроблених операцій
            context['unprocessed_count'] = Finop.objects.filter(
                taxpayer=context['selected_taxpayer'],
                operation_type=OPERATION_TYPE_INCOME,
                processing_status=PROCESSING_STATUS_NEW
            ).count()

            # Форма фільтрації
            context['filter_form'] = FinopFilterForm(
                self.request.GET,
                taxpayer=context['selected_taxpayer']
            )

        return context

class FinopDetailView(LoginRequiredMixin, DetailView):
    """Детальний перегляд фінансової операції"""
    model = Finop
    template_name = 'finops/finop_detail.html'
    context_object_name = 'finop'

    def get_queryset(self):
        # Обмежуємо доступ до операцій тільки платників податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user)
        return Finop.objects.filter(taxpayer__in=taxpayers).select_related('taxpayer', 'bank_account')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Додаємо інформацію про теги
        if self.object.tags:
            context['tags_list'] = [tag.strip() for tag in self.object.tags.split(',')]

        # Додаємо інформацію про пов'язані записи книги доходів
        if hasattr(self.object, 'income_records'):
            context['income_records'] = self.object.income_records.all()

        return context

class FinopCreateView(LoginRequiredMixin, CreateView):
    """Створення нової фінансової операції"""
    model = Finop
    form_class = FinopForm
    template_name = 'finops/finop_form.html'

    def get_success_url(self):
        return reverse_lazy('finop_list') + f'?taxpayer={self.object.taxpayer.id}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Отримуємо платника податків
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                kwargs['taxpayer'] = Taxpayer.objects.get(id=taxpayer_id, user=self.request.user)
            except Taxpayer.DoesNotExist:
                kwargs['taxpayers'] = Taxpayer.objects.filter(user=self.request.user, is_active=True)
        else:
            kwargs['taxpayers'] = Taxpayer.objects.filter(user=self.request.user, is_active=True)

        return kwargs

    def form_valid(self, form):
        # Встановлюємо джерело як ручне введення
        form.instance.source = 'manual'

        messages.success(self.request, _("Фінансову операцію успішно створено"))
        return super().form_valid(form)

class FinopUpdateView(LoginRequiredMixin, UpdateView):
    """Редагування фінансової операції"""
    model = Finop
    form_class = FinopForm
    template_name = 'finops/finop_form.html'

    def get_success_url(self):
        return reverse_lazy('finop_list') + f'?taxpayer={self.object.taxpayer.id}'

    def get_queryset(self):
        # Обмежуємо доступ до операцій тільки платників податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user)
        return Finop.objects.filter(taxpayer__in=taxpayers)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['taxpayer'] = self.get_object().taxpayer
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Фінансову операцію успішно оновлено"))
        return super().form_valid(form)

class FinopDeleteView(LoginRequiredMixin, DeleteView):
    """Видалення фінансової операції"""
    model = Finop
    template_name = 'finops/finop_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('finop_list') + f'?taxpayer={self.object.taxpayer.id}'

    def get_queryset(self):
        # Обмежуємо доступ до операцій тільки платників податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user)
        return Finop.objects.filter(taxpayer__in=taxpayers)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        # Перевіряємо, чи не пов'язана операція з записом книги доходів
        if hasattr(self.object, 'income_records') and self.object.income_records.exists():
            messages.error(request, _("Неможливо видалити операцію, оскільки вона пов'язана з записами книги доходів"))
            return redirect('finop_detail', pk=self.object.pk)

        self.object.delete()
        messages.success(request, _("Фінансову операцію успішно видалено"))

        return redirect(success_url)

class SyncFinopsView(LoginRequiredMixin, TemplateView):
    """Перегляд для синхронізації фінансових операцій з банків"""
    template_name = 'finops/sync_finops.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отримуємо платників податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user, is_active=True)
        context['taxpayers'] = taxpayers

        # Отримуємо вибраного платника податків
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                context['selected_taxpayer'] = Taxpayer.objects.get(id=taxpayer_id, user=self.request.user)
            except Taxpayer.DoesNotExist:
                context['selected_taxpayer'] = taxpayers.first() if taxpayers.exists() else None
        else:
            context['selected_taxpayer'] = taxpayers.first() if taxpayers.exists() else None

        # Отримуємо банківські рахунки для вибраного платника податків
        if context['selected_taxpayer']:
            context['bank_accounts'] = BankAccount.objects.filter(is_deleted=False)

            # Отримуємо джерело
            source = self.request.GET.get('source')
            if source in [SOURCE_PRIVATBANK, SOURCE_MONOBANK]:
                context['source'] = source

                # Фільтруємо рахунки за належністю до банку
                if source == SOURCE_PRIVATBANK:
                    context['bank_accounts'] = context['bank_accounts'].filter(
                        bank__name__icontains='приват'
                    )
                elif source == SOURCE_MONOBANK:
                    context['bank_accounts'] = context['bank_accounts'].filter(
                        bank__name__icontains='моно'
                    )

        # Дати за замовчуванням - останні 30 днів
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=30)

        context['start_date'] = start_date
        context['end_date'] = end_date

        return context

    def post(self, request, *args, **kwargs):
        """Обробка запиту на синхронізацію"""
        taxpayer_id = request.POST.get('taxpayer')
        account_id = request.POST.get('account')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        source = request.POST.get('source')

        if not all([taxpayer_id, account_id, start_date, end_date, source]):
            return HttpResponse("Відсутні обов'язкові параметри", status=400)

        try:
            taxpayer = Taxpayer.objects.get(id=taxpayer_id, user=request.user)
            bank_account = BankAccount.objects.get(id=account_id)
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        except (Taxpayer.DoesNotExist, BankAccount.DoesNotExist, ValueError) as e:
            return HttpResponse(f"Неправильні параметри: {str(e)}", status=400)

        # Отримуємо відповідний сервіс синхронізації за типом банку
        if source == SOURCE_PRIVATBANK:
            sync_service = PrivatBankSyncService()
            new_count, updated_count = sync_service.sync_finops(
                taxpayer,
                bank_account,
                start_date,
                end_date
            )
        elif source == SOURCE_MONOBANK:
            sync_service = MonoBankSyncService()
            new_count, updated_count = sync_service.sync_finops(
                taxpayer,
                bank_account,
                start_date,
                end_date
            )
        else:
            return HttpResponse("Джерело не підтримується", status=400)

        if request.headers.get('HX-Request'):
            # HTMX запит - повертаємо частковий вміст
            context = {
                'success': True,
                'new_count': new_count,
                'updated_count': updated_count,
                'account': bank_account,
                'taxpayer': taxpayer,
                'source': source
            }
            return render(request, 'finops/partials/sync_result.html', context)
        else:
            # Звичайне подання форми - перенаправлення на список операцій
            messages.success(
                request,
                f"Синхронізовано {new_count} нових та {updated_count} існуючих операцій"
            )
            return redirect('finop_list') + f'?taxpayer={taxpayer.id}'

class ProcessFinopView(LoginRequiredMixin, DetailView):
    """Перегляд для обробки фінансової операції та створення запису про дохід"""
    model = Finop
    template_name = 'finops/process_finop.html'
    context_object_name = 'finop'

    def get_queryset(self):
        # Обмежуємо доступ до операцій тільки платників податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user)
        return Finop.objects.filter(
            taxpayer__in=taxpayers,
            operation_type=OPERATION_TYPE_INCOME,
            processing_status=PROCESSING_STATUS_NEW
        )

    def post(self, request, *args, **kwargs):
        """Обробка запиту на створення запису про дохід"""
        finop = self.get_object()

        # Імпортуємо тут, щоб уникнути циклічних імпортів
        from income_book.forms import IncomeRecordForm

        # Якщо "пропустити", просто позначаємо як оброблено
        if 'skip' in request.POST:
            finop.mark_as_ignored()

            if request.headers.get('HX-Request'):
                messages.success(request, _("Операцію пропущено"))
                return HttpResponse(status=200, headers={'HX-Refresh': 'true'})
            else:
                return redirect('finop_list') + f'?taxpayer={finop.taxpayer.id}'

        # Створюємо форму для запису про дохід
        form = IncomeRecordForm(request.POST)
        form.instance.taxpayer = finop.taxpayer
        form.instance.finop = finop

        if form.is_valid():
            with transaction.atomic():
                # Зберігаємо запис про дохід
                income_record = form.save()

                # Позначаємо операцію як оброблену
                finop.mark_as_processed()

                messages.success(request, _("Запис про дохід успішно створено"))

                if request.headers.get('HX-Request'):
                    return render(request, 'income_book/partials/process_success.html', {
                        'income_record': income_record,
                        'finop': finop
                    })
                else:
                    return redirect('income_record_detail', pk=income_record.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class CategoryListView(LoginRequiredMixin, ListView):
    """Перегляд списку категорій"""
    model = Category
    template_name = 'finops/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Отримуємо вибраного платника податків
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                taxpayer = Taxpayer.objects.get(id=taxpayer_id, user=self.request.user)
            except Taxpayer.DoesNotExist:
                # Беремо першого доступного платника податків
                taxpayers = Taxpayer.objects.filter(user=self.request.user, is_active=True)
                taxpayer = taxpayers.first