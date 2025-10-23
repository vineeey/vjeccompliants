from __future__ import annotations

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .ml.infer import infer_enrich_complaint
from .models import Complaint, DepartmentMembership
from .utils_async import run_in_background


@receiver(post_save, sender=Complaint)
def complaint_post_save(sender, instance: Complaint, created: bool, **kwargs):
    """
    After saving a complaint, run local ML inference synchronously to fill:
    category, priority, summary, model_version, confidence and map department.
    Avoid infinite recursion by updating fields without re-triggering inference.
    """
    # If enrichment needed, run synchronously on SQLite to avoid lock issues and to make tests deterministic.
    needs_enrich = not instance.category or not instance.summary or instance.model_version == ""
    if needs_enrich:
        engine = settings.DATABASES.get("default", {}).get("ENGINE", "")
        if engine.endswith("sqlite3") or getattr(settings, "SYNC_ENRICH", False):
            changed = infer_enrich_complaint(instance)
            if changed:
                # Save only the fields we changed to avoid re-triggering heavy operations
                instance.save(update_fields=["category", "priority", "summary", "model_version", "confidence", "department"])
            return
        else:
            def _enrich_and_assign(complaint_id: int):
                try:
                    comp = Complaint.objects.get(pk=complaint_id)
                except Complaint.DoesNotExist:
                    return

                changed = infer_enrich_complaint(comp)
                if changed:
                    comp.save(update_fields=["category", "priority", "summary", "model_version", "confidence", "department"])

                # Auto-assign removed by request: do not set assigned_to automatically

            run_in_background(_enrich_and_assign, instance.pk)
            return

    # Auto-assign removed by request: leave assigned_to unchanged

    # Email notification on status change
    old_status = getattr(instance, "_old_status", None)
    if old_status is not None and old_status != instance.status:
        recipient = getattr(instance.created_by, "email", None)
        if recipient:
            subject = f"Complaint #{instance.pk} status updated: {instance.status}"
            message = (
                f"Hello {getattr(instance.created_by, 'first_name', '') or instance.created_by.username},\n\n"
                f"Your complaint '{instance.title}' status changed from '{old_status}' to '{instance.status}'.\n\n"
                f"Summary: {instance.summary or '-'}\nCategory: {instance.category or '-'} | Priority: {instance.priority or '-'}\n\n"
                f"Thanks."
            )
            send_mail(subject, message, getattr(settings, "DEFAULT_FROM_EMAIL", None), [recipient], fail_silently=True)


@receiver(pre_save, sender=Complaint)
def complaint_pre_save(sender, instance: Complaint, **kwargs):
    if instance.pk:
        try:
            prev = Complaint.objects.get(pk=instance.pk)
            instance._old_status = prev.status
        except Complaint.DoesNotExist:
            instance._old_status = None