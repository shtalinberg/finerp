
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from banks.models import BankAccount
from taxpayers.models import Taxpayer

from .constants import (
    EXPENSE_CATEGORIES,
    EXPENSE_CATEGORY_OTHER_EXPENSE,
    INCOME_CATEGORIES,
    INCOME_CATEGORY_OTHER_INCOME,
    OPERATION_TYPES,
)
from .models import Category, Finop


class FinopForm(forms.ModelForm):
    """Форма для створення/редагування фінансових операцій"""

    taxpayer = forms.ModelChoiceField(
        queryset=Taxpayer.objects.none(),
        required=True,
        label=_("Платник податків"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    bank_account = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        required=True,
        label=_("Банківський рахунок"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    tags = forms.CharField(
        required=False,
        label=_("Теги"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'data-role': 'tagsinput'}),
        help_text=_("Введіть теги через кому")
    )

    class Meta:
        model = Finop
        fields = [
            'taxpayer', 'bank_account', 'operation_date', 'amount', 'amount_uah',
            'description', 'operation_type', 'operation_status',
            'income_category', 'expense_category', 'is_taxable',
            'sender_name', 'sender_account', 'recipient_name', 'recipient_account',
            'notes', 'tags', 'reference'
        ]
        widgets = {
            'operation_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amount_uah': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'operation_type': forms.Select(attrs={'class': 'form-select', 'id': 'operation_type'}),
            'operation_status': forms.Select(attrs={'class': 'form-select'}),
            'income_category': forms.Select(attrs={'class': 'form-select', 'id': 'income_category'}),
            'expense_category': forms.Select(attrs={'class': 'form-select', 'id': 'expense_category'}),
            'is_taxable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sender_name': forms.TextInput(attrs={'class': 'form-control'}),
            'sender_account': forms.TextInput(attrs={'class': 'form-control'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'recipient_account': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'reference': forms.TextInput(attrs={'class': 'form-control'})
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
            self.fields['bank_account'].queryset = BankAccount.objects.filter(is_deleted=False)
        elif taxpayers:
            self.fields['taxpayer'].queryset = taxpayers
            self.fields['bank_account'].queryset = BankAccount.objects.filter(is_deleted=False)

            # Якщо є лише один платник податків, вибираємо його за замовчуванням
            if taxpayers.count() == 1:
                self.fields['taxpayer'].initial = taxpayers.first()
        else:
            # В іншому випадку обмежуємо вибір банківських рахунків
            self.fields['bank_account'].queryset = BankAccount.objects.filter(is_deleted=False)

        # Встановлюємо поточну дату/час за замовчуванням, якщо це новий запис
        if not self.instance.pk and not self.initial.get('operation_date'):
            self.initial['operation_date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

        # Якщо це наявний запис, заповнюємо поле тегів
        if self.instance.pk and self.instance.tags:
            self.initial['tags'] = self.instance.tags

    def clean_taxpayer(self):
        # Забезпечуємо збереження значення, навіть якщо поле disabled
        if self.fields['taxpayer'].widget.attrs.get('disabled') == 'disabled' and 'taxpayer' in self.data:
            return Taxpayer.objects.get(pk=self.data.get('taxpayer'))
        return self.cleaned_data['taxpayer']

    def clean(self):
        cleaned_data = super().clean()
        operation_type = cleaned_data.get('operation_type')

        # Перевіряємо категорії в залежності від типу операції
        if operation_type == 'income':
            cleaned_data['expense_category'] = None
            if not cleaned_data.get('income_category'):
                cleaned_data['income_category'] = INCOME_CATEGORY_OTHER_INCOME
        elif operation_type == 'expense':
            cleaned_data['income_category'] = None
            if not cleaned_data.get('expense_category'):
                cleaned_data['expense_category'] = EXPENSE_CATEGORY_OTHER_EXPENSE
        else:
            cleaned_data['income_category'] = None
            cleaned_data['expense_category'] = None

        return cleaned_data

class CategoryForm(forms.ModelForm):
    """Форма для створення/редагування категорій"""

    taxpayer = forms.ModelChoiceField(
        queryset=Taxpayer.objects.none(),
        required=True,
        label=_("Платник податків"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Category
        fields = ['taxpayer', 'name', 'category_type', 'description', 'is_default', 'is_active', 'order', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-select color-select'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'})
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
        elif taxpayers:
            self.fields['taxpayer'].queryset = taxpayers

            # Якщо є лише один платник податків, вибираємо його за замовчуванням
            if taxpayers.count() == 1:
                self.fields['taxpayer'].initial = taxpayers.first()

        # Додаємо кольори
        self.fields['color'].widget.choices = [
            ('primary', _('Синій')),
            ('secondary', _('Сірий')),
            ('success', _('Зелений')),
            ('danger', _('Червоний')),
            ('warning', _('Жовтий')),
            ('info', _('Блакитний')),
            ('dark', _('Темний')),
            ('light', _('Світлий'))
        ]

    def clean_taxpayer(self):
        # Забезпечуємо збереження значення, навіть якщо поле disabled
        if self.fields['taxpayer'].widget.attrs.get('disabled') == 'disabled' and 'taxpayer' in self.data:
            return Taxpayer.objects.get(pk=self.data.get('taxpayer'))
        return self.cleaned_data['taxpayer']

class FinopImportForm(forms.Form):
    """Форма для імпорту фінансових операцій з файлу"""

    taxpayer = forms.ModelChoiceField(
        queryset=Taxpayer.objects.none(),
        required=True,
        label=_("Платник податків"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    bank_account = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        required=True,
        label=_("Банківський рахунок"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    file = forms.FileField(
        label=_("Файл"),
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    file_format = forms.ChoiceField(
        label=_("Формат файлу"),
        choices=[
            ('csv', _('CSV')),
            ('xlsx', _('Excel')),
            ('qif', _('QIF (Quicken)'))
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    date_format = forms.ChoiceField(
        label=_("Формат дати"),
        choices=[
            ('dmy', _('ДД.ММ.РРРР')),
            ('mdy', _('ММ.ДД.РРРР')),
            ('ymd', _('РРРР-ММ-ДД'))
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        # Отримуємо параметри користувача
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        # Налаштовуємо поля вибору платника податків та банківського рахунку
        if user:
            self.fields['taxpayer'].queryset = Taxpayer.objects.filter(user=user)
            self.fields['bank_account'].queryset = BankAccount.objects.filter(is_deleted=False)
        else:
            self.fields['taxpayer'].queryset = Taxpayer.objects.none()
            self.fields['bank_account'].queryset = BankAccount.objects.none()

class FinopFilterForm(forms.Form):
    """Форма для фільтрації фінансових операцій"""

    date_from = forms.DateField(
        required=False,
        label=_("З дати"),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    date_to = forms.DateField(
        required=False,
        label=_("До дати"),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    operation_type = forms.ChoiceField(
        required=False,
        label=_("Тип операції"),
        choices=[('', _('Всі'))] + list(OPERATION_TYPES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    bank_account = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        required=False,
        label=_("Банківський рахунок"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    amount_min = forms.DecimalField(
        required=False,
        label=_("Мінімальна сума"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    amount_max = forms.DecimalField(
        required=False,
        label=_("Максимальна сума"),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    processing_status = forms.ChoiceField(
        required=False,
        label=_("Статус обробки"),
        choices=[('', _('Всі')), ('new', _('Нові')), ('processed', _('Оброблені'))],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    category = forms.ChoiceField(
        required=False,
        label=_("Категорія"),
        choices=[('', _('Всі'))],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    search = forms.CharField(
        required=False,
        label=_("Пошук"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Пошук у описі, відправнику, одержувачі...')})
    )

    def __init__(self, *args, **kwargs):
        # Отримуємо параметри користувача
        taxpayer = kwargs.pop('taxpayer', None)

        super().__init__(*args, **kwargs)

        # Налаштовуємо поля вибору банківських рахунків
        if taxpayer:
            self.fields['bank_account'].queryset = BankAccount.objects.filter(is_deleted=False)

            # Додаємо категорії
            income_categories = [('', _('Всі'))]
            for code, label in INCOME_CATEGORIES:
                income_categories.append((f'income_{code}', label))

            expense_categories = []
            for code, label in EXPENSE_CATEGORIES:
                expense_categories.append((f'expense_{code}', label))

            # Також додаємо користувацькі категорії
            custom_categories = Category.objects.filter(taxpayer=taxpayer, is_active=True)
            for category in custom_categories:
                if category.category_type == 'income':
                    income_categories.append((f'custom_income_{category.id}', category.name))
                elif category.category_type == 'expense':
                    expense_categories.append((f'custom_expense_{category.id}', category.name))
                else: # both
                    income_categories.append((f'custom_income_{category.id}', category.name))
                    expense_categories.append((f'custom_expense_{category.id}', category.name))

            # Оновлюємо поле категорій
            self.fields['category'].choices = income_categories + expense_categories