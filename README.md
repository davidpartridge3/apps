# Dave's Apps — project bundle

Everything needed to run, edit and deploy the apps.

## What's here

| Path | What it is |
|---|---|
| `dist/` | The deployable site (three apps). Upload the **contents** of this folder to GitHub Pages. |
| `dist/kitchen/` | Weekly Kitchen — recipes, cook mode, planner, shopping mode, timers. |
| `dist/workout/` | Hypertrophy Hub — plan, rest timers, set logging, body log. |
| `dist/betting/` | Edge — no-vig odds, +EV, CLV log, quarter-Kelly, honest P&L (hand-authored). |
| `dist/SETUP.md` | Tap-by-tap iPhone install guide. |
| `src/recipe/` | Build script + recipe and ingredient-guide data for the kitchen app. |
| `src/workout/` | Build script for the workout app. |
| `DEVELOPMENT.md` | How the apps are built. **Read before changing anything.** |
| `BACKLOG.md` | Original specs — all items now built (see the STATUS note at the top). |
| `test/verify.mjs` | Playwright check: both generated apps render with JS off **and** on. |
| `test/betting.mjs` | Playwright check: the betting math matches hand-computed values. |
| `skill/daves-apps.skill` | Drop this into Cowork so it picks up the conventions automatically. |

## Build & verify (Windows)

```bash
python build.py                                      # regenerate kitchen + workout into dist/
python -m http.server 8123 --directory dist          # serve locally
node test/verify.mjs                                  # JS-off/on checks (needs the server)
node test/betting.mjs                                 # betting math checks
```

Service workers are **auto-versioned** from a content hash — no manual cache bump. The betting app is a hand-authored single file (no generator); edit `dist/betting/index.html` directly.

## To hand this to Cowork

Start a Cowork session, attach `daves-apps.skill` and this whole folder, and say:

> Here's my apps project. Read DEVELOPMENT.md and BACKLOG.md, then start on A1 — planning the week with Laurel.

## To rebuild

```bash
cd src/recipe  && python3 build_app.py
cd src/workout && python3 build_workout.py
```

Both scripts use absolute paths — update them for wherever the repo lives.
