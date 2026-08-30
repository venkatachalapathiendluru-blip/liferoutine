# LifeRoutine 360

A personal daily-health web app that helps you plan meals, track water intake, and
review end-of-day summaries. The product front-end is served by **Django 5 + SQLite**
(no separate static server), with the Python health engines alongside for tests.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Requirements](#requirements)
5. [Run Locally](#run-locally)
6. [Testing](#testing)
7. [Deployment (Production)](#deployment-production)
8. [Sharing & Team Workflow](#sharing--team-workflow)
9. [Data & Privacy](#data--privacy)
10. [Troubleshooting](#troubleshooting)
11. [License](#license)

---

## Features

| Page | Route | What it does |
|------|-------|--------------|
| **Meal Planner** | `/` | Generate a 1–7 day (or custom) meal plan. Check foods per meal (Early Morning, Breakfast, Lunch, Snacks, Dinner) and see per-meal + daily calories that update live. |
| **Water Tracker** | `/water/` | Log daily water intake; monitor progress vs. a target (default 3000 ml). |
| **Daily Summary** | `/summary/` | End-of-day health summary across tasks, water intake, and calories with an overall score and recommendations. |
| **Food Admin** | `/food-admin/` | Manage the food & ingredient catalog and use the calorie calculator (meal and daily totals). |

Data is stored in your browser's `localStorage` — no account or server needed.

---

## Tech Stack

- **Frontend:** HTML5, CSS3, vanilla JavaScript (ES6 classes), Bootstrap 5 (CDN), Bootstrap Icons.
- **Server & routing:** Django 5.2 serving the pages as templates.
- **Storage:** Browser `localStorage` (app data) + SQLite (Django).
- **Static files:** django staticfiles + Whitenoise for production.
- **Python engines:** `routine_engine.py`, `daily_summary_engine.py`, `water_demo.py` (stdlib-only).
- **Deployment:** Render / Railway / any WSGI host (see `docs/DEPLOYMENT.md`).

---

## Project Structure

```
liferoutine/
├── requirements.txt        # Python dependencies (Django, Whitenoise)
├── docs/                   # Documentation
│   ├── TESTING.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── TEAM_WORKFLOW.md
│
├── routine_engine.py       # Daily timeline generation (Python)
├── daily_summary_engine.py # Daily summary scoring (Python)
├── water_demo.py           # Water scheduling algorithm demo (standalone)
├── test_timeline.py        # Timeline engine test
├── test_water_engine.py    # Water engine test
│
└── liferoutine360/         # Django project (product + backend experiments)
    ├── manage.py
    ├── liferoutine360/     # settings.py, urls.py, wsgi.py ...
    ├── web/                # Product pages (views, urls, tests)
    ├── templates/web/      # meal planner / summary / water / food-admin
    ├── static/web/         # the app's JS + CSS
    ├── accounts/           # login/register/profile app
    ├── planning/           # experimental backend app (timelines)
    ├── nutrition/          # experimental backend app
    ├── water/              # experimental backend app (DB water engine)
    ├── payments/           # experimental backend app
    └── core/               # experimental dashboard app
```

---

## Requirements

- **Python 3.10+** (`python3` in your terminal)
- **Django 5.2** and **Whitenoise** (installed via `requirements.txt`)
- A web browser
- (Optional) **Git** + **GitHub account** for version control/sharing

Check your versions:

```bash
python3 --version
git --version      # optional
```

---

## Run Locally

```bash
cd liferoutine

# 1) one-time setup
python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) initialize the database
cd liferoutine360
python3 manage.py migrate

# 3) (optional) create a superuser for Django admin
python3 manage.py createsuperuser

# 4) run the dev server
python3 manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and use the navbar:

| URL | Page |
|-----|------|
| `http://127.0.0.1:8000/` | Meal Planner |
| `http://127.0.0.1:8000/water/` | Water Tracker |
| `http://127.0.0.1:8000/summary/` | Daily Summary |
| `http://127.0.0.1:8000/food-admin/` | Food Admin |
| `http://127.0.0.1:8000/admin/` | Django admin (login required) |

> The app's data lives in `localStorage`; Django only serves the pages, so you don't
> need to touch the database for the product to work. The `accounts/`, `planning/`,
> `nutrition/`, `water/`, `payments/`, `core/` apps are experimental backend features.

---

## Testing

See **[docs/TESTING.md](docs/TESTING.md)** for the full guide. Quick start:

```bash
# Django project checks & tests
cd liferoutine360
python3 manage.py check
python3 manage.py test

# Engine tests (require Django, from the project root)
cd ..
python3 test_timeline.py
python3 test_water_engine.py

# Standalone Python engines (no dependencies)
python3 routine_engine.py
python3 daily_summary_engine.py
python3 water_demo.py
```

---

## Deployment (Production)

The site is a single Django app — deploy it to any WSGI host. Recommended: **Render**
or **Railway** (free tiers). Summary:

```bash
# build command
pip install -r requirements.txt && python3 manage.py collectstatic --noinput

# start command
gunicorn liferoutine360.wsgi
```

Supply `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS=<your-domain>`
as environment variables. Static files are served by Whitenoise — no CDN setup needed.
Full details, including a `render.yaml` blueprint, are in
**[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**.

---

## Sharing & Team Workflow

The project is on GitHub and ready to collaborate on. The workflow is:

```bash
git clone git@github.com:venkatachalapathiendluru-blip/liferoutine.git
cd liferoutine
# create a branch, make changes, open a Pull Request
```

Full guide — including branch names, commit style, PR etiquette, and how to bring new
members on board — is in **[docs/TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md)**.

---

## Data & Privacy

- All user-entered data (meals, foods, water) lives **only in the browser's
  `localStorage`** per device. Clearing browser data resets the app.
- `cookies.txt`, `csrf.txt`, `.env`, `db.sqlite3`, and `staticfiles/` are
  **git-ignored** — they are never committed or deployed.
- The `auth-system.js` file uses a trivial client-side "hash" and is a **demo only** —
  never use it for real security.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3` not found | Install Python 3.10+ from python.org or your package manager. |
| Port 8000 in use | Use a different port: `python3 manage.py runserver 8001`. |
| Page loads but no data saves | `localStorage` may be blocked (private mode / strict settings). Use a normal browser tab. |
| `ModuleNotFoundError: django` | `pip install -r requirements.txt` (inside the venv — see above). |
| Static files 404 in production | Run `python3 manage.py collectstatic` in the build command (Whitenoise serves them). |
| Page loads unstyled | Check the browser console; confirm assets load from `/static/web/...`. |

---

## License

Copyright © 2024 LifeRoutine 360. All rights reserved. No license is granted for reuse
or redistribution without permission.