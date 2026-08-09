#!/usr/bin/env python3
# Single-file workout app. Renders AND runs its rest timers with zero JavaScript
# (CSS-driven countdowns). JavaScript, when available, upgrades the timer with
# sound, vibration, pause and +/- adjustments.
import html, json, os

# Portable output path relative to this script (see DEVELOPMENT.md).
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))          # repo root (…/daves-apps)
_OUT  = os.path.join(_REPO, "dist", "workout", "index.html")

PLAN = [
 dict(key="sun", label="SUN", emoji="🟣", color="#a78bfa", title="Upper Pull",
   sub="Back thickness / width / biceps",
   target="<b>Target:</b> most sets 1–3 RIR · final isolation set 0–1 RIR OK",
   ex=[
    ("Lat Pulldown","4 × 8–12","Controlled eccentric, full stretch",None,(90,120)),
    ("Chest-Supported DB Row","3 × 8–12","Drive elbows back; minimize momentum",None,(90,120)),
    ("Single-Arm Cable Row","3 × 10–15","Full stretch → controlled contraction",None,(75,90)),
    ("Rear Delt Fly","3 × 15–20","Controlled reps, avoid swinging",None,(45,75)),
    ("EZ-Bar or DB Curl","3 × 8–12","Full ROM; controlled eccentric",None,(60,90)),
    ("Incline DB Curl or Preacher Curl","3 × 10–15","Deep stretch at bottom",None,(60,90)),
   ]),
 dict(key="mon", label="MON", emoji="⚪", color="#9ca3af", title="Rest / Cardio",
   sub="Optional Zone 2 — 20–30 min", rest=True,
   rest_h="Optional Zone 2 Cardio · 20–30 min",
   rest_items=["Incline treadmill walk","Stationary bike","Elliptical"],
   rest_note="Conversational pace / moderate effort. No lifting required.",
   rest_pills=["💧 Hydrate","🥩 Protein","😴 Sleep 7–9h"],
   cardio_timer=(1500,"Zone 2 cardio","▶ 25-min cardio timer")),
 dict(key="tue", label="TUE", emoji="🟢", color="#4ade80", title="Lower Body",
   sub="Mass-focused / hypertrophy",
   target="<b>Target:</b> compounds 1–3 RIR · isolation 0–2 RIR",
   ex=[
    ("Hack Squat","4 × 8–12","Deep, controlled ROM · quads > spinal loading","Alt: Goblet Squat if hack squat unavailable",(120,180)),
    ("Romanian Deadlift","3 × 8–12","Moderate weight · 3-sec eccentric · deep hamstring stretch",None,(120,120)),
    ("Walking Lunges","3 × 10–12 / leg","Long controlled stride",None,(90,120)),
    ("Seated Leg Curl","3 × 10–15","Full stretch → hard contraction",None,(75,90)),
    ("Leg Extension","3 × 12–20","Controlled eccentric · pause/squeeze at top",None,(60,75)),
    ("Standing Calf Raises","4 × 10–20","Deep stretch at bottom · full contraction at top",None,(60,90)),
   ]),
 dict(key="wed", label="WED", emoji="⚪", color="#9ca3af", title="Rest / Cardio",
   sub="Optional cardio — 20–30 min", rest=True,
   rest_h="Optional Cardio · 20–30 min",
   rest_items=["Incline walk","Bike","Elliptical"],
   rest_note="Keep intensity moderate. Focus on recovery, hydration, nutrition and sleep.",
   rest_pills=["💧 Hydrate","🥗 Nutrition","😴 Recovery"],
   cardio_timer=(1500,"Zone 2 cardio","▶ 25-min cardio timer")),
 dict(key="thu", label="THU", emoji="🔴", color="#f87171", title="Upper Push",
   sub="Chest / delts / triceps",
   target="<b>Target:</b> pressing 1–3 RIR · isolation 0–2 RIR. Optional: controlled partials on the last set of laterals or triceps.",
   ex=[
    ("Incline DB Press","3 × 6–10","Controlled eccentric (~2–3 s) · deep stretch",None,(120,180)),
    ("Machine or Cable Chest Press","3 × 8–12","Constant tension · controlled ROM",None,(90,120)),
    ("Seated DB Shoulder Press","2–3 × 8–12","Controlled reps · avoid excessive arching",None,(90,120)),
    ("Cable Lateral Raises","4 × 12–20","Controlled reps · keep tension on lateral delt",None,(45,75)),
    ("Cable Fly (low → high)","2 × 12–15","Deep stretch · controlled contraction",None,(45,75)),
    ("Rope Triceps Pushdowns","3 × 10–15","Full extension · controlled eccentric",None,(60,75)),
    ("Overhead Triceps Extension","2 × 10–15","Deep stretch behind head",None,(60,75)),
   ]),
 dict(key="fri", label="FRI", emoji="🟡", color="#fbbf24", title="Rest",
   sub="Complete rest or light walking", rest=True,
   rest_h="Complete rest OR light walking",
   rest_items=["Sleep","Protein","Hydration","Recovery"],
   rest_note="Recover enough to grow — tomorrow is Full Body day.",
   rest_pills=["😴 7–9 h sleep","🥩 0.7–1.0 g/lb protein","💧 Hydration"]),
 dict(key="sat", label="SAT", emoji="🟠", color="#fb923c", title="Full Body",
   sub="Hypertrophy + lower-fatigue volume",
   target="<b>Target:</b> quality hard sets, 1–3 RIR. Finish with the 10–15 min cardio below.",
   ex=[
    ("Dumbbell Bench Press","3 × 10–12","Controlled eccentric",None,(90,120)),
    ("Cable Row","3 × 10–12","Full stretch → contraction",None,(90,120)),
    ("Bulgarian Split Squat","3 × 10–12 / leg","Controlled descent · deep ROM",None,(90,120)),
    ("Seated or Lying Leg Curl","3 × 12–15","Full stretch",None,(60,90)),
    ("Cable/DB Lateral Raise","3 × 15–20","Strict form",None,(45,60)),
    ("Optional Arms — Cable Curl","2 × 12–15","Optional finisher volume",None,(45,60)),
    ("Optional Arms — Rope Pushdown","2 × 12–15","Optional finisher volume",None,(45,60)),
   ],
   finisher=("🔥 Finisher · 10–15 min",
     "Choose ONE: incline treadmill walk, stationary bike, or sled. Example: 40 s moderate → 20 s push, repeat for 10–12 min. Don't turn this into an all-out HIIT session every week — the goal is extra cardiovascular work without compromising recovery.",
     600,"Cardio finisher","▶ Start 10-min finisher")),
]

