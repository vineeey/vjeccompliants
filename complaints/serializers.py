
from __future__ import annotations

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Complaint, ComplaintAttachment


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=4)  # Reduced from 8 to 4

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_("Username already exists."))
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("Email already registered."))
        return value


class ComplaintAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintAttachment
        fields = ["id", "file", "mime_type", "uploaded_at"]
        read_only_fields = ["id", "mime_type", "uploaded_at"]


class ComplaintSerializer(serializers.ModelSerializer):
    attachments = ComplaintAttachmentSerializer(many=True, read_only=True)
    department_name = serializers.SerializerMethodField(read_only=True)
    # Accept submitter info from form; keep optional
    submitter_name = serializers.CharField(required=False, allow_blank=True)
    submitter_division = serializers.CharField(required=False, allow_blank=True)
    submitter_admission_no = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Complaint
        fields = [
            "id", "title", "description", "anonymous", "department", "department_name",
            "status", "category", "priority", "summary", "model_version",
            "confidence", "created_at", "updated_at", "attachments", "assigned_to",
            "submitter_name", "submitter_division", "submitter_admission_no",
        ]
    # Keep system-managed fields read-only
    read_only_fields = ["status", "summary", "model_version", "confidence", "created_at", "updated_at", "assigned_to"]

    def create(self, validated_data):
        return Complaint.objects.create(**validated_data)

    def get_department_name(self, obj):
        try:
            return obj.department.name if obj.department else None
        except Exception:
            return None

    # No per-field getters needed; values come from model fields. If you want
    # to hide these when anonymous, that can be handled in the view layer.