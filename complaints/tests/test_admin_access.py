import os
import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Group

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def admin_secret_key_settings(settings):
    settings.ADMIN_SECRET_KEY = "adminisgoingtologin"
    return settings


@pytest.fixture
def hod_user():
    u = User.objects.create_user(username="hod1", email="hod1@example.com", password="pass1234")
    g, _ = Group.objects.get_or_create(name="HOD")
    g.user_set.add(u)
    return u


def test_admin_access_success(client, hod_user):
    url = reverse('admin-access-login')
    resp = client.post(url, data={
        'username_or_email': hod_user.username,
        'password': 'pass1234',
        'secret_key': 'adminisgoingtologin',
        'next': reverse('complaints-dashboard'),
    }, follow=False)
    # Should redirect to dashboard directly
    assert resp.status_code in (302, 301)
    assert resp['Location'].endswith(reverse('complaints-dashboard')) or '/admin/complaints/' in resp['Location']


def test_admin_access_fail_bad_secret(client, hod_user):
    url = reverse('admin-access-login')
    resp = client.post(url, data={
        'username_or_email': hod_user.username,
        'password': 'pass1234',
        'secret_key': 'wrongkey',
    })
    assert resp.status_code == 200
    assert b'Login failed' in resp.content


def test_admin_access_fail_not_in_group(client):
    user = User.objects.create_user(username="user1", password="pass1234")
    url = reverse('admin-access-login')
    resp = client.post(url, data={
        'username_or_email': user.username,
        'password': 'pass1234',
        'secret_key': 'adminisgoingtologin',
    })
    assert resp.status_code == 200
    assert b'Login failed' in resp.content


def test_access_control_dashboard_requires_admin_gate(client, hod_user):
    # login normal
    client.login(username=hod_user.username, password='pass1234')
    resp = client.get(reverse('complaints-dashboard'))
    # Should redirect to admin-access-login because session flag missing
    assert resp.status_code in (302, 301)
    assert reverse('admin-access-login') in resp.url


def test_admin_signup_success(client, settings):
    settings.ADMIN_SECRET_KEY = 'adminisgoingtologin'
    settings.ADMIN_SIGNUP_ENABLED = True
    url = reverse('admin-access-signup')
    resp = client.post(url, data={
        'username': 'newhod',
        'email': 'newhod@example.com',
        'password': 'pass1234',
        'role': 'HOD',
        'secret_key': 'adminisgoingtologin',
    }, follow=True)
    assert resp.status_code == 200
    # After success it redirects to admin-access-login
    assert any(r[0].endswith(reverse('admin-access-login')) for r in resp.redirect_chain)
