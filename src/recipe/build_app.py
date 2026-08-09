#!/usr/bin/env python3
"""Builds a single-file weekly recipe app that works with or without JavaScript.
Week tabs, recipe detail, step-by-step cook mode, cooking timers and the
shopping list are all CSS-driven; JS only adds sound/vibration + richer timer."""
import json, html, collections, os

# Portable paths: resolve everything relative to this script's location so the
# build runs wherever the repo lives (see DEVELOPMENT.md).
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, "data")
_REPO = os.path.dirname(os.path.dirname(_HERE))          # repo root (…/daves-apps)
_OUT  = os.path.join(_REPO, "dist", "kitchen", "index.html")

R = json.load(open(os.path.join(_DATA, "all_recipes.json"), encoding="utf-8"))
WEEKS = sorted({r["week"] for r in R})
NMONTH = len(WEEKS) // 4
ORDER = {"dinner": 0, "batch": 1}
BY_WEEK = {w: sorted([r for r in R if r["week"] == w], key=lambda x: ORDER[x["slot"]]) for w in WEEKS}

STORE_META = {
    "TJ":     ("Trader Joe's", "tj"),
    "Aldi":   ("Aldi",         "aldi"),
    "Either": ("Either store", "either"),
    "Pantry": ("Pantry",       "pantry"),
}

import re as _re, urllib.parse as _up
GUIDES = {g["key"]: g for g in json.load(open(os.path.join(_DATA, "guides.json"), encoding="utf-8"))}

_QTY = _re.compile(r"""^\s*(
      \d+[\d\s/.¼-¾-]*\s*
      (lb|lbs|pound|pounds|oz|ounce|ounces|g|kg|cup|cups|tbsp|tsp|teaspoon|tablespoon|
       clove|cloves|can|cans|jar|jars|bag|bags|box|boxes|bunch|bunches|head|heads|
       package|packages|pack|packs|container|containers|sprig|sprigs|stalk|stalks|
       slice|slices|piece|pieces|pouch|pouches|block|blocks|large|medium|small|
       links|link|sheet|sheets|quart|quarts|pint|pints|ml|l)?s?\b\.?\s*
    )+""", _re.X | _re.I)
_TRAIL = _re.compile(r",\s*(chopped|sliced|minced|grated|diced|crushed|torn|halved|quartered|"
                     r"thinly sliced|finely chopped|roughly chopped|drained|rinsed|"
                     r"cut into.*|separated|whites and greens separated|julienned|smashed|"
                     r"at room temperature|softened|beaten|peeled.*|trimmed|zested and juiced|"
                     r"plus more.*|divided|to taste|for serving|for garnish)\b.*$", _re.I)
_PAREN = _re.compile(r"\s*\([^)]*\)")
_KEYS = set(GUIDES)

def gkey(item):
    k = _PAREN.sub("", item)
    k = _QTY.sub("", k).strip()
    k = _TRAIL.sub("", k).strip(" ,")
    k = _re.sub(r"\s+", " ", k).lower()
    if k in _KEYS: return k
    k2 = _re.sub(r"\bcloves? (of )?garlic\b|\bgarlic cloves?\b", "garlic", k)
    for c in (k2, k2[:-1] if k2.endswith("s") else k2, k2[:-2] if k2.endswith("es") else k2):
        if c in _KEYS: return c
    return None

def slug(k):
    return "g-" + _re.sub(r"[^a-z0-9]+", "-", k.lower()).strip("-")[:60]

def photo_url(g):
    store = {"TJ": "Trader Joe's", "Aldi": "Aldi"}.get(g["store"], "")
    q = _up.quote(f'{store} {g["display"]}'.strip())
    return f"https://duckduckgo.com/?q={q}&iax=images&ia=images"

def esc(s): return html.escape(str(s), quote=True)
def mmss(t): return f"{t//60}:{t%60:02d}"

# ---------- collect the timer durations actually used ----------
DURS = sorted({s["timer"] for r in R for s in r["steps"] if s.get("timer")})

def roll(dur):
    """(items_html, step_count) — 1s resolution up to 10 min, then 10s."""
    if dur <= 600:
        vals = range(dur, -1, -1); n = dur
    else:
        vals = range(dur, -1, -10); n = dur // 10
    return "".join(f"<i>{mmss(v)}</i>" for v in vals), n

