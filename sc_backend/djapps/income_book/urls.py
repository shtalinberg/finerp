
from django.urls import path

from .views import (
    CreateAdjustmentView,
    FillFromFinopView,
    IncomeBookListView,
    IncomeRecordCreateView,
    IncomeRecordDeleteView,
    IncomeRecordDetailView,
    IncomeRecordUpdateView,
)

urlpatterns = [
    path('', IncomeBookListView.as_view(), name='income_book_list'),
    path('<int:pk>/', IncomeRecordDetailView.as_view(), name='income_record_detail'),
    path('create/', IncomeRecordCreateView.as_view(), name='income_record_create'),
    path('<int:pk>/update/', IncomeRecordUpdateView.as_view(), name='income_record_update'),
    path('<int:pk>/delete/', IncomeRecordDeleteView.as_view(), name='income_record_delete'),
    path('<int:pk>/adjust/', CreateAdjustmentView.as_view(), name='create_adjustment'),
    path('fill-from-finop/<int:pk>/', FillFromFinopView.as_view(), name='fill_from_finop'),
]