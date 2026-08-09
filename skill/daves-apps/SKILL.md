---
name: daves-apps
description: Build and edit Dave's personal apps — the Hypertrophy Hub workout app, the Weekly Kitchen recipe app, and the betting edge-analysis tool. Use when working on any of these, when asked to add recipes, change the workout plan, rebuild or deploy the apps, or when the user mentions kitchen app, workout app, rest timer, meal plan, shopping list, or betting tool.
---

# Dave's Apps

Three single-file, installable web apps deployed to GitHub Pages. Source lives in the project repo: `src/recipe/`, `src/workout/`, and `dist/` (the deployable site).

## Rule zero: everything works without JavaScript

Dave reviews these in preview panes where scripts are blocked. An early version rendered content via JS and showed him a blank page.

State and navigation live in HTML/CSS:
- Tabs, sheets, overlays → hidden radio/checkbox inputs + `~` sibling selectors, or `:target` + anchors
- Timers → CSS `@keyframes` over a strip of pre-rendered digits with `steps()`
- Checklists → `:checked` sibling rules

JavaScript only adds sound, vibration, pause/adjust, date detection, shuffle, sharing. Wrap JS-only controls in `.js-only`. `<body class="no-js">` becomes `class="js"` on the first script line.

## The apps are generated — never hand-edit dist/

```bash
cd src/recipe  && python3 build_app.py        # -> dist/kitchen/index.html
cd src/workout && python3 build_workout.py    # -> dist/workout/index.html
```

Edit the build script or the JSON data, then rebuild. Hand edits to `dist/*/index.html` are destroyed on the next build.

## Data

- `src/recipe/data/all_recipes.json` — 96 recipes, 24 weeks, 6 months. Each week: 3 dinners (2 servings) + 1 batch cook (6 servings).
- `src/recipe/data/guides.json` — 171 ingredient shopping guides keyed by normalised ingredient string.
- Recipe `timer` values must come from: 60, 120, 180, 240, 300, 420, 480, 600, 720, 900, 1200, 1500, 1800. Anything else produces a dead button.
- Recipe IDs are deterministic (`w{week}r{index}`). Never use Python `hash()` — it is randomised per process.
- No nutrition or macro numbers anywhere in the recipe app. Deliberate.

## Before shipping, always

1. Rebuild both apps.
2. Test in Playwright with `javaScriptEnabled: false` **and** `true`.
3. Check for console/page errors.
4. Bump `CACHE` in the relevant `sw.js` (`kitchen-v1` → `v2`) or installed apps keep serving stale content.
5. Deliver with `SendUserFile` and remind Dave to force-close and reopen the installed app.

## Deployment facts

Dave is on iPhone. Only **Safari** can add to the Home Screen — Chrome and Edge cannot. Keep `apple-mobile-web-app-capable`, `apple-mobile-web-app-title` and `apple-touch-icon` in every app head. Local files can never be installed; the apps must be served over https.

## Betting tool: the honest framing

Build mechanical-edge tooling only: no-vig fair odds, line shopping / +EV vs consensus, closing-line-value tracking, quarter-Kelly staking, honest P&L. **Never build or imply an "AI picks winners" feature** — sportsbook lines are efficient and the closing line beats nearly all private models. If asked for predictions, explain the trade-off rather than complying. Include the caveats: books limit winners, most bettors lose, this is not financial advice.

See `BACKLOG.md` in the repo for full specs on the planned work.
