import io
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_api_complaint_create_multipart_with_attachment():
    client = APIClient()
    image_bytes = b"\xFF\xD8\xFF\xE0" + b"0" * 1024  # minimal JPEG-like header + padding
    file1 = SimpleUploadedFile("test.jpg", image_bytes, content_type="image/jpeg")

    data = {
        "title": "Leak in lab",
        "description": "There is a water leak in the physics lab.",
        "anonymous": "true",
        "attachments": [file1],
    }
    resp = client.post("/api/complaints/create/", data, format="multipart", REMOTE_ADDR="10.0.0.6")
    assert resp.status_code == 201
    body = resp.json()
    assert body["category"] != ""
    # attachments are read-only on serializer; ensure attachments list present
    assert "attachments" in body


@pytest.mark.django_db
def test_api_complaint_create_audio_missing_file_returns_400():
    client = APIClient()
    resp = client.post("/api/complaints/create-audio/", {"anonymous": "true"}, format="multipart")
    assert resp.status_code == 400
    assert "missing" in resp.json().get("detail", "").lower()
