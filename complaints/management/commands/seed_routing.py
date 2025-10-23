from __future__ import annotations

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import Group, User
from django.conf import settings

from complaints.models import Department, CategoryDepartmentMapping, DepartmentMembership


DEFAULT_DEPARTMENTS = [
    "Facilities",
    "Academics",
    "Administration",
    "Finance",
    "Discipline",
    "Hostel",
    "Transport",
    "IT Services",
    "Library",
]

CATEGORY_TO_DEPT = {
    "infrastructure": "Facilities",
    "academics": "Academics",
    "administration": "Administration",
    "finance": "Finance",
    "discipline": "Discipline",
    "hostel": "Hostel",
    "transport": "Transport",
}


class Command(BaseCommand):
    help = (
        "Seed common departments, category→department mappings, and demo memberships. "
        "Use --no-backfill to skip enrichment backfill."
    )

    def add_arguments(self, parser):
        parser.add_argument("--no-backfill", action="store_true", help="Skip backfilling enrichment")

    def handle(self, *args, **options):
        # 1) Ensure groups
        hod_group, _ = Group.objects.get_or_create(name="HOD")
        principal_group, _ = Group.objects.get_or_create(name="Principal")
        self.stdout.write(self.style.SUCCESS("Ensured groups HOD, Principal"))

        # 2) Departments
        dept_objs = {}
        for name in DEFAULT_DEPARTMENTS:
            dept, _ = Department.objects.get_or_create(name=name)
            dept_objs[name] = dept
        self.stdout.write(self.style.SUCCESS(f"Ensured departments: {', '.join(DEFAULT_DEPARTMENTS)}"))

        # 3) Mappings
        for cat, dname in CATEGORY_TO_DEPT.items():
            dept = dept_objs[dname]
            CategoryDepartmentMapping.objects.get_or_create(category=cat, defaults={"department": dept})
        self.stdout.write(self.style.SUCCESS("Ensured category→department mappings"))

        # 4) Demo users and memberships in DEBUG/dev
        if settings.DEBUG:
            # Demo HOD
            hod_user, _ = User.objects.get_or_create(username="hod_demo", defaults={"email": "hod@example.com"})
            if not hod_user.has_usable_password():
                hod_user.set_password("pass1234")
                hod_user.save()
            hod_group.user_set.add(hod_user)

            # Assign HOD to Facilities by default
            DepartmentMembership.objects.get_or_create(
                user=hod_user, department=dept_objs["Facilities"], defaults={"role": DepartmentMembership.ROLE_ADMIN}
            )

            # Create one staff per mapped department for auto-assign demo
            for cat, dname in CATEGORY_TO_DEPT.items():
                uname = f"{dname.lower().replace(' ', '_')}_staff"
                staff, _ = User.objects.get_or_create(username=uname, defaults={"email": f"{uname}@example.com"})
                if not staff.has_usable_password():
                    staff.set_password("pass1234")
                    staff.save()
                DepartmentMembership.objects.get_or_create(
                    user=staff, department=dept_objs[dname], defaults={"role": DepartmentMembership.ROLE_STAFF}
                )
            self.stdout.write(self.style.WARNING("Created demo users hod_demo and *_staff with password 'pass1234'"))

        # 5) Backfill enrichment unless disabled
        if not options.get("no_backfill"):
            try:
                call_command("backfill_enrichment")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Backfill failed: {e}"))

        self.stdout.write(self.style.SUCCESS("Seeding completed."))
