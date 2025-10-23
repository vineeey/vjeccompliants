from django.urls import path
from django.views.generic import TemplateView

from .views_pages import (
    HomeView,
    ComplaintFormView,
    MyCasesView,
    DepartmentDashboardView,
    ReportsView,
    HelpView,
    OfflineView,
    ComplaintDetailView,
    AdminAuditView,
)
from .views import admin_access_login, app_logout, admin_access_signup

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("submit/", ComplaintFormView.as_view(), name="submit_complaint"),
    path("cases/", MyCasesView.as_view(), name="my_cases"),
    path("cases/<int:pk>/", ComplaintDetailView.as_view(), name="case_detail"),
    path("departments/", DepartmentDashboardView.as_view(), name="departments"),
    path("reports/", ReportsView.as_view(), name="reports"),
    path("help/", HelpView.as_view(), name="help"),
    path("offline/", OfflineView.as_view(), name="offline"),
    path("auth/signup/", TemplateView.as_view(template_name="registration/signup.html"), name="signup"),
    path("admin-access/login/", admin_access_login, name="admin-access-login"),
    path("admin-access/signup/", admin_access_signup, name="admin-access-signup"),
    path("logout/", app_logout, name="app-logout"),
    path("admin/complaints/", DepartmentDashboardView.as_view(), name="complaints-dashboard"),
    path("admin/audit/", AdminAuditView.as_view(), name="admin-audit"),
]
