# Backlog — what to build next

Three projects. Read `DEVELOPMENT.md` first; the no-JavaScript rule applies to everything in the kitchen and workout apps.

Priority order: **A1 → A2 → A3 → C → B**.

---

# A. Kitchen app enhancements

## A1. Plan the week with Laurel (highest priority)

Dave's fiancée Laurel should help choose the week's meals. There is no server and there must not be one — no accounts, no database, no hosting cost. Everything travels in the URL.

**Build a "Plan this week" flow.**

Entry point: a button on each week panel. It opens a picker showing all 96 recipes, browsable and filterable by cuisine, time and dinner-vs-batch. Dave taps three dinners plus one batch cook. Chosen recipes get assigned to days of the week.

**Sharing.** A "Send to Laurel" button encodes the plan into the URL hash — recipe IDs plus day assignments, e.g. `#plan=w3r0.mon,w7r1.tue,w12r2.thu,w5r3.sun`. Keep it compact; IDs are already short. Use the Web Share API where available (`navigator.share`) falling back to clipboard copy, and always also produce a plain-text version she can read in the message itself:

```
This week's dinners 🍳
Mon — Gochujang Bulgogi Beef Bowls (25 min)
Tue — Basque Cod al Pil-Pil (30 min)
Thu — Cantonese Steamed Cod (35 min)
Sun — Hungarian Goulash (batch, 70 min)
Open: https://<pages-url>/kitchen/#plan=...
```

On load, if a `#plan=` hash is present, render that plan as the active week — including its combined shopping list — instead of the date-derived one. This is what makes the link work for Laurel with no install.

**Voting.** Laurel should be able to respond, not just receive. Give the picker a 👍/👎 per recipe; her choices encode into a `#votes=` hash she sends back. When Dave opens a `#votes=` link, show her reactions on the cards so he can finalise. Keep it to one round-trip — do not build a chat.

Persist the current plan in `localStorage` so it survives app restarts, but the URL is always the source of truth when a hash is present.

**Constraint:** the picker and plan view must still render with JavaScript off (fall back to the normal fixed week). Encoding/decoding and sharing are legitimately JS-only — wrap those controls in `.js-only`.

## A2. Real in-store shopping mode

The shopping list exists and every specialty ingredient already has a guide sheet (`guides.json`: aisle, package description, size, rough price, what to look for, what people grab by mistake, plus an image-search link). Make it work for someone actually pushing a cart.

- **Split by store first, then by aisle.** Dave shops Trader Joe's and Aldi in separate trips. Add a store toggle at the top — "Trader Joe's only / Aldi only / Everything" — and group items under aisle headings within each, using the `aisle` field. This is the single biggest usability win: it turns the list into a walking route.
- **Progress**: "12 of 31 items" with a progress bar. Checking the last item in an aisle should visibly complete that section.
- **Hide checked items** toggle, so the list shrinks as he shops.
- **Bigger tap targets** in this mode — one-handed use while pushing a trolley. Minimum 56px rows.
- **Keep the screen awake** while the list is open (`navigator.wakeLock`, same as the workout app).
- **Combine duplicates across recipes**: if two recipes each need garlic, show one line with both amounts and which dishes they're for.
- **Pantry check first**: before shopping, a quick pass to tick off what he already has, so those items drop off the list.

## A3. Making it fun and good at time management

Pick from these, highest value first:

- **Multiple simultaneous timers.** Currently only one runs at a time, which is wrong for real cooking — rice, sauce and protein all at once. Show running timers as a stacked bar with labels, each independently pausable. This is the most requested kind of cooking-app feature and the current single-timer design is the app's weakest point.
- **Cook timeline.** For each recipe, precompute a suggested order of operations so downtime is used — "while the beef browns, pickle the cucumbers". Many steps already say this in prose; surface it as a timeline view showing which steps overlap.
- **"Tonight" card** on the home screen: the next unmade meal of the current week, one tap from cook mode.
- **Favourites and history.** Heart a recipe; track what's been cooked and when (`localStorage`). A "cook again" shelf of past hits. Feeds the shuffle so it can favour things they liked.
- **Servings scaler.** 2 → 4 → 6, rescaling ingredient quantities and the shopping list. Quantities are free text, so parse leading numbers and fractions and leave anything unparseable alone rather than mangling it.
- **Rating after cooking.** At the end of cook mode, a quick 1–5. Low-rated recipes get deprioritised by shuffle.
- **Prep-ahead flags.** Mark steps doable the night before; a Sunday view lists all of the week's prep-ahead work in one place.

