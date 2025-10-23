from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.templatetags.static import static as static_url
from complaints.views import app_logout
from complaints.views_pages import ComplaintDetailView

urlpatterns = [
    # Frontend pages at root (placed before admin/ so '/admin/complaints/' maps here)
    path("", include("complaints.urls_pages")),
    # API routes
    path("api/", include("complaints.urls")),
    # Django auth views
    path("auth/", include("django.contrib.auth.urls")),
    # Override auth logout to use our lenient logout view (handles GET in DEBUG)
    path("auth/logout/", app_logout, name="logout"),
    # Serve a favicon to avoid 404s in dev
    path("favicon.ico", RedirectView.as_view(url=static_url("complaints/img/logo.png"), permanent=True)),
    # Django admin
    path("admin/", admin.site.urls),
     path('complaints/<int:pk>/', ComplaintDetailView.as_view(), name='complaint_detail_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)