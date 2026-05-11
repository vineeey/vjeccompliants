<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=220&text=VJEC%20Complaints&fontAlign=50&fontAlignY=38&color=0:7F00FF,50:E100FF,100:00DBDE&desc=3D%20Animative%20Campus%20Complaint%20Platform&descAlignY=60&animation=fadeIn" />

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Orbitron&weight=700&size=24&duration=2800&pause=700&color=E100FF&center=true&vCenter=true&width=900&lines=Award-Worthy+UX+for+Complaint+Management;Fast+Submission+%7C+Role-Based+Access+%7C+Traceable+Workflow;Built+with+Django+%2B+DRF+for+Reliability+at+Scale)](https://git.io/typing-svg)

<p>
  <img src="https://img.shields.io/badge/Django-4.2+-0f172a?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/DRF-API-7c3aed?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Pytest-Tested-06b6d4?style=for-the-badge&logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/Secure-Role%20Guarded-22c55e?style=for-the-badge&logo=shield&logoColor=white" />
</p>

</div>

---

## ✨ Why this feels “award-winning”

- 🌌 **3D visual identity** with animated hero banner and neon cyber style
- ⚡ **Smooth complaint lifecycle** from submission to privileged admin handling
- 🔐 **Strong access control** for HOD/Principal routes, server-side enforced
- 🧠 **Smart enrichment flow** with deterministic behavior in test/SQLite contexts
- 🎯 **Anonymous-ready intake** for safer reporting experiences

---

## 🚀 Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🔧 Environment

Create `.env` (or export vars) with:

```env
ADMIN_SECRET_KEY=changeme
DJANGO_SECRET_KEY=changeme-dev
DEBUG=true
```

> The admin-access login requires `ADMIN_SECRET_KEY`. Never use default values in production.

---

## 🧪 Tests

```bash
pytest -q
```

During tests (and with SQLite), complaint enrichment runs synchronously for deterministic behavior.
You can force this mode with:

```env
SYNC_ENRICH=true
```

---

## 🛡️ Access & Behavior Notes

- Admin UI appears only for HOD/Principal group users or users with `is_hod` / `is_principal` flags.
- Server-side authorization protects admin endpoints even if UI elements are hidden.
- Anonymous complaint submission is supported when `anonymous=true` is supplied.

---

<div align="center">

### 🌠 Built to look premium. Engineered to stay practical.

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00DBDE,100:FC00FF&height=3&section=footer" />

</div>
