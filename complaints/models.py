from __future__ import annotations

import os
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords

from .validators import validate_file_size, validate_mime_type

User = get_user_model()


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self) -> str:
        return self.name


class CategoryDepartmentMapping(models.Model):
    category = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="category_mappings")

    class Meta:
        verbose_name = "Category → Department Mapping"
        verbose_name_plural = "Category → Department Mappings"

    def __str__(self) -> str:
        return f"{self.category} → {self.department.name}"


class Complaint(models.Model):
    STATUS_PENDING = "pending"
    STATUS_IN_REVIEW = "in_review"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_REVIEW, "In Review"),
        (STATUS_RESOLVED, "Resolved"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="complaints")
    anonymous = models.BooleanField(default=False)
    department = models.ForeignKey("Department", on_delete=models.SET_NULL, null=True, blank=True, related_name="complaints")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    category = models.CharField(max_length=100, blank=True, default="")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, blank=True, default=PRIORITY_LOW)
    summary = models.TextField(blank=True, default="")
    model_version = models.CharField(max_length=100, blank=True, default="")
    confidence = models.FloatField(default=0.0)
    # Draft reply suggestion for admins to edit before sending
    reply_draft = models.TextField(blank=True, default="")

    # Optional submitter details for identification in HOD views
    submitter_name = models.CharField(max_length=150, blank=True, default="")
    submitter_division = models.CharField(max_length=50, blank=True, default="")
    submitter_admission_no = models.CharField(max_length=50, blank=True, default="")

    # Optional assignee (auto-assigned from department members if available)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_complaints",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"{self.title} (#{self.pk})"


def attachment_upload_to(instance: "ComplaintAttachment", filename: str) -> str:
    cid = instance.complaint_id or "unassigned"
    return os.path.join("complaints", str(cid), filename)


class ComplaintAttachment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(
        upload_to=attachment_upload_to,
        validators=[validate_file_size, validate_mime_type],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    mime_type = models.CharField(max_length=100, blank=True, default="")

    def clean(self):
        for validator in self._meta.get_field("file").validators:
            validator(self.file)

    def __str__(self) -> str:
        return f"Attachment #{self.pk} for Complaint #{self.complaint_id}"


class DepartmentMembership(models.Model):
    ROLE_ADMIN = "admin"
    ROLE_STAFF = "staff"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_STAFF, "Staff"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="department_memberships")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="members")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_STAFF)

    class Meta:
        unique_together = ("user", "department")

    def __str__(self) -> str:
        return f"{self.user.username} in {self.department.name} ({self.role})"


class AdminAccessAudit(models.Model):
    """Audit log for HOD/Principal admin-access attempts."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    success = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        who = self.user.username if self.user else self.email or "unknown"
        return f"AdminAccessAudit({who}, success={self.success}, at={self.created_at:%Y-%m-%d %H:%M:%S})"
