# Complaints System – Developer Guide

## Quick start

1. Create and activate a virtualenv
2. Install dependencies
3. Configure env vars
4. Migrate and run

### Environment

Copy `.env.example` to `.env` (or set env vars locally):

```
ADMIN_SECRET_KEY=changeme
DJANGO_SECRET_KEY=changeme-dev
DEBUG=true
```

The admin-access login requires `ADMIN_SECRET_KEY`; never use the default in production.

### Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt  # if present
python manage.py migrate
python manage.py runserver
```

Optionally seed roles/users (HOD/Principal):

```
python manage.py createsuperuser
# or add users to Groups: HOD, Principal
```

### Tests

```
pytest -q
```

During tests (and when using SQLite), complaint enrichment runs synchronously to avoid database locks
and to make results deterministic. You can force synchronous behavior by setting `SYNC_ENRICH=true`.

### Notes

- Admin UI is displayed only for users in HOD/Principal groups or with flags `is_hod`/`is_principal`.
- Server-side checks protect all admin routes; UI is not the only guard.
- Anonymous complaint submission is allowed when `anonymous=true` is provided.
