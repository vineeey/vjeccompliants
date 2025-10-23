from typing import Dict
from django.contrib.auth.models import Group

ADMIN_GROUPS = {"HOD", "Principal"}

def role_flags(request) -> Dict[str, object]:
    user = getattr(request, "user", None)
    is_admin = False
    role_name = ""
    if user and user.is_authenticated:
        try:
            if getattr(user, "is_hod", False):
                is_admin = True
                role_name = "HOD"
            elif getattr(user, "is_principal", False):
                is_admin = True
                role_name = "Principal"
            elif user.groups.filter(name__in=ADMIN_GROUPS).exists():
                is_admin = True
                # pick first matching group as role name
                g = user.groups.filter(name__in=ADMIN_GROUPS).values_list("name", flat=True).first()
                role_name = g or ""
        except Exception:
            is_admin = False
    return {
        "is_hod_or_principal": is_admin,
        "role_name": role_name,
    }
