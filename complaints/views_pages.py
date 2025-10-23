from __future__ import annotations

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from .models import DepartmentMembership
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse


ALLOWED_ADMIN_GROUPS = ["HOD", "Principal"]


class AdminAccessRequiredMixin(LoginRequiredMixin):
    login_url = "/auth/login/"

    def _user_is_admin_role(self, user) -> bool:
        if getattr(user, "is_hod", False) or getattr(user, "is_principal", False):
            return True
        return user.groups.filter(name__in=ALLOWED_ADMIN_GROUPS).exists()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        # Ensure groups exist
        for g in ALLOWED_ADMIN_GROUPS:
            Group.objects.get_or_create(name=g)
        # Require admin role AND a recent admin-access gate in this session
        if not self._user_is_admin_role(request.user) or not request.session.get("admin_access_granted", False):
            return redirect(f"{reverse('admin-access-login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)


class HomeView(TemplateView):
    template_name = "pages/home.html"


class ComplaintFormView(LoginRequiredMixin, TemplateView):
    template_name = "pages/complaint_form.html"
    login_url = "/auth/login/"


class MyCasesView(LoginRequiredMixin, TemplateView):
    template_name = "pages/my_cases.html"
    login_url = "/auth/login/"


class DepartmentOnlyMixin(LoginRequiredMixin):
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        # Allow HOD/Principal to access even without explicit Department membership
        is_admin_role = (
            getattr(request.user, "is_hod", False)
            or getattr(request.user, "is_principal", False)
            or request.user.groups.filter(name__in=ALLOWED_ADMIN_GROUPS).exists()
        )
        if not is_admin_role:
            has_membership = DepartmentMembership.objects.filter(user=request.user).exists()
            if not has_membership:
                return HttpResponseForbidden("Department access required")
        return super().dispatch(request, *args, **kwargs)


class DepartmentDashboardView(AdminAccessRequiredMixin, DepartmentOnlyMixin, TemplateView):

    template_name = "pages/department_dashboard.html"
    login_url = "/auth/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from .models import Complaint, DepartmentMembership
        from django.db import models
        request = self.request
        dept_ids = list(DepartmentMembership.objects.filter(user=user).values_list("department_id", flat=True))
        is_principal = getattr(user, "is_principal", False) or user.groups.filter(name="Principal").exists()
        is_hod = getattr(user, "is_hod", False) or user.groups.filter(name="HOD").exists()
        if is_principal or is_hod:
            complaints = Complaint.objects.all()
        elif user.is_staff or user.is_superuser:
            complaints = Complaint.objects.all()
        else:
            complaints = Complaint.objects.filter(created_by=user)
        # Apply status and priority filters from GET params
        status_f = request.GET.get("status")
        if status_f:
            complaints = complaints.filter(status=status_f)
        priority_f = request.GET.get("priority")
        if priority_f:
            complaints = complaints.filter(priority=priority_f)
        complaints = complaints.order_by("-created_at")
        context["complaints"] = complaints
        # Add counts for dashboard summary
        context["count_pending"] = complaints.filter(status="pending").count()
        context["count_in_review"] = complaints.filter(status="in_review").count()
        context["count_resolved"] = complaints.filter(status="resolved").count()
        return context


class AdminAuditView(AdminAccessRequiredMixin, TemplateView):
    template_name = "pages/admin_audit.html"
    login_url = "/auth/login/"


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "pages/reports.html"
    login_url = "/auth/login/"


class HelpView(TemplateView):
    template_name = "pages/help.html"


class OfflineView(TemplateView):
    template_name = "offline.html"


class ComplaintDetailView(LoginRequiredMixin, TemplateView):
    template_name = "pages/complaint_detail.html"
    login_url = "/auth/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Complaint
        pk = self.kwargs.get("pk")
        try:
            complaint = Complaint.objects.get(pk=pk)
        except Complaint.DoesNotExist:
            complaint = None
        context["complaint"] = complaint
        return context
