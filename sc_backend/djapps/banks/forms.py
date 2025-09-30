
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Bank, BankAccount


class BankForm(forms.ModelForm):
    """Форма для створення та редагування банку"""
    class Meta:
        model = Bank
        fields = ['name', 'ifi_mfo', 'bank_type', 'city', 'address',
                 'swift_code', 'swift_name', 'swift_address',
                 'corr_name', 'corr_address', 'corr_swift', 'corr_account']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'ifi_mfo': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_type': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'swift_code': forms.TextInput(attrs={'class': 'form-control'}),
            'swift_name': forms.TextInput(attrs={'class': 'form-control'}),
            'swift_address': forms.TextInput(attrs={'class': 'form-control'}),
            'corr_name': forms.TextInput(attrs={'class': 'form-control'}),
            'corr_address': forms.TextInput(attrs={'class': 'form-control'}),
            'corr_swift': forms.TextInput(attrs={'class': 'form-control'}),
            'corr_account': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BankAccountForm(forms.ModelForm):
    """Форма для створення та редагування банківського рахунку"""
    class Meta:
        model = BankAccount
        fields = ['acc_iban', 'bank', 'account_type', 'currency',
                 'account_status', 'is_main', 'is_default']
        widgets = {
            'acc_iban': forms.TextInput(attrs={'class': 'form-control'}),
            'bank': forms.Select(attrs={'class': 'form-select'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'account_status': forms.Select(attrs={'class': 'form-select'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.taxpayer = kwargs.pop('taxpayer', None)
        super().__init__(*args, **kwargs)

        # Фільтруємо список банків - показуємо тільки активні
        self.fields['bank'].queryset = Bank.objects.filter(is_deleted=False)