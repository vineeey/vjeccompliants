from functools import wraps
from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

ALLOWED_GROUPS = ["HOD", "Principal"]


def _ensure_admin_groups():
    for name in ALLOWED_GROUPS:
        Group.objects.get_or_create(name=name)


def _user_is_hod_or_principal(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_hod", False) or getattr(user, "is_principal", False):
        return True
    return user.groups.filter(name__in=ALLOWED_GROUPS).exists()


def hod_or_principal_required(view_func):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        _ensure_admin_groups()
        if not request.user.is_authenticated:
            return redirect(f"{reverse('admin-access-login')}?next={request.path}")
        if not _user_is_hod_or_principal(request.user):
            return HttpResponseForbidden("You are not allowed to access this page.")
        # Require that the user has passed the admin access gate in this session
        if not request.session.get("admin_access_granted", False):
            return redirect(f"{reverse('admin-access-login')}?next={request.path}")
        return view_func(request, *args, **kwargs)

    return _wrapped
