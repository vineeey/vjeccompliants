import pytest
from django.contrib.auth.models import User, Group
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_navbar_shows_admin_menu_for_hod(client):
    user = User.objects.create_user(username="hodx", password="pass1234")
    Group.objects.get_or_create(name="HOD")[0].user_set.add(user)
    client.login(username="hodx", password="pass1234")
    resp = client.get(reverse("home"))
    assert resp.status_code == 200
    content = resp.content.decode("utf-8")
    assert "Manage Complaints" in content
    assert "Audit Trail" in content
    assert "Submit Complaint" not in content


def test_navbar_shows_student_menu_for_non_admin(client):
    user = User.objects.create_user(username="stud1", password="pass1234")
    client.login(username="stud1", password="pass1234")
    resp = client.get(reverse("home"))
    assert resp.status_code == 200
    content = resp.content.decode("utf-8")
    assert "Submit Complaint" in content
    # Admin menu hidden for non-admin users
    assert "Manage Complaints" not in content
    assert "Audit Trail" not in content
