
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import AddressForm, TaxpayerDocumentForm, TaxpayerForm, TaxpayerSettingsForm
from .models import Taxpayer, TaxpayerDocument, TaxpayerSettings


class TaxpayerListView(LoginRequiredMixin, ListView):
    """Список платників податків"""
    model = Taxpayer
    template_name = 'taxpayers/taxpayer_list.html'
    context_object_name = 'taxpayers'

    def get_queryset(self):
        return Taxpayer.objects.filter(user=self.request.user).select_related('address')

class TaxpayerDetailView(LoginRequiredMixin, DetailView):
    """Детальна інформація про платника податків"""
    model = Taxpayer
    template_name = 'taxpayers/taxpayer_detail.html'
    context_object_name = 'taxpayer'

    def get_queryset(self):
        return Taxpayer.objects.filter(user=self.request.user).select_related('address')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Додаємо документи
        context['documents'] = self.object.documents.all().order_by('-created_at')

        # Отримуємо налаштування
        try:
            context['settings'] = self.object.settings
        except TaxpayerSettings.DoesNotExist:
            # Якщо налаштувань немає, створюємо їх
            context['settings'] = TaxpayerSettings.objects.create(taxpayer=self.object)

        # Додаємо інформацію про фінансові операції
        if hasattr(self.object, 'finops'):
            # Отримуємо статистику за доходами/витратами
            income_count = self.object.finops.filter(operation_type='income').count()
            expense_count = self.object.finops.filter(operation_type='expense').count()

            context['income_count'] = income_count
            context['expense_count'] = expense_count

        # Додаємо інформацію про записи книги доходів
        if hasattr(self.object, 'income_records'):
            context['income_records_count'] = self.object.income_records.count()

        # Додаємо інформацію про податкові звіти
        if hasattr(self.object, 'tax_reports'):
            context['tax_reports_count'] = self.object.tax_reports.count()

        return context

