# Dave's Apps — project bundle

Everything needed to run, edit and deploy the apps.

## What's here

| Path | What it is |
|---|---|
| `dist/` | The deployable site. Upload the **contents** of this folder to GitHub Pages. |
| `dist/SETUP.md` | Tap-by-tap iPhone install guide. |
| `src/recipe/` | Build script + recipe and ingredient-guide data for the kitchen app. |
| `src/workout/` | Build script for the workout app. |
| `DEVELOPMENT.md` | How the apps are built. **Read before changing anything.** |
| `BACKLOG.md` | Specs for the next round of work, including the betting tool. |
| `skill/daves-apps.skill` | Drop this into Cowork so it picks up the conventions automatically. |

## To hand this to Cowork

Start a Cowork session, attach `daves-apps.skill` and this whole folder, and say:

> Here's my apps project. Read DEVELOPMENT.md and BACKLOG.md, then start on A1 — planning the week with Laurel.

## To rebuild

```bash
cd src/recipe  && python3 build_app.py
cd src/workout && python3 build_workout.py
```

Both scripts use absolute paths — update them for wherever the repo lives.
