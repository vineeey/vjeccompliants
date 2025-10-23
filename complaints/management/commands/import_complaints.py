from __future__ import annotations

import csv
import json
from typing import Iterable, Dict, Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from ...models import Complaint, Department

User = get_user_model()


def _create_from_dict(d: Dict[str, Any]) -> Complaint:
    """Create a complaint from a dictionary (assumes keys similar to admin export)."""
    username = d.get("created_by")
    user = None
    if username:
        user = User.objects.filter(username=username).first()

    dept_name = d.get("department")
    dept = None
    if dept_name:
        dept, _ = Department.create_or_get(name=dept_name) if hasattr(Department, "create_or_get") else Department.objects.get_or_create(name=dept_name)

    return Complaint.objects.create(
        title=d.get("title", "")[:255],
        description=d.get("description", ""),
        created_by=user,
        anonymous=bool(d.get("anonymous", False)),
        department=dept,
        status=d.get("status", Complaint.STATUS_PENDING),
        category=d.get("category", ""),
        priority=d.get("priority", Complaint.PRIORITY_LOW),
        summary=d.get("summary", ""),
        model_version=d.get("model_version", ""),
        confidence=float(d.get("confidence", 0.0)),
    )


class Command(BaseCommand):
    help = "Import complaints from a CSV or JSON file (format similar to admin export)."

    def add_arguments(self, parser):
        parser.add_argument("path", type=str, help="Path to CSV or JSON file")

    def handle(self, *args, **options):
        path = options["path"]
        if path.lower().endswith(".csv"):
            self._import_csv(path)
        elif path.lower().endswith(".json"):
            self._import_json(path)
        else:
            raise CommandError("Unsupported file type. Use .csv or .json")

    def _import_csv(self, path: str):
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                _create_from_dict(row)
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported {count} complaints from CSV."))

    def _import_json(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise CommandError("JSON must be a list of complaint objects.")
        for item in data:
            _create_from_dict(item)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(data)} complaints from JSON."))