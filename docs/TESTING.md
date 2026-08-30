# Testing Guide

This guide explains how to test every part of the project: the frontend routes, the
standalone Python engines, the Django project, and manual browser checks.

## 1. Prerequisites

```bash
python3 --version        # 3.10+
git --version            # optional
cd liferoutine
```

For tests that use the Django backend (`test_timeline.py`, `test_water_engine.py`,
`manage.py test`) you also need Django:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Frontend smoke test (routes)

Start the server, then hit every route. Each should return `200`:

```bash
cd liferoutine
python3 server.py &
sleep 1

for path in "/" "/summary/" "/water/" "/admin/"; do
  echo -n "$path -> "
  curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8000$path"
done

kill %1
```

Expected output:

```
/ -> 200
/summary/ -> 200
/water/ -> 200
/admin/ -> 200
```

## 3. Standalone Python engines (no Django needed)

```bash
cd liferoutine
python3 routine_engine.py        # prints a timeline for a 6:00 AM wake-up
python3 daily_summary_engine.py  # prints a sample daily summary + recommendations
python3 water_demo.py            # runs 3 water-scheduling scenarios (early/standard/late)
```

All three should run to completion with no tracebacks. `water_demo.py` prints
`Match: ✓` and `Meal avoidance: ✓` for every scenario.

## 4. Engine tests (require Django)

```bash
cd liferoutine
python3 test_timeline.py     # last line: "✓ All tests passed!"
python3 test_water_engine.py # last lines: "TEST COMPLETED SUCCESSFULLY!" + "✓ ... working correctly!"
```

## 5. Django project checks

```bash
cd liferoutine/liferoutine360
python3 manage.py check               # "System check identified no issues (0 silenced)."
python3 manage.py test                # runs the Django test suites (accounts/planning/nutrition/water/payments/core)
python3 test_dashboard.py             # boots a test client; prints login/dashboard status 200
```

> `test_dashboard.py` expects `liferoutine360/liferoutine360/urls.py` to expose the
> login + dashboard routes. Run it from inside the `liferoutine360/` directory.

## 6. Manual browser checklist

After `python3 server.py`, verify in a browser:

1. **Meal Planner** (`http://localhost:8000/`)
   - Generate a 7-day plan → one card appears per day with 5 meal sections + water row.
   - Check a food → the meal calorie count and the day's total update immediately.
   - Click **Save** → a "Saved" indicator flashes; data persists after refresh.
2. **Water Tracker** (`http://localhost:8000/water/`)
   - Log water → progress updates (`consumed / target ml` and percentage).
3. **Summary** (`http://localhost:8000/summary/`)
   - Loads the daily summary view and shows score/tasks/water/calories sections.
4. **Admin** (`http://localhost:8000/admin/`)
   - Add a food and an ingredient; both appear in the catalog.
   - Calorie calculator: add a food + quantity to a meal → totals update.

## 7. Cross-device check

Because data is stored in `localStorage`, each browser/device is independent. A
"Save" in Chrome will not appear in Firefox, or on another computer. This is
expected behaviour, not a bug.

## 8. Gotchas

- `test_water_engine.py` previously used nested f-strings which only parse on Python
  3.12+. It is written to be **Python 3.10-compatible** — keep it that way.
- Always reset `localStorage` (DevTools → Application → Clear storage) before
  re-testing default seed data.
- If anything fails, the parent app uses `localStorage` keys:
  `mealPlannerData`, `foodManagerData`, and `liferoutine_*`.