# durations that need a CSS timer; those in PAIRED get an a/b pair so "Restart" always replays
DURATIONS = [60, 75, 90, 120, 180, 600, 1500]
PAIRED    = {60, 75, 90, 120, 180, 600}
CIRC = 339.292   # 2 * pi * 54

def esc(s): return html.escape(s, quote=True)
def jsarg(s): return html.escape(json.dumps(s), quote=True)
def fmt_rest(r): return f"{r[0]}–{r[1]} s" if r[0] != r[1] else f"{r[0]} s"
def mmss(t): return f"{t//60}:{t%60:02d}"
def variants(sec): return ["a","b"] if sec in PAIRED else ["a"]

# ---------------- tabs / radios ----------------
tabs_html = "\n      ".join(
  f'<label class="tab" for="d{i}" style="--tabc:{d["color"]};--tabbg:{d["color"]}2e">'
  f'<span>{d["emoji"]} {d["label"]}</span><small>{esc(d["title"])}</small></label>'
  for i, d in enumerate(PLAN))

day_radios = "\n".join(
  f'<input type="radio" name="day" id="d{i}" class="dayradio"{" checked" if i == 0 else ""}>'
  for i in range(len(PLAN)))

tmr_radios = ['<input type="radio" name="tmr" id="t-none" class="tmrradio" checked>']
for sec in DURATIONS:
    for v in variants(sec):
        tmr_radios.append(f'<input type="radio" name="tmr" id="t{sec}{v}" class="tmrradio">')
tmr_radios = "\n".join(tmr_radios)

active_tab_rules   = ",\n".join(f'#d{i}:checked ~ header label[for="d{i}"]' for i in range(len(PLAN)))
active_panel_rules = ",\n".join(f'#d{i}:checked ~ main #p{i}' for i in range(len(PLAN)))
day_accent_rules   = "\n".join(
  f'#d{i}:checked ~ .tmr-wrap{{--accent:{d["color"]}; --accent-soft:{d["color"]}26;}}'
  for i, d in enumerate(PLAN))

show_rules = ",\n".join(
  f'#t{sec}{v}:checked ~ .tmr-wrap #tc{sec}{v}'
  for sec in DURATIONS for v in variants(sec))

# ---------------- CSS keyframes per duration ----------------
keyframes = [
  f"@keyframes ringrun{{to{{stroke-dashoffset:{CIRC};}}}}",
  "@keyframes fadeout{to{opacity:0;}}",
  "@keyframes fadein{from{opacity:0;}to{opacity:1;}}",
  "@keyframes flashbg{50%{background:var(--accent-soft);}}",
  "@keyframes pulse{0%,100%{transform:translateY(-50%) scale(1);}"
  "50%{transform:translateY(-50%) scale(1.07);}}",
]
for sec in DURATIONS:
    keyframes.append(f"@keyframes roll{sec}{{to{{transform:translateY(-{sec}em);}}}}")
keyframes_css = "\n  ".join(keyframes)

# ---------------- CSS timer overlays ----------------
def overlay(sec, v):
    other = "b" if v == "a" else "a"
    digits = "".join(f"<i>{mmss(t)}</i>" for t in range(sec, -1, -1))
    restart = (f'<label class="btn-pause" for="t{sec}{other}">↻ Restart</label>'
               if sec in PAIRED else
               f'<label class="btn-pause" for="t-none">✕ Close</label>')
    return f'''<div class="tmr-css" id="tc{sec}{v}" style="animation:flashbg .5s {sec}s 4;">
  <label class="tmr-min" for="t-none">Close ✕</label>
  <div class="tmr-ex">{mmss(sec)} rest</div>
  <div class="ring-wrap">
    <svg viewBox="0 0 120 120">
      <circle class="ring-bg" cx="60" cy="60" r="54"></circle>
      <circle class="ring-fg" cx="60" cy="60" r="54"
        style="stroke-dasharray:{CIRC}; animation:ringrun {sec}s linear forwards;"></circle>
    </svg>
    <div class="tmr-digits">
      <div class="cd" style="animation:fadeout .2s {sec}s forwards;"><div class="cd-roll" style="animation:roll{sec} {sec}s steps({sec}) forwards;">{digits}</div></div>
      <div class="tmr-state" style="animation:fadeout .01s {sec}s forwards;">Resting</div>
      <div class="tmr-go" style="animation:fadein .25s {sec}s forwards, pulse 1s {sec}s infinite;">GO — next set!</div>
    </div>
  </div>
  <div class="tmr-actions">
    {restart}
    <label class="btn-done" for="t-none">Done — lift!</label>
  </div>
</div>'''

overlays_html = "\n".join(overlay(sec, v) for sec in DURATIONS for v in variants(sec))

def start_btn(sec, name, text=None, cls="rest-btn"):
    inner = text if text else ('<svg viewBox="0 0 24 24" fill="currentColor">'
                               '<path d="M8 5v14l11-7z"></path></svg> Start rest')
    return (f'<label class="{cls}" for="t{sec}a" data-sec="{sec}" '
            f'data-name="{esc(name)}">{inner}</label>')

