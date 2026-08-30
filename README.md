# LifeRoutine 360

A personal daily-health web app that helps you plan meals, track water intake, and review end-of-day summaries. It ships as a **static web app** (no build step, no framework) plus an **optional Django backend** for experiments and Python-based health engines.

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

| Page | What it does |
|------|--------------|
| **Meal Planner** (`index.html`) | Generate a 1–7 day (or custom) meal plan. Check foods per meal (Early Morning, Breakfast, Lunch, Snacks, Dinner) and see per-meal + daily calories that update live. |
| **Water Tracker** (`water-tracker.html`) | Log daily water intake; monitor progress vs. a target (default 3000 ml). |
| **Daily Summary** (`summary.html`) | End-of-day health summary across tasks, water intake, and calories with an overall score and recommendations. |
| **Food Admin** (`admin.html`) | Manage the food & ingredient catalog and use the calorie calculator (meal and daily totals). |

Data is stored in your browser's `localStorage` — no account or server needed.

---

## Tech Stack

- **Frontend:** HTML5, CSS3, vanilla JavaScript (ES6 classes), Bootstrap 5 (CDN), Bootstrap Icons.
- **Storage:** Browser `localStorage`.
- **Local server:** Python `http.server` based router (`server.py`).
- **Backend (optional):** Django 5.2 + SQLite (`liferoutine360/`).
- **Deployment:** Vercel (static hosting via `vercel.json`).

---

## Project Structure

```
liferoutine/
├── index.html              # Meal Planner (home page)
├── summary.html            # Daily Summary
├── admin.html              # Food/ingredient admin + calculator
├── water-tracker.html      # Water tracker
│
├── server.py               # Local Python dev server with URL routing
├── vercel.json             # Vercel deployment config (production)
├── .vercelignore           # Files excluded from Vercel deploys
│
├── food-models.js          # Food/Ingredient/CalorieCalculator models (localStorage)
├── script.js               # Meal planner UI logic
├── water-intake.js         # Water intake manager
├── water-tracker.js        # Water tracker UI logic
├── summary.js              # Summary UI logic
├── admin-script.js         # Admin UI logic
├── auth-system.js          # Client-side role/module demo (DEMO ONLY)
│
├── routine_engine.py       # Daily timeline generation (Python)
├── daily_summary_engine.py # Daily summary scoring (Python)
├── water_demo.py           # Water scheduling algorithm demo (standalone)
├── test_timeline.py        # Timeline engine test
├── test_water_engine.py    # Water engine test
│
├── liferoutine360/         # [OPTIONAL] Django backend prototype
│   ├── manage.py
│   └── liferoutine360/settings.py
│
├── requirements.txt        # Python dependencies (backend)
└── docs/                   # Documentation
    ├── TESTING.md
    ├── DEPLOYMENT.md
    └── TEAM_WORKFLOW.md
```

> Note: the Django app (`liferoutine360/`) is an optional, experimental backend. The
> deployed product is the static site. See [DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Requirements

- **Python 3.10+** (`python3` in your terminal)
- A web browser
- (Optional) **Git** + **GitHub account** for version control/sharing
- (Optional) `pip` + a virtual environment for the Django backend

Check your versions:

```bash
python3 --version
git --version      # optional
```

---

## Run Locally

```bash
cd liferoutine
python3 server.py
```

Open [http://localhost:8000/](http://localhost:8000/) and use the navbar:

| URL | Page |
|-----|------|
| `http://localhost:8000/` | Meal Planner |
| `http://localhost:8000/summary/` | Daily Summary |
| `http://localhost:8000/water/` | Water Tracker |
| `http://localhost:8000/admin/` | Food Admin |

Stop the server with `Ctrl+C`.

> Why `server.py` and not just opening `index.html`? The app loads JS modules and
> relies on `localStorage`, and the nice `/summary/`, `/water/`, `/admin/` routes come
> from `server.py`. You can also run `python3 -m http.server 8000` but then you must
> visit `index.html` / `summary.html` directly (no pretty routes).

### Running the Django backend (optional / experimental)

```bash
cd liferoutine

# 1) one-time setup
python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) initialize the database
cd liferoutine360
python3 manage.py migrate

# 3) create a superuser (optional, for Django admin)
python3 manage.py createsuperuser

# 4) run the dev server
python3 manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and use the Django admin at
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

---

## Testing

See **[docs/TESTING.md](docs/TESTING.md)** for the full guide. Quick start:

```bash
# Frontend routes (expect HTTP 200 for each)
python3 server.py &        # then curl /, /summary/, /water/, /admin/
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/

# Standalone Python engines (no dependencies)
python3 routine_engine.py
python3 daily_summary_engine.py
python3 water_demo.py

# Engine tests (require Django + `pip install -r requirements.txt`)
python3 test_timeline.py
python3 test_water_engine.py

# Django project checks & tests
cd liferoutine360
python3 manage.py check
python3 manage.py test
```

---

## Deployment (Production)

The static site is **Vercel-ready** (`vercel.json`). In under a minute:

```bash
npm i -g vercel          # once
cd liferoutine
vercel --prod
```

You'll receive a live URL like `https://liferoutine.vercel.app`. See
**[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for Vercel details, custom domains, and
notes about the (separate) Django backend deployment.

---

## Sharing & Team Workflow

The project is ready to share and collaborate on. The workflow is:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<you>/liferoutine.git
git push -u origin main
```

Then teammates `git clone` it, Git-tracked changes flow through branches + pull
requests. Full guide — including branch names, commit style, PR etiquette, and how to
bring new members on board — is in **[docs/TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md)**.

---

## Data & Privacy

- All user-entered data (meals, foods, water) lives **only in the browser's
  `localStorage`** per device. Clearing browser data resets the app.
- `cookies.txt`, `csrf.txt`, `.env`, and the Django `db.sqlite3` are **git-ignored and
  Vercel-ignored** — they are never deployed or committed.
- The `auth-system.js` file uses a trivial client-side "hash" and is a **demo only** —
  never use it for real security.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3` not found | Install Python 3.10+ from python.org or your package manager. |
| Port 8000 in use | Run `python3 server.py 8001` or stop the other process (`kill %1` in the shell that started it). |
| Page loads but no data saves | `localStorage` may be blocked (private mode / strict settings). Use a normal browser tab. |
| `ModuleNotFoundError: django` | `pip install -r requirements.txt` (or inside a venv — see above). |
| Vercel build shows Python files | Fine by design; `.vercelignore` excludes `*.py`, `*.md`, the Django app, and secrets from the deploy. |

---

## License

Copyright © 2024 LifeRoutine 360. All rights reserved. No license is granted for reuse
or redistribution without permission.