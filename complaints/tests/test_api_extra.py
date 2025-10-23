import io
import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from complaints.models import Department, CategoryDepartmentMapping


@pytest.mark.django_db
def test_api_complaint_create_audio_success_with_mock(monkeypatch):
    client = APIClient()

    # Mock transcription to avoid heavyweight model downloads
    import complaints.views as views
    monkeypatch.setattr(views, "process_audio", lambda path: "urgent leak in room 101" )

    fake_wav = SimpleUploadedFile(
        "voice.wav", b"RIFF0000WAVEfmt ", content_type="audio/wav"
    )

    resp = client.post(
        "/api/complaints/create-audio/",
        {"audio": fake_wav, "anonymous": "true"},
        format="multipart",
        REMOTE_ADDR="10.0.0.1",
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["category"] != ""
    assert data["summary"] != ""


@pytest.mark.django_db
def test_api_invalid_attachment_mime_returns_400():
    client = APIClient()
    bad_file = SimpleUploadedFile("readme.txt", b"hello world", content_type="text/plain")

    resp = client.post(
        "/api/complaints/create/",
        {
            "title": "Invalid file",
            "description": "Test invalid mime",
            "anonymous": "true",
            "attachments": [bad_file],
        },
        format="multipart",
        REMOTE_ADDR="10.0.0.2",
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_department_mapping_on_enrichment():
    client = APIClient()
    dept = Department.objects.create(name="Facilities")
    CategoryDepartmentMapping.objects.create(category="infrastructure", department=dept)

    resp = client.post(
        "/api/complaints/create/",
        {
            "title": "Broken fan",
            "description": "The fan in classroom is broken and needs repair.",
            "anonymous": True,
        },
        format="json",
        REMOTE_ADDR="10.0.0.3",
    )
    assert resp.status_code == 201
    data = resp.json()
    # department should be mapped by enrichment
    assert data["department"] == dept.id


@pytest.mark.django_db
def test_staff_list_sees_all():
    client = APIClient()
    staff = User.objects.create_user(username="staff", password="pass12345", is_staff=True)
    u1 = User.objects.create_user(username="a", password="pass12345")
    u2 = User.objects.create_user(username="b", password="pass12345")

    # create complaints as u1 and u2
    client.login(username="a", password="pass12345")
    r1 = client.post(
        "/api/complaints/create/",
        {"title": "Issue A", "description": "room light broken", "anonymous": False},
        format="json",
        REMOTE_ADDR="10.0.0.4",
    )
    assert r1.status_code == 201
    client.logout()

    client.login(username="b", password="pass12345")
    r2 = client.post(
        "/api/complaints/create/",
        {"title": "Issue B", "description": "payment refund delay", "anonymous": False},
        format="json",
        REMOTE_ADDR="10.0.0.5",
    )
    assert r2.status_code == 201
    client.logout()

    # staff sees all
    client.login(username="staff", password="pass12345")
    list_resp = client.get("/api/complaints/")
    assert list_resp.status_code == 200
    items = list_resp.json()
    titles = {i["title"] for i in items}
    assert {"Issue A", "Issue B"}.issubset(titles)