# ============================================================ CSS
CSS_STATIC = """
  :root{
    --bg:#12100e; --card:#1c1917; --card2:#262220; --line:#332e2a;
    --txt:#f2ede7; --dim:#a49b91; --dimmer:#6f665e;
    --accent:#f0a04b; --accent-soft:#f0a04b26;
    --green:#6fcf8f; --tj:#e4572e; --aldi:#4a90d9;
    --safe-b:env(safe-area-inset-bottom,0px);
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
  html,body{margin:0;padding:0;background:var(--bg);color:var(--txt);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    font-size:16px;line-height:1.5;}
  body{padding-bottom:calc(24px + var(--safe-b));}
  .wkradio,.viewradio,.stepradio,.tmrradio,.chk{position:absolute;opacity:0;pointer-events:none;width:0;height:0;}

  header{position:sticky;top:0;z-index:20;background:rgba(18,16,14,.95);
    -webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);
    border-bottom:1px solid var(--line);padding:14px 16px 0;}
  h1{font-size:19px;margin:0;font-weight:800;letter-spacing:.2px;}
  .sub{color:var(--dimmer);font-size:12px;font-weight:600;margin-top:1px;}
  .tabs{display:flex;gap:6px;overflow-x:auto;padding:12px 0;
    scrollbar-width:none;-ms-overflow-style:none;}
  .tabs::-webkit-scrollbar{display:none;}
  .tab{flex:0 0 auto;border:1px solid var(--line);background:var(--card);color:var(--dim);
    border-radius:12px;padding:8px 14px;font-size:13px;font-weight:800;cursor:pointer;
    user-select:none;white-space:nowrap;}
  .tab.is-now::after{content:" • now";color:var(--accent);font-size:11px;}
  .tabs.wkrow{display:none;padding-top:0;}
  .mtab{font-size:13px;}
  .wtab{font-size:12.5px;padding:7px 13px;}
  .shuffle{border-style:dashed;color:var(--accent);}
  .no-js .js-only{display:none !important;}

  main{padding:16px;max-width:680px;margin:0 auto;}
  .wkpanel{display:none;}
  .wk-head{margin-bottom:6px;}
  .wk-title{font-size:24px;font-weight:800;margin:0;}
  .wk-sub{color:var(--dim);font-size:14px;margin:3px 0 0;}

  .card{display:block;background:var(--card);border:1px solid var(--line);border-radius:18px;
    padding:16px;margin:13px 0;cursor:pointer;user-select:none;position:relative;overflow:hidden;}
  .card:active{transform:scale(.995);}
  .card-top{display:flex;gap:13px;align-items:flex-start;}
  .hero{font-size:32px;line-height:1;flex:0 0 auto;width:52px;height:52px;border-radius:14px;
    background:var(--card2);display:flex;align-items:center;justify-content:center;}
  .card-main{flex:1;min-width:0;}
  .slot{font-size:10.5px;letter-spacing:1.3px;text-transform:uppercase;font-weight:800;
    color:var(--accent);}
  .slot.batch{color:var(--green);}
  .card h3{margin:2px 0 3px;font-size:17.5px;font-weight:800;line-height:1.25;}
  .meta{color:var(--dimmer);font-size:12.5px;font-weight:700;}
  .blurb{color:var(--dim);font-size:13.5px;margin-top:8px;}
  .cta{margin-top:12px;display:inline-flex;align-items:center;gap:7px;background:var(--accent);
    color:#1a1005;font-weight:800;font-size:13.5px;border-radius:11px;padding:9px 15px;}

  .list-btn{display:block;text-align:center;border:1px dashed var(--line);color:var(--dim);
    background:var(--card);border-radius:14px;padding:14px;font-weight:800;font-size:14px;
    margin:18px 0 6px;cursor:pointer;user-select:none;}

  /* ---------- full-screen sheets ---------- */
  .sheet{position:fixed;inset:0;z-index:40;background:var(--bg);display:none;
    flex-direction:column;overflow-y:auto;}
  .sheet-head{position:sticky;top:0;background:rgba(18,16,14,.96);
    -webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);
    border-bottom:1px solid var(--line);padding:14px 16px;display:flex;align-items:center;gap:12px;}
  .back{border:1px solid var(--line);background:var(--card);color:var(--dim);border-radius:11px;
    padding:8px 13px;font-weight:800;font-size:13px;cursor:pointer;user-select:none;flex:0 0 auto;}
  .sheet-title{font-weight:800;font-size:15.5px;line-height:1.25;flex:1;min-width:0;}
  .sheet-body{padding:18px 16px calc(40px + var(--safe-b));max-width:680px;margin:0 auto;width:100%;}

  .r-hero{display:flex;gap:14px;align-items:center;margin-bottom:6px;}
  .r-hero .hero{width:60px;height:60px;font-size:36px;}
  .r-name{font-size:22px;font-weight:800;line-height:1.2;}
  .r-meta{color:var(--dimmer);font-size:13px;font-weight:700;margin-top:3px;}
  .r-blurb{color:var(--dim);font-size:14.5px;margin:12px 0 20px;}

  .sec-label{font-size:11.5px;letter-spacing:1.4px;text-transform:uppercase;color:var(--dimmer);
    font-weight:800;margin:22px 0 8px;}
  .ing{display:flex;align-items:center;gap:11px;background:var(--card);border:1px solid var(--line);
    border-radius:12px;padding:11px 13px;margin:7px 0;cursor:pointer;user-select:none;font-size:14.5px;}
  .box{width:21px;height:21px;border-radius:6px;border:2px solid var(--line);flex:0 0 auto;
    display:flex;align-items:center;justify-content:center;color:transparent;font-size:12px;font-weight:900;}
  .ing-row{display:flex;align-items:stretch;gap:7px;}
  .ing-row .ing{flex:1;min-width:0;margin:7px 0;}
  .ing-src{color:var(--dimmer);font-size:11.5px;font-weight:700;}
  .info-btn{flex:0 0 auto;width:38px;margin:7px 0;border:1px solid var(--line);
    background:var(--card);border-radius:12px;display:flex;align-items:center;justify-content:center;
    color:var(--accent);font-weight:900;font-size:15px;text-decoration:none;}
  .info-btn:active{background:var(--card2);}
  .chk:checked + .ing-row .ing{opacity:.45;}
  .chk:checked + .ing-row .ing .box{background:var(--green);border-color:var(--green);color:#12100e;}
  .chk:checked + .ing-row .ing .ing-txt{text-decoration:line-through;}

  /* ---------- ingredient guide sheets (:target, no JS needed) ---------- */
  .gsheet{position:fixed;inset:0;z-index:70;background:var(--bg);display:none;
    flex-direction:column;overflow-y:auto;}
  .gsheet:target{display:flex;}
  .g-hero{display:flex;gap:15px;align-items:center;margin-bottom:16px;}
  .g-ico{width:78px;height:78px;border-radius:20px;flex:0 0 auto;display:flex;
    align-items:center;justify-content:center;background:var(--card2);border:1px solid var(--line);}
  .g-ico svg{width:52px;height:52px;}
  .g-name{font-size:21px;font-weight:800;line-height:1.2;}
  .g-where{margin-top:5px;display:flex;gap:6px;flex-wrap:wrap;align-items:center;}
  .g-row{background:var(--card);border:1px solid var(--line);border-radius:14px;
    padding:13px 15px;margin:9px 0;}
  .g-row h4{margin:0 0 4px;font-size:11px;letter-spacing:1.3px;text-transform:uppercase;
    color:var(--dimmer);font-weight:800;}
  .g-row p{margin:0;font-size:14.5px;color:var(--txt);}
  .g-row.warn{border-left:3px solid #e4572e;}
  .g-row.warn h4{color:#f38a68;}
  .g-facts{display:flex;gap:9px;margin:9px 0;}
  .g-fact{flex:1;background:var(--card);border:1px solid var(--line);border-radius:14px;
    padding:11px 13px;text-align:center;}
  .g-fact b{display:block;font-size:16px;font-weight:800;}
  .g-fact span{font-size:10.5px;letter-spacing:1.2px;text-transform:uppercase;color:var(--dimmer);
    font-weight:800;}
  .g-photo{display:block;text-align:center;background:var(--accent);color:#1a1005;font-weight:800;
    font-size:15px;border-radius:14px;padding:15px;margin:18px 0 6px;text-decoration:none;}
  .g-note{color:var(--dimmer);font-size:11.5px;text-align:center;margin-top:8px;}
  .g-index a{display:flex;gap:11px;align-items:center;background:var(--card);
    border:1px solid var(--line);border-radius:12px;padding:11px 13px;margin:7px 0;
    text-decoration:none;color:var(--txt);font-size:14.5px;font-weight:600;}
  .g-index a svg{width:26px;height:26px;flex:0 0 auto;}
  .guide-btn{display:block;text-align:center;border:1px solid var(--line);color:var(--accent);
    background:var(--card);border-radius:14px;padding:13px;font-weight:800;font-size:14px;
    margin:10px 0 6px;text-decoration:none;}
  .ing-txt{flex:1;}
  .pill{font-size:10.5px;font-weight:800;border-radius:20px;padding:3px 9px;flex:0 0 auto;
    letter-spacing:.3px;}
  .pill.tj{background:rgba(228,87,46,.16);color:#f38a68;}
  .pill.aldi{background:rgba(74,144,217,.16);color:#8bbaea;}
  .pill.either{background:#2a2522;color:var(--dim);}
  .pill.pantry{background:#2a2522;color:var(--dimmer);}

  .note{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accent);
    border-radius:12px;padding:12px 14px;margin:10px 0;font-size:13.5px;color:var(--dim);}
  .note b{color:var(--txt);}

  .cook-cta{display:block;text-align:center;background:var(--accent);color:#1a1005;font-weight:800;
    font-size:16px;border-radius:14px;padding:16px;margin:26px 0 8px;cursor:pointer;user-select:none;}

  /* ---------- cook mode ---------- */
  .cook{position:fixed;inset:0;z-index:50;background:var(--bg);display:none;
    flex-direction:column;}
  .cook-head{padding:14px 16px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:12px;}
  .prog{height:4px;background:var(--line);border-radius:2px;margin-bottom:18px;flex:0 0 auto;}
  .prog i{display:block;height:100%;background:var(--accent);}
  .step{display:none;flex:1;flex-direction:column;padding:26px 20px calc(20px + var(--safe-b));
    overflow-y:auto;max-width:680px;margin:0 auto;width:100%;}
  .step-n{font-size:11.5px;letter-spacing:1.6px;text-transform:uppercase;color:var(--accent);
    font-weight:800;}
  .step-txt{font-size:22px;font-weight:600;line-height:1.42;margin:14px 0 0;}
  .step-tip{color:var(--dim);font-size:14px;margin-top:14px;display:flex;gap:8px;align-items:flex-start;}
  .step-timer{margin-top:20px;display:inline-flex;align-items:center;gap:8px;background:var(--card2);
    border:1px solid var(--accent);color:var(--accent);font-weight:800;font-size:15px;
    border-radius:12px;padding:13px 18px;cursor:pointer;user-select:none;align-self:flex-start;}
  .step-nav{display:flex;gap:10px;margin-top:auto;padding-top:26px;}
  .nav-btn{flex:1;text-align:center;border-radius:13px;padding:15px 0;font-weight:800;font-size:15.5px;
    cursor:pointer;user-select:none;}
  .nav-back{background:var(--card2);color:var(--txt);border:1px solid var(--line);}
  .nav-next{background:var(--accent);color:#1a1005;}
  .nav-done{background:var(--green);color:#0d2716;}

  /* ---------- timers ---------- */
  .tmr,.tmr-css{position:fixed;inset:0;z-index:60;background:rgba(18,16,14,.985);display:none;
    flex-direction:column;align-items:center;justify-content:center;padding:24px;text-align:center;}
  .tmr.show{display:flex;}
  .js .tmr-css{display:none !important;}
  .tmr-ex{color:var(--dim);font-size:15px;font-weight:700;max-width:90%;}
  .ring-wrap{position:relative;width:min(70vw,290px);height:min(70vw,290px);margin:22px 0;}
  .ring-wrap svg{width:100%;height:100%;transform:rotate(-90deg);}
  .ring-bg{fill:none;stroke:var(--line);stroke-width:7;}
  .ring-fg{fill:none;stroke:var(--accent);stroke-width:7;stroke-linecap:round;}
  .tmr .ring-fg{transition:stroke-dashoffset .95s linear;}
  .tmr-digits{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
    justify-content:center;}
  .tmr-time{font-size:58px;font-weight:800;font-variant-numeric:tabular-nums;}
  .tmr-time.warn{color:#f5c451;}
  .tmr-time.overtime{color:var(--green);}
  .tmr-state{font-size:11.5px;letter-spacing:2px;text-transform:uppercase;color:var(--dimmer);
    font-weight:800;margin-top:2px;}
  .cd{height:1em;overflow:hidden;font-size:58px;font-weight:800;line-height:1;
    font-variant-numeric:tabular-nums;}
  .cd-roll i{display:block;height:1em;font-style:normal;}
  .tmr-go{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);opacity:0;
    font-size:27px;font-weight:800;color:var(--green);pointer-events:none;}
  .tmr-adjust{display:flex;gap:10px;margin-bottom:18px;}
  .adj{border:1px solid var(--line);background:var(--card);color:var(--txt);border-radius:12px;
    padding:10px 18px;font-size:15px;font-weight:800;cursor:pointer;font-family:inherit;}
  .tmr-actions{display:flex;gap:10px;width:100%;max-width:340px;}
  .tmr-actions button,.tmr-actions label{flex:1;border:none;border-radius:14px;padding:15px 0;
    font-size:16px;font-weight:800;cursor:pointer;font-family:inherit;text-align:center;user-select:none;}
  .btn-pause{background:var(--card2);color:var(--txt);border:1px solid var(--line) !important;}
  .btn-done{background:var(--accent);color:#1a1005;}

  .nojs{display:none;background:#1e2a3a;border:1px solid #39506e;color:#a9c6e8;border-radius:12px;
    padding:11px 14px;font-size:12.5px;margin:0 0 14px;}
  .no-js .nojs{display:block;}

  @keyframes ringrun{to{stroke-dashoffset:339.292;}}
  @keyframes fadeout{to{opacity:0;}}
  @keyframes fadein{from{opacity:0;}to{opacity:1;}}
  @keyframes pulse{0%,100%{transform:translateY(-50%) scale(1);}50%{transform:translateY(-50%) scale(1.07);}}
"""