# ---------------- panels ----------------
panels = []
for i, d in enumerate(PLAN):
    p = [f'<section class="panel" id="p{i}" '
         f'style="--accent:{d["color"]};--accent-soft:{d["color"]}26;--accent-line:{d["color"]}66;">']
    p.append(f'<div class="day-head"><h2 class="day-title">{d["emoji"]} {d["label"]} — {esc(d["title"])}</h2>'
             f'<p class="day-sub">{esc(d["sub"])}</p></div>')
    if d.get("rest"):
        items = "".join(f"<li>{esc(x)}</li>" for x in d["rest_items"])
        pills = "".join(f'<span class="pill">{esc(x)}</span>' for x in d["rest_pills"])
        p.append(f'<div class="rest-day"><h3>{esc(d["rest_h"])}</h3><ul>{items}</ul>'
                 f'<p class="rest-note">{esc(d["rest_note"])}</p>'
                 f'<div class="pill-row">{pills}</div>')
        if d.get("cardio_timer"):
            sec, lbl, txt = d["cardio_timer"]
            p.append(f'<div class="btn-wrap">{start_btn(sec, lbl, esc(txt))}</div>')
        p.append("</div>")
    else:
        p.append(f'<div class="target-box">🎯 {d["target"]}</div>')
        for j, (name, scheme, cue, alt, r) in enumerate(d["ex"]):
            cid = f"c{i}_{j}"
            altline = f'<div class="ex-alt">{esc(alt)}</div>' if alt else ""
            p.append(
              f'<div class="ex-card">'
              f'<input type="checkbox" class="dchk" id="{cid}">'
              f'<div class="ex-body">'
              f'<div class="ex-top"><span class="ex-num">{j+1}</span>'
              f'<div class="ex-main"><div class="ex-name">{esc(name)}</div>'
              f'<div class="ex-scheme">{esc(scheme)}</div>'
              f'<div class="ex-cue">{esc(cue)}</div>{altline}</div>'
              f'<label class="done-toggle" for="{cid}" aria-label="Mark done">✓</label></div>'
              f'<div class="ex-foot"><span class="rest-label">Rest {fmt_rest(r)}</span>'
              f'{start_btn(r[1], name)}</div></div></div>')
        if d.get("finisher"):
            h, note, sec, lbl, txt = d["finisher"]
            p.append(f'<div class="rest-day finisher"><h3>{esc(h)}</h3>'
                     f'<p class="rest-note">{esc(note)}</p>'
                     f'<div class="btn-wrap">{start_btn(sec, lbl, esc(txt))}</div></div>')
    p.append("</section>")
    panels.append("\n".join(p))
panels_html = "\n".join(panels)

presets_html = "\n      ".join(
  start_btn(s, "Quick rest", mmss(s), cls="preset") for s in [60, 90, 120, 180])

GUIDE = """
  <div class="section-label">Reference</div>
  <details class="guide"><summary>⏱️ Rest period rules</summary><div class="guide-body">
    <table>
      <tr><td><b>Heavy compound</b><br>Hack squat · RDL · DB press · rows · shoulder press</td><td>2–3 min</td></tr>
      <tr><td><b>Moderate compound</b><br>Lunges · pulldowns · chest press · DB bench</td><td>90–120 s</td></tr>
      <tr><td><b>Isolation</b><br>Laterals · curls · triceps · leg extensions · leg curls · calves</td><td>45–90 s</td></tr>
    </table>
    <b>Rule:</b> if you're still significantly out of breath or your muscles haven't recovered enough to perform the next set properly, take additional rest. Don't sacrifice performance just to hit an arbitrary rest timer.
  </div></details>

  <details class="guide"><summary>📈 Double progression</summary><div class="guide-body">
    For a rep range like <b>3 × 6–10</b>: start with a weight you can perform for roughly 10 / 9 / 8. Over subsequent workouts, increase total reps → 10 / 10 / 9 → 10 / 10 / 10. Once you hit the top of the rep range on <b>every set</b> with good form, increase the weight and repeat the process.
    <span class="mono">70-lb DB Incline Press
Week 1 → 10 / 9 / 8
Week 2 → 10 / 10 / 9
Week 3 → 10 / 10 / 10   ⬆ increase to 75 lb
Week 4 → 8 / 7 / 6 … continue progressing</span>
  </div></details>

  <details class="guide"><summary>🎯 RIR — reps in reserve</summary><div class="guide-body">
    <b>Compound movements:</b> generally 1–3 RIR<br>
    <b>Isolation movements:</b> generally 0–2 RIR<br>
    <b>Final isolation set:</b> occasionally 0–1 RIR<br><br>
    You do NOT need to take every set to failure. The goal is high-quality hard sets while maintaining enough recovery to progress week after week.
  </div></details>

  <details class="guide"><summary>🧠 Training principles</summary><div class="guide-body">
    <b>1. Progressive overload</b> — gradually increase weight OR reps OR quality of execution over time.<br><br>
    <b>2. Mechanical tension &gt; chasing the pump</b> — the pump is enjoyable, but prioritise load + ROM + proximity to failure + progressive overload.<br><br>
    <b>3. Controlled eccentrics</b> — roughly 2–3 s down. Don't obsess over counting seconds; the goal is controlled → stable → full ROM rather than dropping the weight.<br><br>
    <b>4. Full ROM</b> — meaningful stretch and complete contraction. Especially incline curls, RDLs, leg curls, leg extensions, calf raises, cable flyes and lateral raises.<br><br>
    <b>5. Partial reps</b> — an optional intensity technique, not something that needs to happen every workout. Best used occasionally at the end of isolation work when already near failure.
  </div></details>

  <details class="guide"><summary>🥩 Recovery targets</summary><div class="guide-body">
    <b>Protein:</b> ~0.7–1.0 g per lb bodyweight per day, spread across several meals.<br>
    <b>Sleep:</b> 7–9 hours per night.<br>
    <b>Hydration:</b> consistent throughout the day.<br>
    <b>Calories:</b> small surplus for muscle gain · around maintenance + high protein for recomposition. Avoid aggressive bulking if minimising fat gain is important.<br><br>
    <b>Cardio:</b> 2–3 sessions per week, mostly 20–30 min moderate intensity. Saturday's post-workout finisher counts as one.
  </div></details>

  <details class="guide"><summary>📊 Progress tracking</summary><div class="guide-body">
    Record after every workout: <b>exercise → weight → reps → RIR</b>.
    <span class="mono">Incline DB Press
70s — 10 / 9 / 8    ~2 RIR
next time → 70s — 10 / 10 / 9</span>
    Track weekly: body weight, key lifts, reps/weights, waist measurement, progress photos, general energy and recovery.<br><br>
    Evaluate after 6–8 weeks. If strength/reps are progressing and measurements are moving in the desired direction — <b>keep the program</b>. Don't change exercises simply because you're getting bored.
  </div></details>

  <details class="guide"><summary>⭐ Primary goal</summary><div class="guide-body">
    Train hard enough to stimulate growth. Recover enough to grow. Progress consistently.<br><br>
    The program does not need to destroy you. <b>Consistency + progressive overload over months = results.</b>
  </div></details>
"""

