
from django import forms
from django.utils.translation import gettext_lazy as _

from .constants import (
    TAX_GROUP_1,
    TAX_GROUP_2,
    TAX_GROUP_3,
    TAX_RATE_1_CHOICES,
    TAX_RATE_2_CHOICES,
    TAX_RATE_3_CHOICES,
    TAX_SYSTEM_SIMPLIFIED,
)
from .models import Address, Taxpayer, TaxpayerDocument, TaxpayerSettings


class AddressForm(forms.ModelForm):
    """Форма для адреси"""
    class Meta:
        model = Address
        fields = ['street', 'house_number', 'apartment', 'city', 'region', 'postal_code']
        widgets = {
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'house_number': forms.TextInput(attrs={'class': 'form-control'}),
            'apartment': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'})
        }

class TaxpayerForm(forms.ModelForm):
    """Форма для платника податків (ФОП)"""

    # Замість вибору податкової ставки через choices, використовуємо динамічний вибір
    tax_rate = forms.FloatField(
        label=_("Ставка податку"),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    class Meta:
        model = Taxpayer
        fields = [
            'full_name', 'tax_number', 'registration_number', 'registration_date',
            'tax_system', 'tax_group', 'tax_rate', 'esv_rate',
            'is_vat_payer', 'vat_registration_number', 'is_active'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tax_system': forms.Select(attrs={'class': 'form-select', 'id': 'tax_system'}),
            'tax_group': forms.Select(attrs={'class': 'form-select', 'id': 'tax_group'}),
            'esv_rate': forms.Select(attrs={'class': 'form-select'}),
            'vat_registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_vat_payer': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Встановлюємо початкові варіанти для ставки податку
        self.set_tax_rate_choices()

        # Додаємо атрибути для JavaScript
        self.fields['tax_system'].widget.attrs.update({
            'onchange': 'updateTaxGroupVisibility(); updateTaxRateChoices();'
        })
        self.fields['tax_group'].widget.attrs.update({
            'onchange': 'updateTaxRateChoices();'
        })

    def set_tax_rate_choices(self):
        """Встановлює варіанти для ставки податку в залежності від групи та системи"""
        instance = self.instance

        if not instance.pk:  # Новий об'єкт
            tax_system = self.initial.get('tax_system', TAX_SYSTEM_SIMPLIFIED)
            tax_group = self.initial.get('tax_group', TAX_GROUP_3)
        else:  # Існуючий об'єкт
            tax_system = instance.tax_system
            tax_group = instance.tax_group

        if tax_system == TAX_SYSTEM_SIMPLIFIED:
            if tax_group == TAX_GROUP_3:
                choices = list(TAX_RATE_3_CHOICES)
            elif tax_group == TAX_GROUP_2:
                choices = list(TAX_RATE_2_CHOICES)
            elif tax_group == TAX_GROUP_1:
                choices = list(TAX_RATE_1_CHOICES)
            else:
                choices = [(5.0, _("5%"))]
        else:  # Загальна система
            choices = [(18.0, _("18%"))]

        self.fields['tax_rate'].widget.choices = choices

        # Якщо поточне значення не в списку варіантів, встановлюємо перше значення
        current_value = self.initial.get('tax_rate', None)
        if not current_value or current_value not in [choice[0] for choice in choices]:
            self.initial['tax_rate'] = choices[0][0]

class TaxpayerSettingsForm(forms.ModelForm):
    """Форма для налаштувань платника податків"""
    class Meta:
        model = TaxpayerSettings
        fields = [
            'auto_categorize', 'auto_process_income',
            'tax_reminder_days', 'sync_frequency_days',
            'notes'
        ]
        widgets = {
            'auto_categorize': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_process_income': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tax_reminder_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '30'}),
            'sync_frequency_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '30'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'})
        }

class TaxpayerDocumentForm(forms.ModelForm):
    """Форма для документів платника податків"""
    class Meta:
        model = TaxpayerDocument
        fields = [
            'title', 'document_type', 'file',
            'issue_date', 'expiry_date', 'notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'})
        }

    def __init__(self, *args, **kwargs):
        self.taxpayer = kwargs.pop('taxpayer', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.taxpayer:
            instance.taxpayer = self.taxpayer
        if commit:
            instance.save()
        return instance