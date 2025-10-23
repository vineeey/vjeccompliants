from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Stub: Build FAISS index for semantic search (to be implemented later)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("FAISS index build is not implemented yet. This is a scaffold."))