rules = []
ACT = "color:#1a1005;background:var(--accent);border-color:var(--accent);"
for i, w in enumerate(WEEKS):
    m = i // 4
    rules.append(f'#wk{i}:checked ~ main #wp{i}{{display:block;}}')
    rules.append(f'#wk{i}:checked ~ header #mrow{m}{{display:flex;}}')
    rules.append(f'#wk{i}:checked ~ header .mtab[for="wk{m*4}"]{{{ACT}}}')
    rules.append(f'#wk{i}:checked ~ header .wtab[for="wk{i}"]{{{ACT}}}')
for r in DURS:
    _, n = roll(r)
    rules.append(f"@keyframes roll{r}{{to{{transform:translateY(-{n}em);}}}}")

view_ids, step_groups = [], []
_seen = collections.Counter()
for w in WEEKS:
    for j, r in enumerate(BY_WEEK[w]):
        r["_id"] = f"w{w}r{j}"          # deterministic: stable across builds
for r in R:
    rid = r["_id"]
    view_ids.append(f'#v{rid}:checked ~ .view-wrap #sv{rid}{{display:flex;}}')
    for si in range(len(r["steps"])):
        step_groups.append(f'#s{rid}_{si}:checked ~ .cook-wrap #ck{rid}{{display:flex;}}')
        step_groups.append(f'#s{rid}_{si}:checked ~ .cook-wrap #cs{rid}_{si}{{display:flex;}}')
