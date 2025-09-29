
from django.urls import path

from .views import (
    TaxpayerCreateView,
    TaxpayerDeleteView,
    TaxpayerDetailView,
    TaxpayerDocumentCreateView,
    TaxpayerDocumentDeleteView,
    TaxpayerListView,
    TaxpayerSettingsUpdateView,
    TaxpayerUpdateView,
    get_tax_rate_choices,
)

urlpatterns = [
    path('', TaxpayerListView.as_view(), name='taxpayer_list'),
    path('<int:pk>/', TaxpayerDetailView.as_view(), name='taxpayer_detail'),
    path('create/', TaxpayerCreateView.as_view(), name='taxpayer_create'),
    path('<int:pk>/update/', TaxpayerUpdateView.as_view(), name='taxpayer_update'),
    path('<int:pk>/delete/', TaxpayerDeleteView.as_view(), name='taxpayer_delete'),
    path('<int:taxpayer_id>/settings/', TaxpayerSettingsUpdateView.as_view(), name='taxpayer_settings_update'),
    path('<int:taxpayer_id>/documents/add/', TaxpayerDocumentCreateView.as_view(), name='taxpayer_document_create'),
    path('documents/<int:pk>/delete/', TaxpayerDocumentDeleteView.as_view(), name='taxpayer_document_delete'),
    path('ajax/tax-rate-choices/', get_tax_rate_choices, name='ajax_tax_rate_choices'),
]