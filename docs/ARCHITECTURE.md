# Architecture

## Overview

LifeRoutine 360 has two independent layers:

1. **Static web app (production)** — the files in the project root. Runs entirely in
   the browser, persisted with `localStorage`. Deployed to Vercel.
2. **Django backend (optional/experimental)** — the `liferoutine360/` folder. A model
   for future per-user accounts and server-side data. Not deployed.

## 1. Static app layer

### Page → logic mapping

| Page                 | JS driving it                |
|----------------------|------------------------------|
| `index.html`         | `script.js` + `food-models.js` + `water-intake.js` |
| `water-tracker.html` | `water-tracker.js` + `water-intake.js` |
| `summary.html`       | `summary.js`                 |
| `admin.html`         | `admin-script.js` + `food-models.js` |

### Domain model (`food-models.js`)

```
FoodManager (catalog, localStorage 'foodManagerData')
 ├── foods[]  ├── ingredients[]
 ├── Food { name, category, calories_per_unit, unit, ingredients[] }
 ├── Ingredient { name, calories_per_unit, unit }
 └── CalorieCalculator { calculateMealCalories(), calculateDailyTotal() }
```

- `Food.calculateCalories()` sums its ingredient calories, or falls back to
  `calories_per_unit` when it has no ingredients.
- `FoodManager` seeds default data on first run and serialises to JSON.

### Meal planner (`script.js`)

- Renders one day-card per date; each card has 5 meal sections +
  water row.
- Checkboxes store `date → meal → [foodIds]` under
  `localStorage['mealPlannerData']`.
- Calorie totals recompute on every checkbox change
  (`updateMealCalories` → `updateDailyCalories`).

### Water intake (`water-intake.js` → used by planner + tracker)

- `WaterIntakeManager` tracks consumed ml vs. a daily target
  (default 3000 ml) per date, giving progress/remaining.

### Auth (`auth-system.js`)

- Demo-only client-side role/module system (`authManager`).
- **Warning:** `hashPassword` uses base64 — it is not real security. The production
  static app stores no account data.

### Routing / server

- `server.py` — a `SimpleHTTPRequestHandler` subclass that maps
  `/summary/`, `/water/`, `/admin/` to the `.html` files and serves static files.
- `vercel.json` mirrors the same rewrites for production (Vercel rewrite table).

## 2. Python engines (shared logic, portable to backend)

Standalone, stdlib-only modules that a future backend (or the admin) can reuse:

| Module | Responsibility |
|--------|----------------|
| `routine_engine.py` | Builds a daily timeline (wake/water/walk/meals/sleep) from a wake-up time; personalises descriptions by health plan + veg preference. |
| `daily_summary_engine.py` | Scores a day (tasks 40% / water 30% / calories 30%), generates a message + recommendations, weekly trend analysis. |
| `water_demo.py` | Pure-python reference algorithm: splits a water target into 8–10 slots that avoid ±30 min around meals. |

Tests for the engines (`test_timeline.py`, `test_water_engine.py`) import the Django
project for DB-backed pieces, driven by `django.setup()`.

## 3. Django layer (`liferoutine360/`)

- Standard Django 5.2 layout: `manage.py`, `liferoutine360/settings.py`, SQLite DB.
- Apps: `accounts`, `planning`, `nutrition`, `water`, `payments`, `core`.
- `water/engine.py` holds the DB-backed `WaterIntakeEngine`
  (`WaterGoal`, `WaterSchedule`, `WaterTimeSlot` models).
- `planning` defines `Timeline` (used to derive wake-up and meal times).

> Keep this layer optional: the deployed product must never depend on it.

## 4. Data flows

```
Browser UI  ──►  FoodManager / MealPlanner / WaterIntakeManager
                    │  localStorage (JSON)
                    ▼
          per-device persistence (no server)
```

No network calls happen at runtime (Bootstrap/Icons load from CDN at page load).

## 5. Deployment topology

```
git push (GitHub) ──► Vercel (via .vercelignore exclusions)
                        │
                        ▼
              https://liferoutine.vercel.app  (static edge CDN)
```

`.vercelignore` keeps the Django app, Python files, docs, and secrets off the CDN.