for w in WEEKS:
    view_ids.append(f'#vlist{w}:checked ~ .view-wrap #svlist{w}{{display:flex;}}')
tmr_rules = [f'#t{d}:checked ~ .tmr-wrap #tc{d}{{display:flex;}}' for d in DURS]

CSS = CSS_STATIC + "\n  " + "\n  ".join(rules + view_ids + step_groups + tmr_rules) + "\n"

# ============================================================ HTML
radios = []
for i in range(len(WEEKS)):
    radios.append(f'<input type="radio" name="wk" id="wk{i}" class="wkradio"{" checked" if i==0 else ""}>')
radios.append('<input type="radio" name="view" id="v-none" class="viewradio" checked>')
for r in R:
    radios.append(f'<input type="radio" name="view" id="v{r["_id"]}" class="viewradio">')
for w in WEEKS:
    radios.append(f'<input type="radio" name="view" id="vlist{w}" class="viewradio">')
radios.append('<input type="radio" name="step" id="s-none" class="stepradio" checked>')
for r in R:
    for si in range(len(r["steps"])):
        radios.append(f'<input type="radio" name="step" id="s{r["_id"]}_{si}" class="stepradio">')
radios.append('<input type="radio" name="tmr" id="t-none" class="tmrradio" checked>')
for d in DURS:
    radios.append(f'<input type="radio" name="tmr" id="t{d}" class="tmrradio">')
radios_html = "\n".join(radios)

mrow = "\n      ".join(
    f'<label class="tab mtab" for="wk{m*4}">Month {m+1}</label>' for m in range(NMONTH))
wrows = []
for m in range(NMONTH):
    inner = "".join(
        f'<label class="tab wtab" for="wk{m*4+k}">Week {k+1}</label>' for k in range(4))
    wrows.append(f'<div class="tabs wkrow" id="mrow{m}">{inner}</div>')
