
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from finops.constants import OPERATION_TYPE_INCOME
from finops.models import Finop
from taxpayers.models import Taxpayer

from .models import IncomeRecord


class IncomeRecordForm(forms.ModelForm):
    """Форма для створення/редагування записів книги доходів"""

    taxpayer = forms.ModelChoiceField(
        queryset=Taxpayer.objects.none(),
        required=True,
        label=_("Платник податків"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    finop = forms.ModelChoiceField(
        queryset=Finop.objects.none(),
        required=False,
        label=_("Пов'язана фінансова операція"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = IncomeRecord
        fields = ['taxpayer', 'date', 'document_number', 'amount', 'income_type', 'description', 'notes', 'finop']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'income_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        # Отримуємо параметри платника податків
        taxpayer = kwargs.pop('taxpayer', None)
        taxpayers = kwargs.pop('taxpayers', None)

        super().__init__(*args, **kwargs)

        # Налаштовуємо поле вибору платника податків
        if taxpayer:
            self.fields['taxpayer'].queryset = Taxpayer.objects.filter(pk=taxpayer.pk)
            self.fields['taxpayer'].initial = taxpayer
            self.fields['taxpayer'].widget.attrs['disabled'] = 'disabled'
            self.fields['finop'].queryset = Finop.objects.filter(
                taxpayer=taxpayer,
                operation_type=OPERATION_TYPE_INCOME,
                is_processed=False
            ).order_by('-operation_date')
        elif taxpayers:
            self.fields['taxpayer'].queryset = taxpayers

            # Якщо є лише один платник податків, вибираємо його за замовчуванням
            if taxpayers.count() == 1:
                self.fields['taxpayer'].initial = taxpayers.first()
        else:
            # В іншому випадку вимикаємо поле вибору фінансової операції
            self.fields['finop'].widget.attrs['disabled'] = 'disabled'

        # Встановлюємо поточну дату за замовчуванням, якщо це новий запис
        if not self.instance.pk and not self.initial.get('date'):
            self.initial['date'] = timezone.now().date()

    def clean_taxpayer(self):
        # Забезпечуємо збереження значення, навіть якщо поле disabled
        if self.fields['taxpayer'].widget.attrs.get('disabled') == 'disabled' and 'taxpayer' in self.data:
            return Taxpayer.objects.get(pk=self.data.get('taxpayer'))
        return self.cleaned_data['taxpayer']

    def clean(self):
        cleaned_data = super().clean()

        # Якщо вибрана фінансова операція, оновлюємо суму та опис за нею
        finop = cleaned_data.get('finop')
        if finop and not self.instance.pk:  # Лише для нових записів
            cleaned_data['amount'] = finop.amount
            if not cleaned_data.get('description'):
                cleaned_data['description'] = finop.description

        return cleaned_data