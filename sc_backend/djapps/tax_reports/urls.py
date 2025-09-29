from django.urls import path

from tax_reports.views import (
    TaxReportDetailView,
    TaxReportListView,
    TaxReportMarkPaidView,
    TaxReportPreviewView,
    TaxReportSubmitView,
)

urlpatterns = [
    path('', TaxReportListView.as_view(), name='tax_report_list'),
    path('<uuid:pk>/', TaxReportDetailView.as_view(), name='tax_report_detail'),
    path('preview/<int:quarter>/<int:year>/', TaxReportPreviewView.as_view(), name='tax_report_preview'),
    path('preview/<int:quarter>/', TaxReportPreviewView.as_view(), name='tax_report_preview'),
    path('<uuid:pk>/mark-paid/', TaxReportMarkPaidView.as_view(), name='tax_report_mark_paid'),
    path('<uuid:pk>/submit/', TaxReportSubmitView.as_view(), name='tax_report_submit'),
    path('<uuid:pk>/download/', TaxReportDetailView.as_view(), name='tax_report_download'),
]