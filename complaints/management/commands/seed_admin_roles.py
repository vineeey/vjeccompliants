from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from django.conf import settings

ALLOWED_GROUPS = ["HOD", "Principal"]

class Command(BaseCommand):
    help = "Create HOD and Principal groups and example users (development only)."

    def handle(self, *args, **options):
        for name in ALLOWED_GROUPS:
            Group.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Ensured groups: HOD, Principal"))

        # Create example users only in DEBUG mode
        if settings.DEBUG:
            hod_user, _ = User.objects.get_or_create(username="hod_demo", defaults={"email": "hod@example.com"})
            if not hod_user.has_usable_password():
                hod_user.set_password("pass1234")
                hod_user.save()
            principal_user, _ = User.objects.get_or_create(username="principal_demo", defaults={"email": "principal@example.com"})
            if not principal_user.has_usable_password():
                principal_user.set_password("pass1234")
                principal_user.save()

            Group.objects.get(name="HOD").user_set.add(hod_user)
            Group.objects.get(name="Principal").user_set.add(principal_user)

            self.stdout.write(self.style.WARNING("Created demo users: hod_demo / principal_demo with password 'pass1234' (development only)."))
            self.stdout.write(self.style.NOTICE("Set ADMIN_SECRET_KEY env var (current default: 'adminisgoingtologin')."))
