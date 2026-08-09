// Prime-directive verification: both apps must work with JavaScript OFF and ON.
// Usage: node test/verify.mjs   (expects the static server on http://localhost:8123)
import { chromium } from 'playwright';

const BASE = process.env.BASE || 'http://localhost:8123';
let failures = 0;
const ok = (c, m) => { console.log(`${c ? '  ✅' : '  ❌'} ${m}`); if (!c) failures++; };

async function page(browser, jsEnabled, hash = '') {
  const ctx = await browser.newContext({ javaScriptEnabled: jsEnabled });
  const p = await ctx.newPage();
  const errors = [];
  p.on('pageerror', e => errors.push(String(e)));
  p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await p.goto(BASE + hash, { waitUntil: 'networkidle' });
  return { ctx, p, errors };
}

async function run() {
  const browser = await chromium.launch();

  // ---------- KITCHEN, JS OFF ----------
  console.log('\nKITCHEN — JavaScript OFF (prime directive)');
  {
    const { ctx, p, errors } = await page(browser, false, '/kitchen/index.html');
    ok((await p.locator('body').getAttribute('class'))?.includes('no-js'), 'body stays .no-js');
    ok(await p.locator('.wkpanel .card').first().isVisible(), 'week 1 recipe cards render');
    ok(!(await p.locator('.plan-btn.open-planner').first().isVisible()), 'planner entry button hidden (.js-only)');
    ok(!(await p.locator('#planner').isVisible()), 'planner overlay hidden');
    // a recipe detail sheet is reachable via CSS radios (no JS)
    ok(await p.locator('#sv w1r0'.replace(' ', '')).count() === 1, 'recipe sheet exists in DOM');
    ok(errors.length === 0, `no page errors (${errors.length})`);
    await ctx.close();
  }

  // ---------- KITCHEN, JS OFF, with a #plan hash (must fall back gracefully) ----------
  console.log('\nKITCHEN — JavaScript OFF + #plan hash (must fall back to fixed week)');
  {
    const { ctx, p, errors } = await page(browser, false, '/kitchen/index.html#plan=w1r0.mon,w1r1.tue');
    ok(await p.locator('.wkpanel .card').first().isVisible(), 'normal week still renders (no blank page)');
    ok(await p.locator('#planPanel').count() === 0, 'no JS-built plan panel injected');
    ok(errors.length === 0, `no page errors (${errors.length})`);
    await ctx.close();
  }

  // ---------- KITCHEN, JS ON ----------
  console.log('\nKITCHEN — JavaScript ON');
  {
    const { ctx, p, errors } = await page(browser, true, '/kitchen/index.html');
    await p.evaluate(() => document.querySelector('.plan-btn.open-planner').click());
    ok(await p.locator('#planner').isVisible(), 'planner overlay opens');
    ok(await p.locator('#plBody .pl-rc').count() === 96, 'picker lists all 96 recipes');
    await ctx.close();
  }

  // ---------- KITCHEN, JS ON, plan hash renders panel ----------
  console.log('\nKITCHEN — JavaScript ON + #plan hash');
  {
    const { ctx, p, errors } = await page(browser, true, '/kitchen/index.html#plan=w1r0.mon,w1r1.tue,w1r2.thu,w1r3.sun&votes=w1r0.u,w1r1.d');
    ok(await p.locator('#planPanel').isVisible(), 'plan panel renders from hash');
    ok(await p.locator('.pp-card').count() === 4, 'four planned meals shown');
    ok((await p.locator('.pp-badge').allTextContents()).join('') === '👍👎', 'vote badges render (👍👎)');
    ok(errors.length === 0, `no page errors (${errors.length})`);
    await ctx.close();
  }

  // ---------- WORKOUT, JS OFF ----------
  console.log('\nWORKOUT — JavaScript OFF');
  {
    const { ctx, p, errors } = await page(browser, false, '/workout/index.html');
    ok((await p.locator('body').getAttribute('class'))?.includes('no-js'), 'body stays .no-js');
    ok(await p.locator('.panel .ex-card').first().isVisible(), 'exercise cards render');
    ok(errors.length === 0, `no page errors (${errors.length})`);
    await ctx.close();
  }

  // ---------- WORKOUT, JS ON ----------
  console.log('\nWORKOUT — JavaScript ON');
  {
    const { ctx, p, errors } = await page(browser, true, '/workout/index.html');
    ok(errors.length === 0, `no page errors (${errors.length})`);
    await ctx.close();
  }

  await browser.close();
  console.log(`\n${failures === 0 ? '✅ ALL CHECKS PASSED' : `❌ ${failures} CHECK(S) FAILED`}`);
  process.exit(failures === 0 ? 0 : 1);
}
run().catch(e => { console.error(e); process.exit(1); });
