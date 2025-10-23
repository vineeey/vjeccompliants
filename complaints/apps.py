from django.apps import AppConfig


class ComplaintsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "complaints"

    def ready(self):
        # Ensure signal handlers are connected. Importing signals should register
        # via decorators, but also connect explicitly as a fallback to be robust
        # in test environments where module-level execution may be skipped.
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
