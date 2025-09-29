from django.conf import settings
from django.conf.urls import handler403, handler404, handler500
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from core.views import error_403, error_404, error_500

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path('', include('core.urls')),
    path('banks/', include('banks.urls')),
    path('finops/', include('finops.urls')),
    path('income-book/', include('income_book.urls')),
    path('tax-reports/', include('tax_reports.urls')),
    path('taxpayers/', include('taxpayers.urls')),
    path("admzone/", admin.site.urls),
]

# Додаткові URL для сповіщень
# urlpatterns += [
#     path('notifications/', lambda x: None, name='notification_list'),
#     path('notifications/<uuid:pk>/read/', lambda request, pk: Notification.objects.get(pk=pk).mark_as_read(), name='notification_read'),
#     path('tasks/', lambda x: None, name='task_list'),
#     path('tasks/<uuid:pk>/', lambda x, pk: None, name='task_detail'),
# ]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]

    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        # path("403/", TemplateView.as_view(template_name="403.html"), name="403"),
        # path("404/", TemplateView.as_view(template_name="404.html"), name="404"),
        path("500/", TemplateView.as_view(template_name="500.html"), name="500"),
        # path("503/", TemplateView.as_view(template_name="503.html"), name="503"),
    ]

handler403 = error_403
handler404 = error_404
handler500 = error_500
