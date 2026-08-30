# Testing Guide

This guide explains how to test every part of the project: the Django routes, the
standalone Python engines, and manual browser checks.

## 1. Prerequisites

```bash
python3 --version        # 3.10+
git --version            # optional
cd liferoutine

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Django project checks & tests

```bash
cd liferoutine/liferoutine360
python3 manage.py check               # "System check identified no issues (0 silenced)."
python3 manage.py check --deploy      # flags deployment-safety issues (debug/secret/hosts)
python3 manage.py test                # Django test suites (web/accounts/planning/nutrition/water/payments/core)
```

The `web` suite tests that every product page returns 200:

```
/ -> 200
/summary/ -> 200
/water/ -> 200
/food-admin/ -> 200
```

## 3. Route smoke test (live server)

Start Django, then hit every route:

```bash
cd liferoutine360
python3 manage.py runserver 127.0.0.1:8000 &
sleep 3

for path in "/" "/summary/" "/water/" "/food-admin/"; do
  echo -n "$path -> "
  curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8000$path"
done

# stop the server
kill %1
```

Expected output:

```
/ -> 200
/summary/ -> 200
/water/ -> 200
/food-admin/ -> 200
```

Also confirm static assets load: `curl -s -o /dev/null -w "%{http_code}\n"
http://127.0.0.1:8000/static/web/script.js` → `200`.

## 4. Engine & app tests

```bash
cd liferoutine
python3 manage.py test   # runs all app tests (web, accounts, planning, nutrition, water, payments, core)
```

The Django project's app tests live in each app's `tests.py` (e.g.
`liferoutine360/water/tests.py` for the DB-backed water engine) plus
`liferoutine360/test_dashboard.py` as a manual admin-dashboard script.

## 5. Manual browser checklist

After `python3 manage.py runserver`, verify in a browser:

1. **Meal Planner** (`http://127.0.0.1:8000/`)
   - Generate a 7-day plan → one card appears per day with 5 meal sections + water row.
   - Check a food → the meal calorie count and the day's total update immediately.
   - Click **Save** → a "Saved" indicator flashes; data persists after refresh.
2. **Water Tracker** (`http://127.0.0.1:8000/water/`)
   - Log water → progress updates (`consumed / target ml` and percentage).
3. **Summary** (`http://127.0.0.1:8000/summary/`)
   - Loads the daily summary view and shows score/tasks/water/calories sections.
4. **Food Admin** (`http://127.0.0.1:8000/food-admin/`)
   - Add a food and an ingredient; both appear in the catalog.
   - Calorie calculator: add a food + quantity to a meal → totals update.
5. **Navbar** — the Meal Planner / Water Tracker / Summary / Accounts links all
   navigate to working routes (no 404s).

## 6. Cross-device check

Because data is stored in `localStorage`, each browser/device is independent. A
"Save" in Chrome will not appear in Firefox, or on another computer. This is
expected behaviour, not a bug.

## 7. Gotchas

- Always reset `localStorage` (DevTools → Application → Clear storage) before
  re-testing default seed data.
- If anything fails, the parent app uses `localStorage` keys:
  `mealPlannerData`, `foodManagerData`, and `liferoutine_*`.
- `staticfiles/` is build output — run `collectstatic` after changing files in
  `static/`; the dev server serves `static/` directly so no step is needed locally.