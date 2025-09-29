
from django.urls import path

from finops.views import FinopListView, ProcessFinopView, SyncFinopsView

urlpatterns = [
    path('', FinopListView.as_view(), name='finop_list'),
    path('sync/', SyncFinopsView.as_view(), name='sync_finops'),
    path('<uuid:pk>/process/', ProcessFinopView.as_view(), name='process_finop'),
]