tabs_html = (f'<div class="tabs">{mrow}'
             f'<label class="tab shuffle js-only" for="wk0" id="shufBtn">🎲 Surprise me</label></div>'
             + "\n      " + "\n      ".join(wrows))

def card(r):
    slot = "Big batch cook" if r["slot"] == "batch" else "Weeknight dinner"
    cls = " batch" if r["slot"] == "batch" else ""
    serv = f'{r["servings"]} servings'
    return f'''<label class="card" for="v{r["_id"]}">
  <div class="card-top">
    <div class="hero">{r["hero"]}</div>
    <div class="card-main">
      <div class="slot{cls}">{slot} · {esc(r["cuisine"])}</div>
      <h3>{esc(r["title"])}</h3>
      <div class="meta">{esc(r["time"])} · {serv}</div>
    </div>
  </div>
  <div class="blurb">{esc(r["blurb"])}</div>
  <span class="cta">▶ Open recipe</span>
</label>'''

panels = []
for i, w in enumerate(WEEKS):
    rs = BY_WEEK[w]
    cuisines = " · ".join(x["cuisine"] for x in rs)
    panels.append(
      f'<section class="wkpanel" id="wp{i}">'
      f'<div class="wk-head"><h2 class="wk-title">Month {i//4+1} · Week {i%4+1}</h2>'
      f'<p class="wk-sub">{esc(cuisines)}</p></div>'
      + "\n".join(card(r) for r in rs)
      + f'<label class="list-btn" for="vlist{w}">🛒 Shopping list for this week</label>'
      + '<a class="guide-btn" href="#g-index">📖 Ingredient buying guide</a>'
      + '</section>')
panels_html = "\n".join(panels)

# ---------------- recipe detail sheets ----------------
def info_link(item):
    k = gkey(item)
    if not k: return ""
    return f'<a class="info-btn" href="#{slug(k)}" aria-label="How to buy this">?</a>'

def ing_row(r, idx, ing):
    label, cls = STORE_META[ing["store"]]
    cid = f'i{r["_id"]}_{idx}'
    return (f'<input type="checkbox" class="chk" id="{cid}">'
            f'<div class="ing-row"><label class="ing" for="{cid}"><span class="box">✓</span>'
            f'<span class="ing-txt">{esc(ing["item"])}</span>'
            f'<span class="pill {cls}">{esc(label)}</span></label>'
            f'{info_link(ing["item"])}</div>')

sheets = []
for r in R:
    rid = r["_id"]
    slot = "Big batch cook" if r["slot"] == "batch" else "Weeknight dinner"
    ings = "\n".join(ing_row(r, i, g) for i, g in enumerate(r["ingredients"]))
    sheets.append(f'''<div class="sheet" id="sv{rid}">
  <div class="sheet-head">
    <label class="back" for="v-none">‹ Back</label>
    <div class="sheet-title">{esc(r["title"])}</div>
  </div>
  <div class="sheet-body">
    <div class="r-hero"><div class="hero">{r["hero"]}</div>
      <div><div class="r-name">{esc(r["title"])}</div>
      <div class="r-meta">{slot} · {esc(r["cuisine"])} · {esc(r["time"])} · {r["servings"]} servings</div></div>
    </div>
    <p class="r-blurb">{esc(r["blurb"])}</p>
    <div class="sec-label">Ingredients — tap to check off</div>
    {ings}
    <label class="cook-cta" for="s{rid}_0">👨‍🍳 Start cooking — step by step</label>
    <div class="note"><b>Swap:</b> {esc(r["swap"])}</div>
    <div class="note"><b>Leftovers:</b> {esc(r["leftovers"])}</div>
  </div>
</div>''')

# ---------------- shopping lists ----------------
for w in WEEKS:
    buckets = collections.OrderedDict((k, []) for k in ["TJ", "Aldi", "Either", "Pantry"])
    for r in BY_WEEK[w]:
        for g in r["ingredients"]:
            buckets[g["store"]].append((g["item"], r["title"]))
    body = []
    for store, items in buckets.items():
        if not items: continue
        label, cls = STORE_META[store]
        body.append(f'<div class="sec-label">{esc(label)} · {len(items)} items</div>')
        for n, (item, src) in enumerate(items):
            cid = f'sl{w}_{cls}_{n}'
            body.append(f'<input type="checkbox" class="chk" id="{cid}">'
                        f'<div class="ing-row"><label class="ing" for="{cid}"><span class="box">✓</span>'
                        f'<span class="ing-txt">{esc(item)}<br>'
                        f'<span class="ing-src">for {esc(src)}</span>'
                        f'</span></label>{info_link(item)}</div>')
    sheets.append(f'''<div class="sheet" id="svlist{w}">
  <div class="sheet-head">
    <label class="back" for="v-none">‹ Back</label>
    <div class="sheet-title">🛒 Month {(w-1)//4+1} · Week {(w-1)%4+1} shopping list</div>
  </div>
  <div class="sheet-body">
    <div class="note">Everything for this week's three dinners and the big batch cook, split by store. Tap items to check them off as you shop.</div>
    {"".join(body)}
  </div>
</div>''')
sheets_html = "\n".join(sheets)

