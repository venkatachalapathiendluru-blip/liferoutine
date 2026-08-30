# Deployment Guide (Production)

The product you ship is the **static site** (the HTML/CSS/JS in the project root).
The Django app in `liferoutine360/` is an optional experimental backend and is
**excluded from this deployment** (both from Vercel via `.vercelignore` and from git
via `.gitignore`'s `db.sqlite3`).

Recommended hosting: **Vercel** — it is free, needs zero configuration, and this
project already includes `vercel.json`.

---

## 1. Deploy to Vercel (recommended)

### 1.1 One-time setup

```bash
npm i -g vercel        # installs the Vercel CLI globally
vercel login           # opens a browser to authenticate
```

### 1.2 Deploy (first time)

From the project root:

```bash
cd liferoutine
vercel --prod
```

The CLI detects the static site (via `vercel.json`), uploads it, and returns a URL,
e.g.:

```
https://liferoutine.vercel.app
```

This is your **production URL** — share it with anyone. There is no browser
interaction needed if you're already logged in.

### 1.3 Subsequent deploys (and previews)

```bash
vercel              # deploy a preview + production alias in one command
vercel --prod       # directly to production
vercel --prod --yes # skip prompts (CI-friendly)
```

Every non-`--prod` deploy creates a unique **preview URL** — great for showing
teammates a change before it goes live.

### 1.4 What `vercel.json` does

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "rewrites": [
    { "source": "/summary", "destination": "/summary.html" },
    { "source": "/admin",   "destination": "/admin.html" },
    { "source": "/water",   "destination": "/water-tracker.html" }
  ]
}
```

It maps the pretty routes `/summary`, `/admin`, `/water` to their files, matching the
behaviour of the local `server.py`.

### 1.5 What is NOT deployed

`.vercelignore` excludes from every deploy:

- the `liferoutine360` Django app (and all `*.py`)
- `*.md` documentation
- secrets: `cookies.txt`, `csrf.txt`, `.env`

If you ever *do* plan to ship secrets to Vercel, set them as
[environment variables](https://vercel.com/docs/projects/environment-variables) in
the project settings — never in the repo.

### 1.6 Custom domain (optional)

In the Vercel dashboard → your project → **Settings → Domains**, add `www.yourdomain.com`.
Your DNS provider (or Vercel's nameservers) then point the domain at the deployment.

---

## 2. Alternative: static hosting anywhere

Because the site is 100% static, it also deploys to:
- **GitHub Pages** (Settings → Pages → select `main` branch) — free, public.
- **Netlify** (drag-and-drop the project folder).
- Any web server that serves static files (Apache, Nginx, cPanel).

For these, the `/summary`, `/admin`, `/water` pretty routes won't work without extra
config; use the `.html` filenames directly instead.

---

## 3. Deploying the Django backend (only if you need it live)

The Django app is **not production-configured**:

- `settings.py` has `DEBUG = True` and a hard-coded `SECRET_KEY` — never expose this.
- SQLite is built for local dev, not concurrent web traffic.

If the backend must run in production:

```bash
# safety first: set env-driven settings (do NOT hard-code secrets)
export DEBUG=0
export SECRET_KEY='a-long-random-string'
export DJANGO_ALLOWED_HOSTS='yourdomain.com'

cd liferoutine/liferoutine360
python3 manage.py collectstatic
```

Deploy options:
- **Render / Railway / Fly.io**: push the `liferoutine360/` folder, run
  `pip install -r requirements.txt && python3 manage.py migrate && gunicorn liferoutine360.wsgi`.
- **AWS/VPS**: run behind Nginx/Gunicorn with HTTPS.

These options need CI config + a real database tweak (`settings.py` → Postgres). This
is out of scope for the current product — the static deploy covers the user-facing app.

---

## 4. Production checklist

- [ ] `vercel --prod` returns a live HTTPS URL.
- [ ] `/`, `/summary`, `/water`, `/admin` all load (200) on the live URL.
- [ ] No `cookies.txt` / `csrf.txt` / `.env` / `db.sqlite3` inside the bundle
      (run `vercel build` then inspect `.vercel/output` if unsure).
- [ ] Browser `localStorage` works on the live domain.
- [ ] A teammate clones from GitHub and can run + deploy independently (see
      `docs/TEAM_WORKFLOW.md`).