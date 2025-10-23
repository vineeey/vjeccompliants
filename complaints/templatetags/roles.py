from django import template

register = template.Library()

ADMIN_GROUPS = {"HOD", "Principal"}

@register.filter(name="has_admin_role")
def has_admin_role(user) -> bool:
    try:
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "is_hod", False) or getattr(user, "is_principal", False):
            return True
        return user.groups.filter(name__in=ADMIN_GROUPS).exists()
    except Exception:
        return False