# ---------------- cook mode ----------------
cooks = []
for r in R:
    rid, n = r["_id"], len(r["steps"])
    panes = []
    for si, s in enumerate(r["steps"]):
        pct = round((si + 1) / n * 100)
        tip = (f'<div class="step-tip"><span>💡</span><span>{esc(s["tip"])}</span></div>'
               if s.get("tip") else "")
        timer = (f'<label class="step-timer" for="t{s["timer"]}" data-sec="{s["timer"]}" '
                 f'data-name="{esc(r["title"])} — step {si+1}">⏱ Start {mmss(s["timer"])} timer</label>'
                 if s.get("timer") else "")
        back = (f'<label class="nav-btn nav-back" for="s{rid}_{si-1}">‹ Back</label>' if si > 0
                else f'<label class="nav-btn nav-back" for="v{rid}">‹ Recipe</label>')
        nxt = (f'<label class="nav-btn nav-next" for="s{rid}_{si+1}">Next ›</label>' if si < n - 1
               else f'<label class="nav-btn nav-done" for="v{rid}">✓ Finished</label>')
        panes.append(f'''<div class="step" id="cs{rid}_{si}">
  <div class="prog"><i style="width:{pct}%"></i></div>
  <div class="step-n">Step {si+1} of {n}</div>
  <p class="step-txt">{esc(s["text"])}</p>
  {tip}
  {timer}
  <div class="step-nav">{back}{nxt}</div>
</div>''')
    cooks.append(f'''<div class="cook" id="ck{rid}">
  <div class="cook-head">
    <label class="back" for="v{rid}">‹ Exit</label>
    <div class="sheet-title">{r["hero"]} {esc(r["title"])}</div>
  </div>
  {"".join(panes)}
</div>''')
cooks_html = "\n".join(cooks)


# ---------------- ingredient guide: icon sprite + sheets ----------------
ICON_PATHS = {
 "jar":     '<path d="M7 3h10v3H7z"/><path d="M6 7h12a1 1 0 0 1 1 1v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V8a1 1 0 0 1 1-1z"/>',
 "bottle":  '<path d="M10 2h4v4l2 3v11a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2V9l2-3z"/>',
 "bag":     '<path d="M6 8h12l-1 13H7z"/><path d="M9 8V5a3 3 0 0 1 6 0v3"/>',
 "box":     '<path d="M4 7h16v13H4z"/><path d="M4 7l2-3h12l2 3M12 7v13"/>',
 "frozen":  '<path d="M12 2v20M4 7l16 10M20 7L4 17"/><path d="M12 6l-2-2 2-2 2 2zM12 18l2 2-2 2-2-2z"/>',
 "can":     '<ellipse cx="12" cy="6" rx="7" ry="2.5"/><path d="M5 6v12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V6"/>',
 "produce": '<circle cx="12" cy="13" r="7"/><path d="M12 6c0-2 1.5-3.5 3.5-4"/>',
 "meat":    '<path d="M4 14a7 7 0 0 1 12-5l4 4-4 4a7 7 0 0 1-12-3z"/><circle cx="9" cy="13" r="2"/>',
 "dairy":   '<path d="M8 3h8v4l2 3v11H6V10l2-3z"/><path d="M8 7h8"/>',
 "bread":   '<path d="M4 11a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v9H4z"/><path d="M8 11v9M16 11v9"/>',
 "spice":   '<path d="M8 3h8v4H8z"/><path d="M7 7h10v13a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1z"/><path d="M11 10h.01M13 12h.01M11 14h.01"/>',
 "pouch":   '<path d="M6 5h12l-1 16H7z"/><path d="M6 5l2-2h8l2 2"/>',
 "noodle":  '<path d="M4 8h16M4 12h16M4 16h16"/><path d="M7 8v8M12 8v8M17 8v8"/>',
 "cheese":  '<path d="M3 16l9-9h9v9z"/><circle cx="16" cy="12" r="1.2"/><circle cx="11" cy="14" r="1"/>',
 "egg":     '<ellipse cx="12" cy="13" rx="6" ry="8"/>',
 "fish":    '<path d="M3 12c4-5 10-5 14 0-4 5-10 5-14 0z"/><path d="M17 12l4-3v6z"/><circle cx="8" cy="12" r="1"/>',
}
sprite = "".join(
    f'<symbol id="ic-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{v}</symbol>'
    for k, v in ICON_PATHS.items())
SPRITE = f'<svg style="display:none" aria-hidden="true">{sprite}</svg>'

def icon(name, cls=""):
    n = name if name in ICON_PATHS else "jar"
    return f'<svg class="{cls}"><use href="#ic-{n}"></use></svg>'

STORE_TONE = {"TJ": "tj", "Aldi": "aldi", "Either": "either", "Pantry": "pantry"}

gsheets = []
for k, g in sorted(GUIDES.items(), key=lambda kv: kv[1]["display"].lower()):
    label, cls = STORE_META.get(g["store"], ("Either store", "either"))
    rows = [f'<div class="g-row"><h4>What the package looks like</h4><p>{esc(g["pkg"])}</p></div>',
            f'<div class="g-row"><h4>Make sure it\'s the right one</h4><p>{esc(g["look_for"])}</p></div>']
    if g.get("confuse"):
        rows.append(f'<div class="g-row warn"><h4>Easy to grab by mistake</h4><p>{esc(g["confuse"])}</p></div>')
    if g.get("tip"):
        rows.append(f'<div class="g-row"><h4>Worth knowing</h4><p>{esc(g["tip"])}</p></div>')
    gsheets.append(f'''<div class="gsheet" id="{slug(k)}">
  <div class="sheet-head">
    <a class="back" href="#close">‹ Back</a>
    <div class="sheet-title">How to buy this</div>
  </div>
  <div class="sheet-body">
    <div class="g-hero">
      <div class="g-ico">{icon(g["icon"])}</div>
      <div><div class="g-name">{esc(g["display"])}</div>
        <div class="g-where"><span class="pill {cls}">{esc(label)}</span>
        <span class="ing-src">{esc(g["aisle"])} aisle</span></div></div>
    </div>
    <div class="g-facts">
      <div class="g-fact"><b>{esc(g["size"])}</b><span>Size</span></div>
      <div class="g-fact"><b>{esc(g["price"])}</b><span>Rough price</span></div>
    </div>
    {"".join(rows)}
    <a class="g-photo" href="{photo_url(g)}" target="_blank" rel="noopener">🔍 See photos of this product</a>
    <div class="g-note">Opens an image search — needs internet. Prices and packaging vary by region and change over time.</div>
  </div>
</div>''')

