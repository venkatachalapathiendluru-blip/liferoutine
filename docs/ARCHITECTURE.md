# Architecture

## Overview

LifeRoutine 360 is a single Django project. Django serves the product front-end as
templates/static assets, and also hosts experimental backend apps (accounts, planning,
nutrition, water, payments, core).

- **Product layer** (what users see): the four pages in the `web` app.
- **App data layer**: lives entirely in the browser's `localStorage` (meals, foods,
  water) — Django only delivers the page + assets.
- **Experimental layer**: `accounts`, `planning`, `nutrition`, `water`, `payments`,
  `core` — work-in-progress server-side features.

## 1. Product layer (`web` app)

### Routes

| Route | View | Template |
|-------|------|----------|
| `/` | `web.views.meal_planner` | `templates/web/index.html` |
| `/water/` | `web.views.water_tracker` | `templates/web/water-tracker.html` |
| `/summary/` | `web.views.daily_summary` | `templates/web/summary.html` |
| `/food-admin/` | `web.views.food_admin` | `templates/web/admin.html` |
| `/admin/` | Django admin (login required) | — |

The `web.urls` include comes **first** in the project `urlpatterns`, so the product
pages own the clean routes; the experimental apps' sub-paths (e.g. `/water/track/`,
`/accounts/login/`) still resolve by falling through to their own includes.

### Page → logic mapping

| Page                 | JS driving it                |
|----------------------|------------------------------|
| `index.html`         | `script.js` + `food-models.js` + `water-intake.js` |
| `water-tracker.html` | `water-tracker.js` + `water-intake.js` |
| `summary.html`       | `summary.js`                 |
| `admin.html`         | `admin-script.js` + `food-models.js` |

Assets live in `static/web/` and are referenced via `{% static 'web/...' %}` so Django
hashed filenames apply in production.

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

- Renders one day-card per date; each card has 5 meal sections + water row.
- Checkboxes store `date → meal → [foodIds]` under `localStorage['mealPlannerData']`.
- Calorie totals recompute on every checkbox change
  (`updateMealCalories` → `updateDailyCalories`).

### Water intake (`water-intake.js` → used by planner + tracker)

- `WaterIntakeManager` tracks consumed ml vs. a daily target (default 3000 ml) per
  date, giving progress/remaining.

### Auth (`auth-system.js`)

- Demo-only client-side role/module system (`authManager`). Not linked from any page.
- **Warning:** `hashPassword` uses base64 — it is not real security.

## 2. Python engines (inside the Django project)

Stdlib-only modules shipped within `liferoutine360/`:

| Module | Responsibility |
|--------|----------------|
| `liferoutine360/routine_engine.py` | Builds a daily timeline (wake/water/walk/meals/sleep) from a wake-up time; personalises descriptions by health plan + veg preference. Used by the `planning` app. |
| `liferoutine360/water/engine.py` | DB-backed `WaterIntakeEngine` (`WaterGoal`, `WaterSchedule`, `WaterTimeSlot` models). |

## 3. Django layer (`liferoutine360/`)

- Standard Django 5.2 layout: `manage.py`, `liferoutine360/settings.py`, SQLite DB.
- Apps: `web` (product) + `accounts`, `planning`, `nutrition`, `water`, `payments`,
  `core` (experimental).
- `water/engine.py` holds the DB-backed `WaterIntakeEngine`
  (`WaterGoal`, `WaterSchedule`, `WaterTimeSlot` models).
- `planning` defines `Timeline` (used to derive wake-up and meal times).
- Static: `STATICFILES_DIRS` points at `static/` (dev), `STATIC_ROOT` at
  `staticfiles/` (built by `collectstatic`, served by Whitenoise).

## 4. Data flows

```
Browser UI  ──►  FoodManager / MealPlanner / WaterIntakeManager
                    │  localStorage (JSON)
                    ▼
          per-device persistence (no server)
```

No first-party network calls happen at runtime (Bootstrap/Icons load from CDN at page
load).

## 5. Deployment topology

```
git push (GitHub) ──► Render / Railway
                          │  gunicorn liferoutine360.wsgi
                          ▼
            https://liferoutine.onrender.com  (Django + Whitenoise)
```

See `docs/DEPLOYMENT.md`. Secrets (`.env`, `db.sqlite3`), `cookies.txt`, `csrf.txt`,
and the build output `staticfiles/` are git-ignored.