# Dave's Apps — developer handoff

Read this first. It explains how the two existing apps are built and the one rule that matters more than any other.

---

## The prime directive

**Everything must work with JavaScript disabled.**

Dave views these apps in previews and on devices where scripts are blocked. An earlier version rendered its content with JavaScript and showed him a blank page. Do not repeat that.

The pattern used throughout: **structure and state live in HTML and CSS; JavaScript only enhances.**

- Navigation, tabs, sheets, overlays → hidden `<input type="radio">` / `<input type="checkbox">` plus `~` sibling selectors, or `:target` with anchor links
- Timers → CSS `@keyframes` animating a strip of pre-rendered digits with `steps()`
- Check-off lists → `<input type="checkbox">` + `:checked` sibling rules
- JavaScript adds → sound, vibration, pause/adjust, date detection, shuffle, clipboard

`<body class="no-js">` is replaced with `class="js"` by the first line of script. Style JS-only affordances with `.js-only` (hidden by `.no-js .js-only{display:none}`).

**Verify both modes before shipping.** Playwright with `javaScriptEnabled: false` and `true`. Never ship on visual inspection alone.

---

## Layout

```
src/recipe/build_app.py          generates dist/kitchen/index.html
src/recipe/data/all_recipes.json 96 recipes (source of truth)
src/recipe/data/guides.json      171 ingredient shopping guides
src/workout/build_workout.py     generates dist/workout/index.html
dist/                            the deployable site (GitHub Pages root)
```

Both apps are **generated** by Python scripts. Never hand-edit `dist/*/index.html` — the change will be lost on the next build. Edit the build script or the JSON data, then rebuild:

```bash
cd src/recipe   && python3 build_app.py
cd src/workout  && python3 build_workout.py
```

Both write directly into `dist/`. Paths are absolute inside the scripts — fix them up for wherever the repo lives.

---

## The recipe app

**Data model.** `all_recipes.json` is a flat array. Each recipe:

```json
{"week": 1, "slot": "dinner|batch", "title": "...", "cuisine": "...", "blurb": "...",
 "time": "30 min", "servings": 2, "hero": "🍚",
 "ingredients": [{"item": "1 lb ground beef", "store": "TJ|Aldi|Either|Pantry"}],
 "steps": [{"text": "...", "timer": 300, "tip": "..."}],
 "swap": "...", "leftovers": "..."}
```

24 weeks, 4 recipes each (3 dinners of 2 servings + 1 batch of 6). Weeks group into months of 4. `timer` must be `null` or one of `60, 120, 180, 240, 300, 420, 480, 600, 720, 900, 1200, 1500, 1800` — the build only emits CSS countdowns for durations actually used, and an unlisted value silently produces a dead button.

**IDs are deterministic** — `w{week}r{index}`. Do not reintroduce `hash()`; Python randomises string hashes per process and IDs changed on every build.

**Ingredient guides.** `guides.json` is keyed by a normalised ingredient string. `gkey()` in the build script strips quantities, parentheses and trailing prep instructions, then matches against the guide keys. Roughly half the ingredient lines match — generic items like "garlic" deliberately have no guide. When adding recipes, run the extraction in `build_app.py` to see which new products need guide entries.

**CSS countdown mechanism.** For duration `d`, a `<div class="cd-roll">` holds `d+1` `<i>` elements (one per second, or per 10s above 600s) and is animated with `steps(n)` over `d` seconds, translating `-n em`. The ring uses `stroke-dashoffset`. Completion states are separate elements with `animation-delay: {d}s`. Restarting requires the element to have been `display:none` in between — that is why closing and reopening works and re-clicking the same control does not.

---

## The workout app

Simpler and smaller. The plan lives in a `PLAN` list at the top of `build_workout.py`. Rest timers use paired `a`/`b` radio variants per duration so the in-overlay **Restart** button always replays the animation. Changing exercises means editing `PLAN` and rebuilding.

---

## Deployment

`dist/` is the site root, deployed to GitHub Pages. It now holds **three** apps — `kitchen/`, `workout/` and `betting/` — each with `index.html`, `manifest.webmanifest`, `sw.js` and three PNG icons, plus a root `index.html` launcher.

**Service workers are now auto-versioned.** The build scripts write `sw.js` with a cache name derived from a hash of the page (`kitchen-<hash>`), so installed apps always pick up new content with no manual bump. (The betting app is hand-authored and uses a network-first page strategy, so it updates when online too.)

The **betting app (`dist/betting/`) is not generated** — it's a hand-authored single file. Edit `dist/betting/index.html` directly. The no-JavaScript rule does not apply to it (it's inherently interactive); its math is covered by `test/betting.mjs`.

**Build & verify (Windows):** `python build.py` regenerates kitchen + workout. Python lives at `C:\Users\david\AppData\Local\Programs\Python\Python312\python.exe`. Serve with `python -m http.server 8123 --directory dist`, then run `node test/verify.mjs` (JS-off/on for both generated apps) and `node test/betting.mjs`.

Dave is on iPhone. Only Safari can install to the Home Screen; Chrome and Edge cannot. Keep `apple-mobile-web-app-capable`, `apple-mobile-web-app-title` and the `apple-touch-icon` link in the head of both apps.

---

## Conventions

- No nutrition numbers anywhere in the recipe app — Dave asked for protein-forward food without macro labelling. This is deliberate.
- Mobile-first: 390px is the design width; tap targets ≥ 44px.
- Dark themes: kitchen is warm (`--accent:#f0a04b`), workout is per-day coloured.
- Recipes should stay bold and regional. 96 distinct cuisines are in use — check `all_recipes.json` before adding, and avoid repeating a cuisine.
- Prices and product details drift. Keep ranges, never state exact prices as fact, and keep the "packaging varies" disclaimer on guide sheets.
- Do not bundle retailer product photos. Guides link to an image search instead — legally clean and keeps the app small.

---

## Before you ship anything

1. Rebuild both apps.
2. Run the Playwright checks with JS **off** and **on**.
3. Confirm no console or page errors.
4. Bump the service worker cache version.
5. Tell Dave to force-close and reopen the installed app to pick up the change.
