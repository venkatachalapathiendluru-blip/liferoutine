# Team Workflow & Sharing Guide

This page covers how to **share the project**, **collaborate as a team on GitHub**, and
run a clean git workflow. It is written for a small team (1–8 people) using
GitHub + a free Vercel deployment.

---

## 1. Share the project (read-only)

The simplest way to share is to put the repo on GitHub as a **public** repository:

```bash
cd liferoutine
git init
git add .
git commit -m "chore: initial commit of LifeRoutine 360"
git branch -M main
git remote add origin https://github.com/<your-account>/liferoutine.git
git push -u origin main
```

> Before the very first push, run `git status` and confirm the `.gitignore` entries
> are picked up:
> ```bash
> git status --short   # db.sqlite3, cookies.txt, csrf.txt, .env must NOT be listed as "to be committed"
> ```

Anyone can then:
- **View** it: `https://github.com/<your-account>/liferoutine`
- **Clone** it: `git clone https://github.com/<your-account>/liferoutine`
- **Use it** without account: on GitHub, **Code → Download ZIP**. (Note: for local
  dev use the `server.py` instructions in the README, not the repo's static preview.)

You can also share a **live demo** with zero accounts: deploy to Vercel
(`vercel --prod`) and send the `*.vercel.app` URL (see `docs/DEPLOYMENT.md`).

---

## 2. Add teammates and make the project theirs

### Option A — give them write access (private/team repo)

1. GitHub → repo → **Settings → Collaborators → Add people** (or add the repo to a
   **team** under an organization).
2. They clone with write access and push their own branches.

### Option B — open-source style (public repo)

Anyone can clone and fork.

1. Teammate clicks **Fork** (their copy of the repo).
2. They clone their fork, work, and open a **Pull Request (PR)** back to `main`.
3. You review and merge.

### Option C — start the repo yourself then invite

If the repo lives under *only one* person's account, that person should
[transfer it](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository)
to an **organization** so everyone has a fair share of ownership.

---

## 3. Daily git workflow

### 3.1 Always pull before you start

```bash
git pull origin main
git checkout -b feature/water-logging   # branch per task
```

### 3.2 Commit small, commit often

```bash
git add <files-you-changed>             # not `git add .` unless you checked first
git commit -m "feat(water): add manual ml input on tracker"
git push -u origin feature/water-logging
```

### 3.3 Open a pull request

- GitHub → **Compare & pull request** → base `main` ← your branch.
- Write a short description: what changed, how to test, screenshots if visual.
- GitHub Actions (if you add them later) run on every PR; watch the checks.

### 3.4 Review & merge

- The reviewer pulls the branch, runs it, clicks **Approve**, then **Merge**.
- After merging, delete the branch (GitHub offers this automatically).

### 3.5 Everyone else

```bash
git checkout main
git pull origin main
```

---

## 4. Branch naming & commit message conventions

**Branches:** `feature/<short-name>`, `fix/<short-name>`, `docs/<short-name>`,
`chore/<short-name>`.

**Commits (Conventional Commits — keeps history readable):**

```
feat(water): add manual ml input
fix(planner): correct end-date when range is 1 day
docs(readme): add setup instructions
chore(server): allow port override
```

Prefixes: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `perf`.

---

## 5. Dealing with conflicts

(You and a teammate edited the same line.)

```bash
git fetch origin
git checkout main && git pull origin main
git checkout <your-branch> && git merge main
# resolve conflicts in the marked files (<<<<<<< / ======= / >>>>>>>)
git add <resolved-files>
git commit -m "merge: resolve conflicts with main"
git push
```

Keep branches short-lived (`git checkout -b ...`) to minimise conflicts.

---

## 6. Code review checklist for this project

- [ ] Run `python3 server.py`; all four routes 200.
- [ ] `code` change doesn't type a path like `/home/<someone>` into any file
      (all paths must be portable).
- [ ] `.py` files stay Python 3.10-compatible (no nested f-strings with same quotes).
- [ ] No new secrets: `cookies.txt`, `csrf.txt`, `.env`, `db.sqlite3` stay ignored.
- [ ] `requirements.txt` updated if a new Python dependency was added.
- [ ] CDN libraries stay on a pinned version (e.g. Bootstrap `5.3.0`).

---

## 7. Adding a new team member (10-minute onboarding)

1. Add them to the GitHub org/repo.
2. They run:
   ```bash
   git clone <repo-url>
   python3 server.py          # frontend works immediately
   ```
3. (If they'll touch Python engine tests) setup:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Point them at `README.md` (run/test/deploy) → `docs/TESTING.md` → this file.
5. First task: a tiny PR (even a one-line docs fix) so the merge flow is muscle-memory.

---

## 8. Keep history clean

```bash
git pull --rebase            # on shared branches, rebase instead of merge commits
git log --oneline --graph    # review history shape
```

Never force-push to a shared branch (`main`). If you must rewrite a *private* branch,
that's fine (you're the only one on it).