class TaxpayerCreateView(LoginRequiredMixin, CreateView):
    """Створення нового платника податків"""
    model = Taxpayer
    form_class = TaxpayerForm
    template_name = 'taxpayers/taxpayer_form.html'
    success_url = reverse_lazy('taxpayer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['address_form'] = AddressForm(self.request.POST)
        else:
            context['address_form'] = AddressForm()
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        address_form = context['address_form']

        if address_form.is_valid():
            # Зберігаємо адресу
            address = address_form.save()

            # Зберігаємо платника податків
            taxpayer = form.save(commit=False)
            taxpayer.user = self.request.user
            taxpayer.address = address
            taxpayer.save()

            # Створюємо налаштування
            TaxpayerSettings.objects.create(taxpayer=taxpayer)

            messages.success(self.request, _("Платника податків успішно створено"))
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class TaxpayerUpdateView(LoginRequiredMixin, UpdateView):
    """Редагування платника податків"""
    model = Taxpayer
    form_class = TaxpayerForm
    template_name = 'taxpayers/taxpayer_form.html'
    success_url = reverse_lazy('taxpayer_list')

    def get_queryset(self):
        return Taxpayer.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['address_form'] = AddressForm(self.request.POST, instance=self.object.address)
        else:
            context['address_form'] = AddressForm(instance=self.object.address)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        address_form = context['address_form']

        if address_form.is_valid():
            # Зберігаємо адресу
            address = address_form.save()

            # Зберігаємо платника податків
            taxpayer = form.save(commit=False)
            taxpayer.address = address
            taxpayer.save()

            messages.success(self.request, _("Платника податків успішно оновлено"))
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class TaxpayerDeleteView(LoginRequiredMixin, DeleteView):
    """Видалення платника податків"""
    model = Taxpayer
    template_name = 'taxpayers/taxpayer_confirm_delete.html'
    success_url = reverse_lazy('taxpayer_list')

    def get_queryset(self):
        return Taxpayer.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Перевіряємо, чи є пов'язані дані
        has_finops = hasattr(self.object, 'finops') and self.object.finops.exists()
        has_income_records = hasattr(self.object, 'income_records') and self.object.income_records.exists()
        has_tax_reports = hasattr(self.object, 'tax_reports') and self.object.tax_reports.exists()

        if has_finops or has_income_records or has_tax_reports:
            # Якщо є пов'язані дані, просто деактивуємо
            self.object.is_active = False
            self.object.save()

            messages.warning(
                request,
                _("Платника податків було деактивовано, а не видалено, оскільки з ним пов'язані дані")
            )
        else:
            # Якщо немає пов'язаних даних, видаляємо
            address = self.object.address
            self.object.delete()
            address.delete()

            messages.success(request, _("Платника податків успішно видалено"))

        return redirect(self.success_url)

class TaxpayerSettingsUpdateView(LoginRequiredMixin, UpdateView):
    """Оновлення налаштувань платника податків"""
    model = TaxpayerSettings
    form_class = TaxpayerSettingsForm
    template_name = 'taxpayers/taxpayer_settings_form.html'

    def get_object(self, queryset=None):
        # Отримуємо платника податків
        taxpayer = get_object_or_404(Taxpayer, pk=self.kwargs['taxpayer_id'], user=self.request.user)

        # Отримуємо або створюємо налаштування
        settings, created = TaxpayerSettings.objects.get_or_create(taxpayer=taxpayer)

        return settings

    def get_success_url(self):
        return reverse_lazy('taxpayer_detail', kwargs={'pk': self.kwargs['taxpayer_id']})

    def form_valid(self, form):
        messages.success(self.request, _("Налаштування успішно оновлено"))
        return super().form_valid(form)

class TaxpayerDocumentCreateView(LoginRequiredMixin, CreateView):
    """Додавання документа платника податків"""
    model = TaxpayerDocument
    form_class = TaxpayerDocumentForm
    template_name = 'taxpayers/taxpayer_document_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['taxpayer'] = get_object_or_404(Taxpayer, pk=self.kwargs['taxpayer_id'], user=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer'] = get_object_or_404(Taxpayer, pk=self.kwargs['taxpayer_id'], user=self.request.user)
        return context

    def get_success_url(self):
        return reverse_lazy('taxpayer_detail', kwargs={'pk': self.kwargs['taxpayer_id']})

    def form_valid(self, form):
        messages.success(self.request, _("Документ успішно додано"))
        return super().form_valid(form)

class TaxpayerDocumentDeleteView(LoginRequiredMixin, DeleteView):
    """Видалення документа платника податків"""
    model = TaxpayerDocument
    template_name = 'taxpayers/taxpayer_document_confirm_delete.html'

    def get_queryset(self):
        # Обмежуємо доступ до документів платників податків користувача
        return TaxpayerDocument.objects.filter(taxpayer__user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('taxpayer_detail', kwargs={'pk': self.object.taxpayer.pk})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        # Видаляємо файл
        if self.object.file:
            self.object.file.delete()

        self.object.delete()
        messages.success(request, _("Документ успішно видалено"))

        return redirect(success_url)

def get_tax_rate_choices(request):
    """AJAX запит для отримання варіантів ставки податку"""
    tax_system = request.GET.get('tax_system')
    tax_group = request.GET.get('tax_group')

    if not tax_system or (tax_system == 'simplified' and not tax_group):
        return JsonResponse({'choices': []})

    choices = []

    if tax_system == 'simplified':
        tax_group = int(tax_group)
        if tax_group == 3:
            from .constants import TAX_RATE_3_CHOICES
            choices = [{'value': rate, 'label': label} for rate, label in TAX_RATE_3_CHOICES]
        elif tax_group == 2:
            from .constants import TAX_RATE_2_CHOICES
            choices = [{'value': rate, 'label': label} for rate, label in TAX_RATE_2_CHOICES]
        elif tax_group == 1:
            from .constants import TAX_RATE_1_CHOICES
            choices = [{'value': rate, 'label': label} for rate, label in TAX_RATE_1_CHOICES]
    else:  # Загальна система
        choices = [{'value': 18.0, 'label': '18%'}]

    return JsonResponse({'choices': choices})