SPOTIFY_SVG = ('<svg viewBox="0 0 24 24"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.5 '
 '17.3a.75.75 0 0 1-1.03.25c-2.82-1.72-6.37-2.11-10.55-1.16a.75.75 0 1 1-.33-1.46c4.57-1.05 8.5-.6 11.66 1.34.35.21.46.67.25 '
 '1.03zm1.47-3.27a.94.94 0 0 1-1.29.31c-3.23-1.98-8.15-2.56-11.97-1.4a.94.94 0 1 1-.55-1.79c4.37-1.33 9.8-.68 13.5 '
 '1.6.44.27.58.85.31 1.28zm.13-3.4C15.24 8.33 8.87 8.12 5.17 9.24a1.12 1.12 0 1 1-.65-2.15c4.25-1.29 11.31-1.04 15.77 '
 '1.6a1.12 1.12 0 0 1-1.19 1.94z"/></svg>')

DOC = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0d0f14">
<meta name="apple-mobile-web-app-title" content="Workout">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-192.png">
<title>Hypertrophy Hub</title>
<style>
  :root{{
    --bg:#0d0f14; --card:#161a22; --card2:#1d222d; --line:#262c3a;
    --txt:#e7eaf0; --dim:#8b93a5; --dimmer:#5c6474;
    --green:#4ade80; --yellow:#fbbf24; --red:#f87171; --spotify:#1DB954;
    --accent:#a78bfa; --accent-soft:#a78bfa26; --accent-line:#a78bfa66;
    --safe-b: env(safe-area-inset-bottom, 0px);
  }}
  *{{box-sizing:border-box; -webkit-tap-highlight-color:transparent;}}
  html,body{{margin:0; padding:0; background:var(--bg); color:var(--txt);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    font-size:16px; line-height:1.45;}}
  body{{padding-bottom:calc(120px + var(--safe-b));}}
  .dayradio,.tmrradio,.sheetchk,.dchk{{position:absolute; opacity:0; pointer-events:none; width:0; height:0;}}

  {keyframes_css}

  header{{position:sticky; top:0; z-index:30; background:rgba(13,15,20,.94);
    -webkit-backdrop-filter:blur(12px); backdrop-filter:blur(12px);
    border-bottom:1px solid var(--line); padding:14px 16px 0;}}
  .h-row{{display:flex; align-items:center; justify-content:space-between; gap:8px;}}
  h1{{font-size:19px; margin:0; font-weight:800; letter-spacing:.2px;}}
  .wake-btn{{border:1px solid var(--line); background:var(--card); color:var(--dim);
    border-radius:20px; font-size:12px; padding:6px 12px; font-weight:700; cursor:pointer;}}
  .wake-btn.on{{color:#0d0f14; background:var(--yellow); border-color:var(--yellow);}}
  .no-js .wake-btn{{display:none;}}

  .tabs{{display:flex; gap:6px; overflow-x:auto; padding:12px 0;
    scrollbar-width:none; -ms-overflow-style:none;}}
  .tabs::-webkit-scrollbar{{display:none;}}
  .tab{{flex:0 0 auto; border:1px solid var(--line); background:var(--card);
    color:var(--dim); border-radius:14px; padding:8px 13px; font-size:13px;
    font-weight:700; display:flex; flex-direction:column; align-items:center; gap:1px;
    min-width:62px; cursor:pointer; user-select:none;}}
  .tab small{{font-size:10px; font-weight:600; opacity:.75; white-space:nowrap;}}
  {active_tab_rules}
  {{color:#fff; border-color:var(--tabc); background:var(--tabbg);}}
  .tab.is-today::after{{content:""; width:5px; height:5px; border-radius:50%;
    background:var(--tabc); margin-top:3px;}}

  main{{padding:16px; max-width:640px; margin:0 auto;}}
  .panel{{display:none;}}
  {active_panel_rules}
  {{display:block;}}

  .day-head{{margin:2px 0 6px;}}
  .day-title{{font-size:24px; font-weight:800; margin:0;}}
  .day-sub{{color:var(--dim); font-size:14px; margin:2px 0 0; font-weight:600;}}
  .target-box{{margin:12px 0 4px; background:var(--card); border:1px solid var(--line);
    border-radius:14px; padding:10px 14px; font-size:13px; color:var(--dim);}}
  .target-box b{{color:var(--txt);}}

  .ex-card{{background:var(--card); border:1px solid var(--line); border-radius:16px;
    padding:14px 14px 12px; margin:12px 0;}}
  .ex-top{{display:flex; align-items:flex-start; gap:10px;}}
  .ex-main{{flex:1; min-width:0;}}
  .ex-num{{color:var(--accent); font-weight:800; font-size:13px; flex:0 0 auto;
    background:var(--accent-soft); border-radius:8px; padding:2px 8px; margin-top:2px;}}
  .ex-name{{font-weight:800; font-size:16.5px;}}
  .ex-scheme{{color:var(--accent); font-weight:800; font-size:14px; margin:5px 0 2px;}}
  .ex-cue{{color:var(--dim); font-size:13px;}}
  .ex-alt{{color:var(--dimmer); font-size:12px; margin-top:4px; font-style:italic;}}
  .ex-foot{{display:flex; align-items:center; justify-content:space-between;
    margin-top:10px; gap:10px;}}
  .rest-label{{font-size:12px; color:var(--dimmer); font-weight:700;}}
  .rest-btn{{border:none; border-radius:12px; font-weight:800; font-size:14px;
    padding:10px 16px; color:#0d0f14; background:var(--accent); cursor:pointer;
    display:inline-flex; align-items:center; gap:7px; font-family:inherit; user-select:none;}}
  .rest-btn:active{{transform:scale(.97);}}
  .rest-btn svg{{width:14px; height:14px;}}
  .btn-wrap{{margin-top:15px;}}
  .done-toggle{{width:26px; height:26px; border-radius:50%; border:2px solid var(--line);
    background:transparent; flex:0 0 auto; cursor:pointer; font-size:14px; font-weight:800;
    display:flex; align-items:center; justify-content:center; color:transparent; margin-top:2px;}}
  .dchk:checked ~ .ex-body{{opacity:.42;}}
  .dchk:checked ~ .ex-body .done-toggle{{background:var(--green); border-color:var(--green); color:#0d0f14;}}

  .rest-day{{background:var(--card); border:1px solid var(--line); border-radius:16px;
    padding:18px; margin-top:14px;}}
  .rest-day.finisher{{border-color:var(--accent-line);}}
  .rest-day h3{{margin:0 0 8px; font-size:17px;}}
  .rest-day ul{{margin:8px 0 0; padding-left:20px; color:var(--dim); font-size:14px;}}
  .rest-day li{{margin:4px 0;}}
  .rest-note{{color:var(--dim); font-size:13.5px; margin:10px 0 0;}}
  .pill-row{{display:flex; flex-wrap:wrap; gap:8px; margin-top:12px;}}
  .pill{{background:var(--card2); border:1px solid var(--line); color:var(--dim);
    font-size:12.5px; font-weight:700; border-radius:20px; padding:6px 12px;}}

  .section-label{{font-size:12px; letter-spacing:1.4px; text-transform:uppercase;
    color:var(--dimmer); font-weight:800; margin:28px 0 6px;}}
  details.guide{{background:var(--card); border:1px solid var(--line); border-radius:14px;
    margin:10px 0; overflow:hidden;}}
  details.guide summary{{padding:13px 16px; font-weight:800; font-size:15px;
    cursor:pointer; list-style:none; display:flex; justify-content:space-between; align-items:center;}}
  details.guide summary::-webkit-details-marker{{display:none;}}
  details.guide summary::after{{content:"+"; color:var(--dimmer); font-size:18px; font-weight:600;}}
  details.guide[open] summary::after{{content:"–";}}
  .guide-body{{padding:0 16px 14px; color:var(--dim); font-size:14px;}}
  .guide-body b{{color:var(--txt);}}
  .guide-body table{{width:100%; border-collapse:collapse; margin:8px 0; font-size:13px;}}
  .guide-body td{{padding:6px 8px; border-top:1px solid var(--line); vertical-align:top;}}
  .guide-body td:last-child{{text-align:right; color:var(--txt); font-weight:700; white-space:nowrap;}}
  .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12.5px;
    background:var(--card2); border-radius:8px; padding:10px 12px; display:block;
    margin:10px 0 0; color:var(--txt); white-space:pre-wrap; line-height:1.6;}}

  .dock{{position:fixed; left:0; right:0; bottom:0; z-index:40;
    background:rgba(18,21,28,.97); -webkit-backdrop-filter:blur(14px); backdrop-filter:blur(14px);
    border-top:1px solid var(--line); padding:10px 14px calc(10px + var(--safe-b));}}
  .dock-inner{{max-width:640px; margin:0 auto; display:flex; flex-direction:column; gap:8px;}}
  .dock-row{{display:flex; gap:8px; align-items:center;}}
  .preset{{flex:1; border:1px solid var(--line); background:var(--card); color:var(--txt);
    border-radius:12px; padding:11px 0; font-size:14px; font-weight:800; cursor:pointer;
    font-family:inherit; text-align:center; display:block; user-select:none;}}
  .preset:active{{transform:scale(.97);}}
  .spotify-toggle{{flex:0 0 auto; width:46px; height:46px; border-radius:12px; border:1px solid var(--line);
    background:var(--card); display:flex; align-items:center; justify-content:center; cursor:pointer;}}
  .spotify-toggle svg{{width:24px; height:24px; fill:var(--spotify);}}
  .minibar{{display:none; align-items:center; gap:10px; background:var(--card2);
    border:1px solid var(--accent); border-radius:12px; padding:8px 12px; cursor:pointer;}}
  .minibar.show{{display:flex;}}
  .mb-time{{font-weight:800; font-variant-numeric:tabular-nums; font-size:18px; color:var(--accent);}}
  .mb-ex{{flex:1; font-size:13px; color:var(--dim); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}}
  .mb-hint{{color:var(--dim); font-size:11px; font-weight:800; letter-spacing:.5px;}}

  .sheet-veil{{position:fixed; inset:0; background:rgba(0,0,0,.55); z-index:50;
    opacity:0; pointer-events:none; transition:opacity .22s ease;}}
  .sheet{{position:fixed; left:0; right:0; bottom:0; z-index:51; background:var(--card);
    border-radius:20px 20px 0 0; border:1px solid var(--line); border-bottom:none;
    padding:18px 18px calc(24px + var(--safe-b)); transform:translateY(105%);
    transition:transform .25s ease; max-height:80vh; overflow-y:auto;}}
  #musicOpen:checked ~ .sheet-veil{{opacity:1; pointer-events:auto;}}
  #musicOpen:checked ~ .sheet{{transform:translateY(0);}}
  .sheet h3{{margin:0 0 2px; display:flex; align-items:center; gap:8px; font-size:18px;}}
  .sheet h3 svg{{width:22px; height:22px; fill:var(--spotify);}}
  .sheet p.hint{{color:var(--dim); font-size:13px; margin:6px 0 14px;}}
  .music-link{{display:flex; align-items:center; gap:12px; background:var(--card2);
    border:1px solid var(--line); border-radius:14px; padding:13px 14px; margin:8px 0;
    color:var(--txt); text-decoration:none; font-weight:700; font-size:15px;}}
  .music-link:active{{background:var(--line);}}
  .ml-ico{{width:36px; height:36px; border-radius:10px; display:flex;
    align-items:center; justify-content:center; font-size:18px; flex:0 0 auto;
    background:rgba(29,185,84,.18);}}
  .music-link small{{display:block; color:var(--dim); font-weight:500; font-size:12px;}}
  .add-row{{display:flex; gap:8px; margin-top:14px;}}
  .no-js .add-row, .no-js .add-note{{display:none;}}
  .add-row input{{flex:1; background:var(--bg); border:1px solid var(--line); color:var(--txt);
    border-radius:12px; padding:11px 12px; font-size:14px; min-width:0; font-family:inherit;}}
  .add-row button{{border:none; background:var(--spotify); color:#04220f; font-weight:800;
    border-radius:12px; padding:0 18px; font-size:14px; cursor:pointer; font-family:inherit;}}
  .add-note{{color:var(--dimmer); font-size:11.5px; margin-top:8px;}}
  .sheet-close{{display:block; text-align:center; margin-top:14px; color:var(--dim);
    font-weight:800; font-size:14px; padding:10px; cursor:pointer;}}

  /* ---------- timer overlays (shared look) ---------- */
  .tmr, .tmr-css{{position:fixed; inset:0; z-index:60; background:rgba(13,15,20,.98);
    display:none; flex-direction:column; align-items:center; justify-content:center;
    padding:24px; text-align:center;}}
  .tmr.show{{display:flex;}}
  {show_rules}
  {{display:flex;}}
  .js .tmr-css{{display:none !important;}}
  .tmr.flash{{animation:flashbg .5s ease 4;}}
  .tmr-ex{{color:var(--dim); font-size:15px; font-weight:700; max-width:90%;}}
  .ring-wrap{{position:relative; width:min(72vw,300px); height:min(72vw,300px); margin:22px 0;}}
  .ring-wrap svg{{width:100%; height:100%; transform:rotate(-90deg);}}
  .ring-bg{{fill:none; stroke:var(--line); stroke-width:7;}}
  .ring-fg{{fill:none; stroke:var(--accent); stroke-width:7; stroke-linecap:round;}}
  .tmr .ring-fg{{transition:stroke-dashoffset .95s linear;}}
  .tmr-digits{{position:absolute; inset:0; display:flex; flex-direction:column;
    align-items:center; justify-content:center;}}
  .tmr-time{{font-size:62px; font-weight:800; font-variant-numeric:tabular-nums;}}
  .tmr-time.warn{{color:var(--yellow);}}
  .tmr-time.overtime{{color:var(--green);}}
  .tmr-state{{font-size:12px; letter-spacing:2px; text-transform:uppercase;
    color:var(--dimmer); font-weight:800; margin-top:2px;}}
  .tmr-adjust{{display:flex; gap:10px; margin-bottom:18px;}}
  .adj{{border:1px solid var(--line); background:var(--card); color:var(--txt);
    border-radius:12px; padding:10px 18px; font-size:15px; font-weight:800;
    cursor:pointer; font-family:inherit;}}
  .tmr-actions{{display:flex; gap:10px; width:100%; max-width:340px;}}
  .tmr-actions button, .tmr-actions label{{flex:1; border:none; border-radius:14px; padding:15px 0;
    font-size:16px; font-weight:800; cursor:pointer; font-family:inherit; text-align:center;
    user-select:none;}}
  .btn-pause{{background:var(--card2); color:var(--txt); border:1px solid var(--line) !important;}}
  .btn-done{{background:var(--accent); color:#0d0f14;}}
  .tmr-min{{position:absolute; top:calc(14px + env(safe-area-inset-top,0px)); right:16px;
    border:1px solid var(--line); background:var(--card); color:var(--dim); border-radius:12px;
    padding:8px 14px; font-weight:700; font-size:13px; cursor:pointer; font-family:inherit;
    user-select:none;}}

  /* ---------- CSS-only countdown ---------- */
  .cd{{height:1em; overflow:hidden; font-size:62px; font-weight:800; line-height:1;
    font-variant-numeric:tabular-nums;}}
  .cd-roll i{{display:block; height:1em; font-style:normal;}}
  .tmr-go{{position:absolute; left:0; right:0; top:50%; transform:translateY(-50%); opacity:0;
    font-size:30px; font-weight:800; color:var(--green); pointer-events:none; letter-spacing:.3px;}}

  .nojs{{display:none; background:#1e2a3a; border:1px solid #39506e; color:#a9c6e8;
    border-radius:12px; padding:11px 14px; font-size:12.5px; margin:0 0 14px;}}
  .no-js .nojs{{display:block; border-color:#39506e;}}
</style>
</head>
<body class="no-js">

{day_radios}
{tmr_radios}
<input type="checkbox" class="sheetchk" id="musicOpen">

<header>
  <div class="h-row">
    <h1>💪 Hypertrophy Hub</h1>
    <button class="wake-btn" id="wakeBtn" onclick="toggleWake()">☀︎ Keep screen on</button>
  </div>
  <div class="tabs" id="tabs">
      {tabs_html}
  </div>
</header>

<main>
  <div class="nojs">ℹ️ Timers work right here — tap any <b>Start rest</b> button. Scripts are off in this view, so there's no beep or buzz at zero; open the file in a browser if you want the sound.</div>
{panels_html}
{GUIDE}
</main>

<div class="dock">
  <div class="dock-inner">
    <div class="minibar" id="minibar" onclick="showTimer()">
      <span class="mb-time" id="mbTime">0:00</span>
      <span class="mb-ex" id="mbEx">Rest</span>
      <span class="mb-hint">TAP TO OPEN</span>
    </div>
    <div class="dock-row">
      {presets_html}
      <label class="spotify-toggle" for="musicOpen" aria-label="Music">{SPOTIFY_SVG}</label>
    </div>
  </div>
</div>

<label class="sheet-veil" for="musicOpen"></label>
<div class="sheet">
  <h3>{SPOTIFY_SVG} Workout music</h3>
  <p class="hint">These open in your Spotify app — music keeps playing in the background while the timer runs.</p>
  <div id="musicLinks">
    <a class="music-link" href="https://open.spotify.com" target="_blank" rel="noopener">
      <span class="ml-ico">🎧</span><span>Open Spotify<small>Resume whatever you were playing</small></span></a>
    <a class="music-link" href="https://open.spotify.com/playlist/37i9dQZF1DX76Wlfdnj7AP" target="_blank" rel="noopener">
      <span class="ml-ico">🔥</span><span>Beast Mode<small>Spotify's flagship workout playlist</small></span></a>
    <a class="music-link" href="https://open.spotify.com/playlist/37i9dQZF1DXdxcBWuJkbcy" target="_blank" rel="noopener">
      <span class="ml-ico">⚡</span><span>Motivation Mix<small>High-energy lifting hits</small></span></a>
    <a class="music-link" href="https://open.spotify.com/search/gym%20workout%20playlist" target="_blank" rel="noopener">
      <span class="ml-ico">🔍</span><span>Browse workout playlists<small>Search "gym workout" in Spotify</small></span></a>
  </div>
  <div class="add-row">
    <input type="url" id="plUrl" placeholder="Paste a Spotify playlist link…" inputmode="url">
    <button onclick="addPlaylist()">Add</button>
  </div>
  <div class="add-note">Added links last for this visit. To keep one permanently, ask Claude to bake it into the app.</div>
  <label class="sheet-close" for="musicOpen">Close</label>
</div>

<div class="tmr-wrap">
{overlays_html}
</div>

<div class="tmr" id="tmr">
  <button class="tmr-min" onclick="hideTimer()">Minimize ▾</button>
  <div class="tmr-ex" id="tmrEx">Rest</div>
  <div class="ring-wrap">
    <svg viewBox="0 0 120 120">
      <circle class="ring-bg" cx="60" cy="60" r="54"></circle>
      <circle class="ring-fg" id="ringFg" cx="60" cy="60" r="54"></circle>
    </svg>
    <div class="tmr-digits">
      <div class="tmr-time" id="tmrTime">0:00</div>
      <div class="tmr-state" id="tmrState">Resting</div>
    </div>
  </div>
  <div class="tmr-adjust">
    <button class="adj" onclick="adjustTimer(-15)">−15s</button>
    <button class="adj" onclick="adjustTimer(15)">+15s</button>
    <button class="adj" onclick="adjustTimer(30)">+30s</button>
  </div>
  <div class="tmr-actions">
    <button class="btn-pause" id="pauseBtn" onclick="togglePause()">Pause</button>
    <button class="btn-done" onclick="stopTimer()">Done — lift!</button>
  </div>
</div>

<script>
document.body.className = 'js';

/* today's tab */
(function(){{
  try{{
    var n = new Date().getDay(), r = document.getElementById('d'+n);
    if(r){{
      r.checked = true;
      var lab = document.querySelector('label[for="d'+n+'"]');
      if(lab){{ lab.classList.add('is-today');
        if(lab.scrollIntoView) lab.scrollIntoView({{inline:'center', block:'nearest'}}); }}
    }}
  }}catch(e){{}}
}})();

/* accent follows the day you're viewing */
function syncAccent(){{
  var c = document.querySelector('.dayradio:checked'); if(!c) return;
  var panel = document.getElementById('p'+c.id.slice(1)); if(!panel) return;
  var cs = getComputedStyle(panel);
  document.documentElement.style.setProperty('--accent', cs.getPropertyValue('--accent'));
  document.documentElement.style.setProperty('--accent-soft', cs.getPropertyValue('--accent-soft'));
}}
Array.prototype.forEach.call(document.querySelectorAll('.dayradio'), function(r){{
  r.addEventListener('change', syncAccent);
}});
syncAccent();

/* start buttons: with JS we use the richer timer instead of the CSS one */
Array.prototype.forEach.call(document.querySelectorAll('[data-sec]'), function(el){{
  el.addEventListener('click', function(e){{
    e.preventDefault();
    startTimer(parseInt(el.getAttribute('data-sec'),10), el.getAttribute('data-name'));
  }});
}});

/* ---------- JS rest timer ---------- */
var CIRC = 2*Math.PI*54;
var ringFg = document.getElementById('ringFg');
ringFg.style.strokeDasharray = CIRC;

var tTotal=0, tEnd=0, tRemain=0, tPaused=false, tick=null, warned=false, finished=false, tLabel='Rest';
var tmr=document.getElementById('tmr'), tmrTime=document.getElementById('tmrTime'),
    tmrEx=document.getElementById('tmrEx'), tmrState=document.getElementById('tmrState'),
    minibar=document.getElementById('minibar'), mbTime=document.getElementById('mbTime'),
    mbEx=document.getElementById('mbEx'), pauseBtn=document.getElementById('pauseBtn');

function startTimer(sec,label){{
  ensureAudio();
  tTotal=sec; tRemain=sec; tEnd=Date.now()+sec*1000;
  tPaused=false; warned=false; finished=false; tLabel=label||'Rest';
  tmrEx.textContent=tLabel; tmrState.textContent='Resting';
  pauseBtn.textContent='Pause';
  showTimer(); renderTimer();
  clearInterval(tick); tick=setInterval(renderTimer,250);
  vibrate([40]);
}}
function renderTimer(){{
  if(!tPaused) tRemain=Math.round((tEnd-Date.now())/1000);
  var r=tRemain, disp=r>=0?r:-r;
  var m=Math.floor(disp/60), s=disp%60;
  var str=(r<0?'+':'')+m+':'+(s<10?'0':'')+s;
  tmrTime.textContent=str; mbTime.textContent=str; mbEx.textContent=tLabel;
  tmrTime.className='tmr-time'+(r<=10&&r>0?' warn':'')+(r<=0?' overtime':'');
  var frac=Math.max(0,Math.min(1,r/tTotal));
  ringFg.style.strokeDashoffset = CIRC*(1-frac);
  if(r<=10 && r>0 && !warned){{ warned=true; beep(880,.12,2); vibrate([80,60,80]); }}
  if(r<=0 && !finished){{
    finished=true;
    tmrState.textContent='GO — next set!';
    tmr.classList.add('flash'); setTimeout(function(){{tmr.classList.remove('flash');}},2200);
    beep(1046,.18,3); vibrate([250,120,250,120,400]);
    document.title='🔔 GO! — Hypertrophy Hub';
    setTimeout(function(){{document.title='Hypertrophy Hub';}},5000);
  }}
}}
function adjustTimer(d){{
  if(tPaused){{ tRemain+=d; }} else {{ tEnd+=d*1000; }}
  if(finished && (tEnd-Date.now())>0){{ finished=false; warned=false; tmrState.textContent='Resting'; }}
  tTotal=Math.max(tTotal, Math.round((tEnd-Date.now())/1000));
  renderTimer();
}}
function togglePause(){{
  if(tPaused){{ tEnd=Date.now()+tRemain*1000; tPaused=false; pauseBtn.textContent='Pause';
    tmrState.textContent = finished ? 'GO — next set!' : 'Resting'; }}
  else {{ tRemain=Math.round((tEnd-Date.now())/1000); tPaused=true; pauseBtn.textContent='Resume';
    tmrState.textContent='Paused'; }}
}}
function stopTimer(){{ clearInterval(tick); tick=null; tmr.classList.remove('show'); minibar.classList.remove('show'); }}
function showTimer(){{ tmr.classList.add('show'); minibar.classList.remove('show'); }}
function hideTimer(){{ tmr.classList.remove('show'); if(tick) minibar.classList.add('show'); }}

var actx=null;
function ensureAudio(){{
  try{{
    if(!actx && (window.AudioContext||window.webkitAudioContext))
      actx=new (window.AudioContext||window.webkitAudioContext)();
    if(actx && actx.state==='suspended') actx.resume();
  }}catch(e){{}}
}}
function beep(freq,dur,times){{
  if(!actx) return;
  for(var i=0;i<times;i++){{
    var t=actx.currentTime + i*(dur+0.12);
    var o=actx.createOscillator(), g=actx.createGain();
    o.type='sine'; o.frequency.value=freq;
    g.gain.setValueAtTime(0.0001,t);
    g.gain.exponentialRampToValueAtTime(0.5,t+0.02);
    g.gain.exponentialRampToValueAtTime(0.0001,t+dur);
    o.connect(g); g.connect(actx.destination);
    o.start(t); o.stop(t+dur+0.05);
  }}
}}
function vibrate(p){{ try{{ if(navigator.vibrate) navigator.vibrate(p); }}catch(e){{}} }}

/* wake lock */
var wl=null;
function toggleWake(){{
  var btn=document.getElementById('wakeBtn');
  if(wl){{ try{{wl.release();}}catch(e){{}} wl=null;
    btn.classList.remove('on'); btn.textContent='☀︎ Keep screen on'; return; }}
  if(!navigator.wakeLock){{ btn.textContent='☀︎ Not supported';
    setTimeout(function(){{btn.textContent='☀︎ Keep screen on';}},2000); return; }}
  navigator.wakeLock.request('screen').then(function(s){{
    wl=s; btn.classList.add('on'); btn.textContent='☀︎ Screen staying on';
    s.addEventListener('release',function(){{ wl=null; btn.classList.remove('on');
      btn.textContent='☀︎ Keep screen on'; }});
  }}).catch(function(){{ btn.textContent='☀︎ Not supported';
    setTimeout(function(){{btn.textContent='☀︎ Keep screen on';}},2000); }});
}}

/* offline support */
if('serviceWorker' in navigator){{window.addEventListener('load',function(){{
  navigator.serviceWorker.register('sw.js').catch(function(){{}});}});}}

/* add a playlist */
function addPlaylist(){{
  var inp=document.getElementById('plUrl'), url=inp.value.trim();
  if(!/^https:\\/\\/open\\.spotify\\.com\\//.test(url)){{
    inp.style.borderColor='var(--red)';
    setTimeout(function(){{inp.style.borderColor='';}},1200); return;
  }}
  var a=document.createElement('a');
  a.className='music-link'; a.href=url; a.target='_blank'; a.rel='noopener';
  a.innerHTML='<span class="ml-ico">⭐</span><span>My playlist<small>'+
    url.replace('https://open.spotify.com/','').slice(0,40)+'</small></span>';
  document.getElementById('musicLinks').appendChild(a);
  inp.value='';
}}
</script>
</body>
</html>
"""

os.makedirs(os.path.dirname(_OUT), exist_ok=True)
open(_OUT, "w", encoding="utf-8", newline="\n").write(DOC)

# Auto-versioned service worker (cache name = hash of the page) so installed
# apps always pick up new content without a manual CACHE bump. See DEVELOPMENT.md.
import hashlib
_ver = hashlib.sha1(DOC.encode("utf-8")).hexdigest()[:10]
SW = ("const CACHE='workout-%s';\n"
      "const ASSETS=['./','./index.html','./manifest.webmanifest','./icon-180.png','./icon-192.png','./icon-512.png'];\n"
      "self.addEventListener('install',e=>{self.skipWaiting();"
      "e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).catch(()=>{}));});\n"
      "self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all("
      "ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});\n"
      "self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;"
      "e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(res=>{"
      "const copy=res.clone();caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{});"
      "return res;}).catch(()=>caches.match('./index.html'))));});\n") % _ver
open(os.path.join(os.path.dirname(_OUT), "sw.js"), "w", encoding="utf-8", newline="\n").write(SW)

print("written", len(DOC), "bytes | cache: workout-" + _ver)