---

# B. Workout app

Largely complete: 4-day split, per-exercise rest timers, CSS countdowns, Spotify links, offline install. Outstanding:

- **Set logging** — weight, reps and RIR per set, stored in `localStorage`. Dave's plan is built on double progression, so the app should show last session's numbers next to each exercise while he lifts. This is the missing piece that makes the app actually drive progression.
- **Progression prompts** — when every set hit the top of the rep range, suggest adding weight next time.
- **Multiple rest timers** are unnecessary here; one is correct.
- **Body-weight and measurement log**, weekly, with a simple trend line.
- Dave's own Spotify playlist links can be baked into the build if he supplies them.

---

# C. Betting edge tool (new project)

**Read this section carefully before building. The framing matters more than the code.**

Dave asked for "an AI that makes bets that win". That product does not exist and must not be implied. Sportsbook lines are set and corrected by sharp money; the closing line beats nearly all private models. Standard -110 pricing requires ~52.4% accuracy just to break even. A tool that claims to predict winners would be dishonest.

He has been told this plainly and accepted a tool built on the mechanical edges instead. **Build that. Do not add a "predictions" or "AI picks" feature, even if asked casually — raise the trade-off instead.**

**What to build:**

1. **No-vig fair odds calculator.** Enter the prices both sides of a market; strip the vig; output true implied probability. This is the foundation everything else sits on.
2. **Line shopping / +EV finder.** Compare a book's price against the consensus of others. Flag where a price is meaningfully better than the market's fair value, and show the expected value as a percentage of stake.
3. **Bet log with closing-line value.** Every bet records the price taken and the closing price. CLV is the honest scoreboard — beating the close consistently is the only real evidence of an edge. Show it prominently; make it hard to ignore a negative trend.
4. **Kelly staking.** Given edge and bankroll, recommend a stake. Default to **quarter Kelly**, not full — full Kelly is far too volatile for a real bankroll. Cap any single stake at a configurable percentage.
5. **Honest P&L.** Actual profit and loss, with a plain-language read on whether the sample is large enough to mean anything. A few dozen bets tells you nothing; make that clear rather than showing a flattering graph.

**Data.** Start with manual entry and The Odds API's free tier (~500 requests/month) on one sport and one market. Do not spend on a paid feed until there are a few hundred logged bets showing positive CLV. Build the data layer behind an interface so the source can be swapped later.

**Tone.** No hype, no "locks", no streak celebrations, no push notifications urging action. The app's job is to tell Dave the truth about whether he is winning, including when the answer is no.

**Must include:** a note that books limit or ban consistent winners, that most bettors lose over time, and that this is a tool for analysis and not financial advice. Add a bankroll-setting step that asks for an amount he is fully prepared to lose, and a visible session/loss limit he sets himself.

**Stack.** Same as the others — single-page, offline-capable, installable, `localStorage` for the bet log, with export to CSV so his data is never trapped. The no-JavaScript rule does **not** apply here; this app is inherently interactive. It should still work offline once loaded.

---

## Working with Dave

- He is on an iPhone and often reviewing in a preview pane where scripts are blocked. Ship things he can actually see.
- Deliver files with `SendUserFile`; he cannot browse the workspace.
- He appreciates being told plainly when something will not work and why — the Home Screen limitation, the betting reality. Do not soften it into vagueness, and do not lecture him either.
- Verify with a real headless browser before claiming something works.
