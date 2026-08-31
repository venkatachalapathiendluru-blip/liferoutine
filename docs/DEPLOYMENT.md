# Deployment Guide (Production)

LifeRoutine 360 is a **Django 5.2 + SQLite** app that also serves the product
front-end. The app data lives in `localStorage` on the browser, so the deploy is a
plain Django/WSGI deployment — no CDN, no separate static server.

Recommended hosts: **Render** or **Railway** (both have free tiers that run Django
with Gunicorn + Whitenoise).

---

## 1. What runs in production

- **App server:** Gunicorn running `liferoutine360.wsgi`.
- **Static files:** served by WhiteNoise from `staticfiles/` (built by
  `collectstatic`). No extra CDN needed.
- **Routes:** `/` (Meal Planner), `/summary/`, `/water/`, `/food-admin/` are product
  pages. `/admin/` is the Django admin.
- **Database:** SQLite by default. Fine for small traffic; switch to Postgres via
  `DJANGO_DATABASE_URL` if you need concurrency (see section 4).

---

## 2. Environment variables

| Variable | Required | Example |
|----------|----------|---------|
| `DJANGO_SECRET_KEY` | Yes (prod) | `a-long-random-string` |
| `DJANGO_DEBUG` | Yes (prod) | `False` |
| `DJANGO_ALLOWED_HOSTS` | Yes (prod) | `liferoutine.onrender.com,www.example.com` |

`settings.py` reads these at startup; without them it falls back to insecure local
defaults (safe for development only). Never paste the real secret into the repo.

---

## 3. Deploy to Render (recommended)

### 3.1 One-time setup

1. Push the repo to GitHub (already done).
2. On [render.com](https://render.com) → **New → Web Service** → connect the
   `liferoutine` repo.
3. Fill in the service settings:

| Field | Value |
|-------|-------|
| Name | `liferoutine` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt && python3 manage.py collectstatic --noinput && python3 manage.py migrate` |
| Start Command | `gunicorn liferoutine360.wsgi` |
| Instance Type | Free |

4. In **Environment**, add:
   - `DJANGO_SECRET_KEY` — generate one, e.g. `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
   - `DJANGO_DEBUG` = `False`
   - `DJANGO_ALLOWED_HOSTS` = your `*.onrender.com` URL (added automatically after first deploy)

### 3.2 Deploy

Render auto-deploys on every push to `main`. You get a live URL like:

```
https://liferoutine.onrender.com
```

### 3.3 Re-deploying after changes

Just `git push origin main` — Render rebuilds and releases.

---

## 4. Production checklist

- [ ] `DJANGO_DEBUG` is `False` and a real `DJANGO_SECRET_KEY` is set.
- [ ] `DJANGO_ALLOWED_HOSTS` includes the live domain.
- [ ] `/`, `/summary/`, `/water/`, `/food-admin/` all load (200) on the live URL.
- [ ] Static assets load (browser console shows no 404s for `/static/web/...`).
- [ ] No `cookies.txt` / `csrf.txt` / `.env` / `db.sqlite3` / `staticfiles/` were
      committed (check `git log --stat` / `.gitignore`).
- [ ] A teammate clones from GitHub and can run + deploy independently (see
      `docs/TEAM_WORKFLOW.md`).

> Switching to Postgres (optional): set a `DJANGO_DATABASE_URL`-style variable and
> adjust `settings.py` to read it (e.g. with `dj-database-url`). For the current
> product the database is unused by the front-end, so SQLite is acceptable.

---

## 5. Local production check (before pushing)

```bash
cd liferoutine360
python3 manage.py check --deploy   # flags insecure settings worth fixing
python3 manage.py test
```