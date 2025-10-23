Admin-access login for HOD/Principal

Environment variable
- Set ADMIN_SECRET_KEY in your environment (do not hardcode in code):
  - PowerShell (Windows):
    $env:ADMIN_SECRET_KEY = "replace-with-strong-secret"; python manage.py runserver
  - Bash:
    export ADMIN_SECRET_KEY="replace-with-strong-secret" && python manage.py runserver

Creating roles
- Ensure groups exist and create demo users (development):
  python manage.py seed_admin_roles
  - Demo users: hod_demo / principal_demo, password: pass1234 (only in DEBUG)

Usage
- Visit /admin-access/login/ for HOD/Principal login.
- Enter username/email, password, and the secret key.
- On success, you’ll be redirected to the complaints dashboard.

Rotating the secret
- Change the ADMIN_SECRET_KEY environment variable.
- Notify HOD/Principal users of the new key.
- Existing sessions continue until logout; revoke sessions by logging out users or clearing sessions.

Security notes
- Do not hardcode production secrets.
- All attempts (success/failure) are audited with timestamp, user/email, IP and reason.
- Endpoint requires HTTPS when DEBUG=False.
- Rate limited (5 attempts per 10 minutes per IP) to reduce brute-force risk.
- Consider enabling 2FA for HOD/Principal accounts.
