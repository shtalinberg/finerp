from django.conf import settings
from django.urls import path

from core.views import DashboardView, test_error_page

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += [
        path('error/<str:error_code>/', test_error_page, name='test_error_page'),
    ]