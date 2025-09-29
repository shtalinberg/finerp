from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from taxpayers.models import Taxpayer

from .forms import BankAccountForm, BankForm
from .models import Bank, BankAccount


class BankListView(LoginRequiredMixin, ListView):
    """Перегляд списку банків"""

    model = Bank
    template_name = 'banks/bank_list.html'
    context_object_name = 'banks'

    def get_queryset(self):
        return Bank.objects.filter(is_deleted=False)


class BankDetailView(LoginRequiredMixin, DetailView):
    """Деталізований перегляд банку"""

    model = Bank
    template_name = 'banks/bank_detail.html'
    context_object_name = 'bank'

    def get_queryset(self):
        return Bank.objects.filter(is_deleted=False)


class BankCreateView(LoginRequiredMixin, CreateView):
    """Створення нового банку"""

    model = Bank
    form_class = BankForm
    template_name = 'banks/bank_form.html'
    success_url = reverse_lazy('bank_list')

    def form_valid(self, form):
        messages.success(self.request, "Банк успішно створено")
        return super().form_valid(form)


class BankUpdateView(LoginRequiredMixin, UpdateView):
    """Редагування банку"""

    model = Bank
    form_class = BankForm
    template_name = 'banks/bank_form.html'
    success_url = reverse_lazy('bank_list')

    def get_queryset(self):
        return Bank.objects.filter(is_deleted=False)

    def form_valid(self, form):
        messages.success(self.request, "Банк успішно оновлено")
        return super().form_valid(form)


class BankAccountListView(LoginRequiredMixin, ListView):
    """Перегляд списку банківських рахунків"""

    model = BankAccount
    template_name = 'banks/bank_account_list.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        # Отримуємо вибраного платника податків
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                taxpayer = Taxpayer.objects.get(id=taxpayer_id, user=self.request.user)
            except Taxpayer.DoesNotExist:
                # Беремо першого доступного платника податків
                taxpayers = Taxpayer.objects.filter(
                    user=self.request.user, is_active=True
                )
                taxpayer = taxpayers.first() if taxpayers.exists() else None
        else:
            # Беремо першого доступного платника податків
            taxpayers = Taxpayer.objects.filter(user=self.request.user, is_active=True)
            taxpayer = taxpayers.first() if taxpayers.exists() else None

        if not taxpayer:
            return BankAccount.objects.none()

        return BankAccount.objects.filter(is_deleted=False, bank__is_deleted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отримуємо платників податків користувача
        taxpayers = Taxpayer.objects.filter(user=self.request.user, is_active=True)
        context['taxpayers'] = taxpayers

        # Отримуємо вибраного платника податків
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                context['selected_taxpayer'] = Taxpayer.objects.get(
                    id=taxpayer_id, user=self.request.user
                )
            except Taxpayer.DoesNotExist:
                context['selected_taxpayer'] = (
                    taxpayers.first() if taxpayers.exists() else None
                )
        else:
            context['selected_taxpayer'] = (
                taxpayers.first() if taxpayers.exists() else None
            )

        return context


class BankAccountCreateView(LoginRequiredMixin, CreateView):
    """Створення нового банківського рахунку"""

    model = BankAccount
    form_class = BankAccountForm
    template_name = 'banks/bank_account_form.html'
    success_url = reverse_lazy('bank_account_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Отримуємо вибраного платника податків
        taxpayer_id = self.request.GET.get('taxpayer')
        if taxpayer_id:
            try:
                kwargs['taxpayer'] = Taxpayer.objects.get(
                    id=taxpayer_id, user=self.request.user
                )
            except Taxpayer.DoesNotExist:
                pass

        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Банківський рахунок успішно створено")
        return super().form_valid(form)


class BankAccountUpdateView(LoginRequiredMixin, UpdateView):
    """Редагування банківського рахунку"""

    model = BankAccount
    form_class = BankAccountForm
    template_name = 'banks/bank_account_form.html'
    success_url = reverse_lazy('bank_account_list')

    def get_queryset(self):
        return BankAccount.objects.filter(is_deleted=False)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Отримуємо платника податків, якому належить рахунок
        # В цьому випадку цей код не потрібен, але залишимо для цілісності
        # Поки що рахунки не прив'язані до платників податків

        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Банківський рахунок успішно оновлено")
        return super().form_valid(form)


class BankDeleteView(LoginRequiredMixin, DeleteView):
    """Видалення банку"""

    model = Bank
    success_url = reverse_lazy('bank_list')

    def delete(self, request, *args, **kwargs):
        bank = self.get_object()
        # Soft delete замість фізичного видалення
        bank.is_deleted = True
        bank.save()

        messages.success(request, f"Банк {bank.name} успішно видалено")
        return redirect(self.success_url)


class BankAccountDeleteView(LoginRequiredMixin, DeleteView):
    """Видалення банківського рахунку"""

    model = BankAccount
    success_url = reverse_lazy('bank_account_list')

    def delete(self, request, *args, **kwargs):
        account = self.get_object()
        # Soft delete замість фізичного видалення
        account.is_deleted = True
        account.save()

        messages.success(request, f"Рахунок {account.acc_iban} успішно видалено")
        return redirect(self.success_url)
