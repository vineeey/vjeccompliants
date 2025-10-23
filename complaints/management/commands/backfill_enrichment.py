from django.core.management.base import BaseCommand

from complaints.models import Complaint
from complaints.ml.infer import infer_enrich_complaint


class Command(BaseCommand):
    help = "Backfill AI enrichment (category, summary, priority, model_version, confidence, department) for existing complaints."

    def handle(self, *args, **options):
        qs = Complaint.objects.all()
        updated = 0
        skipped = 0
        for c in qs.iterator():
            needs = (not c.category) or (not c.summary) or (c.model_version == "")
            if not needs:
                skipped += 1
                continue
            changed = infer_enrich_complaint(c)
            if changed:
                c.save(update_fields=[
                    "category",
                    "priority",
                    "summary",
                    "model_version",
                    "confidence",
                    "department",
                ])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Enrichment backfill complete: updated={updated}, skipped={skipped}"))
