import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_api_complaint_create_anonymous_json():
    client = APIClient()
    payload = {
        "title": "Broken fan in classroom",
        "description": "The fan in room 101 is broken and needs urgent repair.",
        "anonymous": True,
    }
    resp = client.post("/api/complaints/create/", payload, format="json")
    assert resp.status_code == 201
    data = resp.json()
    assert data["category"] != ""
    assert data["summary"] != ""
    assert data["priority"] in ["low", "medium", "high"]


@pytest.mark.django_db
def test_api_register_returns_201():
    client = APIClient()
    resp = client.post(
        "/api/register/",
        {"username": "bob", "email": "bob@example.com", "password": "password123"},
        format="json",
    )
    assert resp.status_code == 201


@pytest.mark.django_db
def test_api_complaint_list_requires_auth():
    client = APIClient()
    resp = client.get("/api/complaints/")
    # Requires auth per view permission_classes
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_api_complaint_list_only_user_items():
    # Create two users and one complaint each; verify user sees only own
    client = APIClient()
    u1 = User.objects.create_user(username="u1", password="pass12345")
    u2 = User.objects.create_user(username="u2", password="pass12345")

    # login as u1 and create complaint
    client.login(username="u1", password="pass12345")
    r1 = client.post(
        "/api/complaints/create/",
        {"title": "Issue A", "description": "room light broken", "anonymous": False},
        format="json",
    )
    assert r1.status_code == 201

    client.logout()

    # login as u2 and create complaint
    client.login(username="u2", password="pass12345")
    r2 = client.post(
        "/api/complaints/create/",
        {"title": "Issue B", "description": "payment refund delay", "anonymous": False},
        format="json",
    )
    assert r2.status_code == 201

    # u2 lists complaints; should only see their own
    list_resp = client.get("/api/complaints/")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    assert all(i["title"] != "Issue A" for i in items)


@pytest.mark.django_db
def test_api_complaint_create_with_image_attachment():
    client = APIClient()
    user = User.objects.create_user(username="up", password="pass12345")
    client.login(username="up", password="pass12345")

    # Minimal fake PNG by extension; validator falls back to extension when magic isn't available
    file = SimpleUploadedFile(
        "photo.png",
        b"\x89PNG\r\n\x1a\n\x00\x00\x00IHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde",
        content_type="image/png",
    )
    resp = client.post(
        "/api/complaints/create/",
        {
            "title": "Attachment Test",
            "description": "room light broken",
            "anonymous": False,
            "attachments": [file],
        },
        format="multipart",
    )
    assert resp.status_code == 201
    data = resp.json()
    assert isinstance(data.get("attachments"), list)
    assert len(data["attachments"]) == 1


@pytest.mark.django_db
def test_api_complaint_create_audio_transcription_unavailable_returns_400():
    client = APIClient()
    # No auth (anonymous allowed for audio create)
    audio = SimpleUploadedFile("note.wav", b"FAKEAUDIO", content_type="audio/wav")
    resp = client.post(
        "/api/complaints/create-audio/",
        {"audio": audio, "title": "Voice Issue", "anonymous": "true"},
        format="multipart",
    )
    # Since whisper libs aren't installed in this env, expect 400 with helpful message
    assert resp.status_code == 400
    assert "Transcription" in resp.json().get("detail", "")