by_store = collections.OrderedDict()
for k, g in sorted(GUIDES.items(), key=lambda kv: kv[1]["display"].lower()):
    by_store.setdefault(g["store"], []).append((k, g))
idx_body = []
for store in ["TJ", "Aldi", "Either", "Pantry"]:
    items = by_store.get(store, [])
    if not items: continue
    label, _ = STORE_META[store]
    idx_body.append(f'<div class="sec-label">{esc(label)} · {len(items)} products</div><div class="g-index">')
    for k, g in items:
        idx_body.append(f'<a href="#{slug(k)}">{icon(g["icon"])}<span>{esc(g["display"])}</span></a>')
    idx_body.append("</div>")
gsheets.append(f'''<div class="gsheet" id="g-index">
  <div class="sheet-head">
    <a class="back" href="#close">‹ Back</a>
    <div class="sheet-title">🛒 Ingredient buying guide</div>
  </div>
  <div class="sheet-body">
    <div class="note">Every store-brand and specialty item used across the six months, with what the package looks like, which aisle it's in and what people grab by mistake.</div>
    {"".join(idx_body)}
  </div>
</div>''')
guides_html = "\n".join(gsheets)

# ---------------- CSS timer overlays ----------------
tmrs = []
for d in DURS:
    digits, n = roll(d)
    tmrs.append(f'''<div class="tmr-css" id="tc{d}">
  <div class="tmr-ex">{mmss(d)} timer</div>
  <div class="ring-wrap">
    <svg viewBox="0 0 120 120">
      <circle class="ring-bg" cx="60" cy="60" r="54"></circle>
      <circle class="ring-fg" cx="60" cy="60" r="54"
        style="stroke-dasharray:339.292; animation:ringrun {d}s linear forwards;"></circle>
    </svg>
    <div class="tmr-digits">
      <div class="cd" style="animation:fadeout .2s {d}s forwards;">
        <div class="cd-roll" style="animation:roll{d} {d}s steps({n}) forwards;">{digits}</div></div>
      <div class="tmr-state" style="animation:fadeout .01s {d}s forwards;">Cooking</div>
      <div class="tmr-go" style="animation:fadein .25s {d}s forwards, pulse 1s {d}s infinite;">Time's up!</div>
    </div>
  </div>
  <div class="tmr-actions"><label class="btn-done" for="t-none">Done</label></div>
</div>''')
tmrs_html = "\n".join(tmrs)

