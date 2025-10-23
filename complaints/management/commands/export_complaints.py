from __future__ import annotations

import csv
import json
from typing import Iterable

from django.core.management.base import BaseCommand, CommandError

from ...models import Complaint


class Command(BaseCommand):
    help = "Export complaints to stdout in JSON or CSV format. Usage: manage.py export_complaints --format json|csv"

    def add_arguments(self, parser):
        parser.add_argument("--format", choices=["json", "csv"], default="json")
        parser.add_argument("--status", nargs="*", help="Optional status filters")

    def handle(self, *args, **options):
        fmt = options["format"]
        qs = Complaint.objects.all().order_by("id")
        statuses = options.get("status") or []
        if statuses:
            qs = qs.filter(status__in=statuses)

        if fmt == "json":
            data = [self._to_dict(c) for c in qs]
            self.stdout.write(json.dumps(data, indent=2, default=str))
        else:
            writer = csv.writer(self.stdout)
            writer.writerow([
                "id", "title", "description", "created_by", "anonymous",
                "department", "status", "category", "priority", "summary",
                "model_version", "confidence", "assigned_to", "created_at", "updated_at",
            ])
            for c in qs:
                writer.writerow([
                    c.id, c.title, c.description, getattr(c.created_by, "username", ""),
                    c.anonymous, getattr(c.department, "name", ""), c.status, c.category,
                    c.priority, c.summary, c.model_version, c.confidence,
                    getattr(c.assigned_to, "username", ""), c.created_at.isoformat(), c.updated_at.isoformat(),
                ])

    def _to_dict(self, c: Complaint):
        return {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "created_by": getattr(c.created_by, "username", None),
            "anonymous": c.anonymous,
            "department": getattr(c.department, "name", None),
            "status": c.status,
            "category": c.category,
            "priority": c.priority,
            "summary": c.summary,
            "model_version": c.model_version,
            "confidence": c.confidence,
            "assigned_to": getattr(c.assigned_to, "username", None),
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
