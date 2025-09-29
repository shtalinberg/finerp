from django.urls import path

from banks.views import (
    BankAccountCreateView,
    BankAccountDeleteView,
    BankAccountListView,
    BankAccountUpdateView,
    BankCreateView,
    BankDeleteView,
    BankDetailView,
    BankListView,
    BankUpdateView,
)

urlpatterns = [

    path('', BankListView.as_view(), name='bank_list'),
    path('<uuid:pk>/', BankDetailView.as_view(), name='bank_detail'),
    path('create/', BankCreateView.as_view(), name='bank_create'),
    path('<uuid:pk>/update/', BankUpdateView.as_view(), name='bank_update'),
    path('<uuid:pk>/delete/', BankDeleteView.as_view(), name='bank_delete'),

    path('accounts/', BankAccountListView.as_view(), name='bank_account_list'),
    path('accounts/create/', BankAccountCreateView.as_view(), name='bank_account_create'),
    path('accounts/<uuid:pk>/update/', BankAccountUpdateView.as_view(), name='bank_account_update'),
    path('accounts/<uuid:pk>/delete/', BankAccountDeleteView.as_view(), name='bank_account_delete'),
]