JS = """
document.body.className='js';
var NW=NWEEKS;
function pickToday(){
  try{
    var d=new Date();
    var monthsSinceEpoch=d.getFullYear()*12+d.getMonth();
    var m=((monthsSinceEpoch%NMONTHS)+NMONTHS)%NMONTHS;
    var wom=Math.min(3,Math.floor((d.getDate()-1)/7));
    return m*4+wom;
  }catch(e){ return 0; }
}
function selectWeek(i,markNow){
  var r=document.getElementById('wk'+i); if(!r) return;
  r.checked=true;
  Array.prototype.forEach.call(document.querySelectorAll('.tab.is-now'),function(l){l.classList.remove('is-now');});
  if(markNow){
    var l=document.querySelector('.wtab[for="wk'+i+'"]');
    if(l) l.classList.add('is-now');
  }
  var mt=document.querySelector('.mtab[for="wk'+(Math.floor(i/4)*4)+'"]');
  if(mt&&mt.scrollIntoView) mt.scrollIntoView({inline:'center',block:'nearest'});
  window.scrollTo(0,0);
}
var TODAY=pickToday();
selectWeek(TODAY,true);

/* shuffle: jump to a random week that isn't the one you're on */
Array.prototype.forEach.call(document.querySelectorAll('.shuffle'),function(btn){
  btn.addEventListener('click',function(e){
    e.preventDefault();
    var cur=document.querySelector('.wkradio:checked');
    var curI=cur?parseInt(cur.id.slice(2),10):-1, n;
    do { n=Math.floor(Math.random()*NW); } while(n===curI&&NW>1);
    selectWeek(n,false);
  });
});

Array.prototype.forEach.call(document.querySelectorAll('[data-sec]'),function(el){
  el.addEventListener('click',function(e){
    e.preventDefault();
    startTimer(parseInt(el.getAttribute('data-sec'),10), el.getAttribute('data-name'));
  });
});

var CIRC=2*Math.PI*54, ringFg=document.getElementById('ringFg');
ringFg.style.strokeDasharray=CIRC;
var tTotal=0,tEnd=0,tRemain=0,tPaused=false,tick=null,warned=false,finished=false,tLabel='Timer';
var tmr=document.getElementById('tmr'),tmrTime=document.getElementById('tmrTime'),
    tmrEx=document.getElementById('tmrEx'),tmrState=document.getElementById('tmrState'),
    pauseBtn=document.getElementById('pauseBtn');

function startTimer(sec,label){
  ensureAudio();
  tTotal=sec;tRemain=sec;tEnd=Date.now()+sec*1000;
  tPaused=false;warned=false;finished=false;tLabel=label||'Timer';
  tmrEx.textContent=tLabel;tmrState.textContent='Cooking';pauseBtn.textContent='Pause';
  tmr.classList.add('show');renderTimer();
  clearInterval(tick);tick=setInterval(renderTimer,250);
  vibrate([40]);
}
function renderTimer(){
  if(!tPaused) tRemain=Math.round((tEnd-Date.now())/1000);
  var r=tRemain,a=r>=0?r:-r,m=Math.floor(a/60),s=a%60;
  tmrTime.textContent=(r<0?'+':'')+m+':'+(s<10?'0':'')+s;
  tmrTime.className='tmr-time'+(r<=10&&r>0?' warn':'')+(r<=0?' overtime':'');
  ringFg.style.strokeDashoffset=CIRC*(1-Math.max(0,Math.min(1,r/tTotal)));
  if(r<=10&&r>0&&!warned){warned=true;beep(880,.12,2);vibrate([80,60,80]);}
  if(r<=0&&!finished){
    finished=true;tmrState.textContent="Time's up!";
    beep(1046,.18,3);vibrate([250,120,250,120,400]);
    document.title="🔔 Time's up!";setTimeout(function(){document.title=DOCTITLE;},5000);
  }
}
function adjustTimer(d){
  if(tPaused){tRemain+=d;}else{tEnd+=d*1000;}
  if(finished&&(tEnd-Date.now())>0){finished=false;warned=false;tmrState.textContent='Cooking';}
  tTotal=Math.max(tTotal,Math.round((tEnd-Date.now())/1000));renderTimer();
}
function togglePause(){
  if(tPaused){tEnd=Date.now()+tRemain*1000;tPaused=false;pauseBtn.textContent='Pause';
    tmrState.textContent=finished?"Time's up!":'Cooking';}
  else{tRemain=Math.round((tEnd-Date.now())/1000);tPaused=true;pauseBtn.textContent='Resume';
    tmrState.textContent='Paused';}
}
function stopTimer(){clearInterval(tick);tick=null;tmr.classList.remove('show');}
var actx=null;
function ensureAudio(){try{
  if(!actx&&(window.AudioContext||window.webkitAudioContext))
    actx=new (window.AudioContext||window.webkitAudioContext)();
  if(actx&&actx.state==='suspended')actx.resume();}catch(e){}}
function beep(f,dur,times){
  if(!actx)return;
  for(var i=0;i<times;i++){
    var t=actx.currentTime+i*(dur+0.12),o=actx.createOscillator(),g=actx.createGain();
    o.type='sine';o.frequency.value=f;
    g.gain.setValueAtTime(0.0001,t);
    g.gain.exponentialRampToValueAtTime(0.5,t+0.02);
    g.gain.exponentialRampToValueAtTime(0.0001,t+dur);
    o.connect(g);g.connect(actx.destination);o.start(t);o.stop(t+dur+0.05);
  }
}
function vibrate(p){try{if(navigator.vibrate)navigator.vibrate(p);}catch(e){}}
if('serviceWorker' in navigator){window.addEventListener('load',function(){
  navigator.serviceWorker.register('sw.js').catch(function(){});});}
""".replace("NWEEKS", str(len(WEEKS))).replace("NMONTHS", str(NMONTH)).replace("DOCTITLE", "'Weekly Kitchen'")

DOC = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#12100e">
<meta name="apple-mobile-web-app-title" content="Kitchen">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-192.png">
<title>Weekly Kitchen</title>
<style>{CSS}</style>
</head>
<body class="no-js">

{radios_html}

<header>
  <h1>🍳 Weekly Kitchen</h1>
  <div class="sub">Trader Joe's + Aldi · 6 months, no repeats · 3 dinners + a big batch</div>
  <div class="tabs">
      {tabs_html}
  </div>
</header>

{SPRITE}

<main>
  <div class="nojs">ℹ️ Everything works here — recipes, step-by-step cook mode and the cooking timers. Scripts are off in this view, so timers won't beep; open the file in a browser if you want sound.</div>
{panels_html}
</main>

<div class="view-wrap">
{sheets_html}
</div>

<div class="cook-wrap">
{cooks_html}
</div>

<div class="tmr-wrap">
{tmrs_html}
</div>

{guides_html}

<div class="tmr" id="tmr">
  <div class="tmr-ex" id="tmrEx">Timer</div>
  <div class="ring-wrap">
    <svg viewBox="0 0 120 120">
      <circle class="ring-bg" cx="60" cy="60" r="54"></circle>
      <circle class="ring-fg" id="ringFg" cx="60" cy="60" r="54"></circle>
    </svg>
    <div class="tmr-digits">
      <div class="tmr-time" id="tmrTime">0:00</div>
      <div class="tmr-state" id="tmrState">Cooking</div>
    </div>
  </div>
  <div class="tmr-adjust">
    <button class="adj" onclick="adjustTimer(-60)">−1m</button>
    <button class="adj" onclick="adjustTimer(60)">+1m</button>
    <button class="adj" onclick="adjustTimer(300)">+5m</button>
  </div>
  <div class="tmr-actions">
    <button class="btn-pause" id="pauseBtn" onclick="togglePause()">Pause</button>
    <button class="btn-done" onclick="stopTimer()">Done</button>
  </div>
</div>

<script>{JS}</script>
</body>
</html>
"""

os.makedirs(os.path.dirname(_OUT), exist_ok=True)
open(_OUT, "w", encoding="utf-8", newline="\n").write(DOC)
print("recipes:", len(R), "| timer durations:", DURS, "| bytes:", len(DOC))
