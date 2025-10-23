from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from ...ml.train_classifier import train_and_save


class Command(BaseCommand):
    help = "Train TF-IDF + Logistic Regression complaint category model from complaints/data/complaints_labeled.csv"

    def handle(self, *args, **options):
        try:
            version = train_and_save()
            self.stdout.write(self.style.SUCCESS(f"Model trained and saved. Version: {version}"))
        except FileNotFoundError as e:
            raise CommandError(str(e))
        except Exception as e:
            raise CommandError(f"Training failed: {e}")