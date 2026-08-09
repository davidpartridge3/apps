// Capture screenshots of the kitchen planner for review. Server on :8123.
import { chromium } from 'playwright';
import { mkdirSync } from 'fs';
const BASE = 'http://localhost:8123';
const OUT = process.env.OUT || 'shots';
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 2, colorScheme: 'dark', isMobile: true, hasTouch: true,
});
const p = await ctx.newPage();
const shot = (name) => p.screenshot({ path: `${OUT}/${name}.png` });

// 1. Home week with the new "Plan this week" button
await p.goto(BASE + '/kitchen/index.html', { waitUntil: 'networkidle' });
await p.waitForTimeout(300);
await shot('1-week');

// 2. Planner picker
await p.evaluate(() => document.querySelector('.plan-btn.open-planner').click());
await p.waitForTimeout(300);
await shot('2-picker');

// 3. Picker with meals selected -> assign days
await p.evaluate(() => {
  const rows = [...document.querySelectorAll('#plBody .pl-rc')];
  let d = 0, b = false;
  for (const row of rows) {
    if (d >= 3 && b) break;
    const batch = row.querySelector('.pl-rc-slot').classList.contains('batch');
    if (batch && !b) { b = true; row.click(); }
    else if (!batch && d < 3) { d++; row.click(); }
  }
  document.getElementById('plNext').click();
});
await p.waitForTimeout(300);
await shot('3-assign-days');

// 4. Share step
await p.evaluate(() => document.getElementById('plNext').click());
await p.waitForTimeout(300);
await shot('4-share');

// 5. Plan panel loaded from a link, with Laurel's votes (fresh load so boot runs)
await p.goto(BASE + '/kitchen/index.html#plan=w1r0.mon,w1r1.tue,w1r2.thu,w1r3.sun&votes=w1r0.u,w1r1.d,w1r3.u', { waitUntil: 'networkidle' });
await p.reload({ waitUntil: 'networkidle' });
await p.waitForTimeout(400);
await shot('5-plan-with-votes');

// 6. Combined shopping list
await p.evaluate(() => document.getElementById('ppShop').click());
await p.waitForTimeout(300);
await shot('6-combined-list');

await browser.close();
console.log('shots written to', OUT);
