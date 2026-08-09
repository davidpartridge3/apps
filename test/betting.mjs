// Verify the betting tool's MATH against hand-computed values. The results are
// what matter here, not the UI. Drives the app's real global functions.
import { chromium } from 'playwright';
const BASE = process.env.BASE || 'http://localhost:8123';
let fails=0;
const approx=(a,b,eps=1e-4)=>a!=null&&Math.abs(a-b)<=eps;
const check=(name,got,exp,eps)=>{ const ok=(typeof exp==='number')?approx(got,exp,eps??1e-4):got===exp;
  console.log(`  ${ok?'✅':'❌'} ${name}  → got ${got}${ok?'':`  (expected ${exp})`}`); if(!ok)fails++; };

const br=await chromium.launch();
const p=await (await br.newContext()).newPage();
p.on('pageerror',e=>{console.log('  ❌ pageerror',e); fails++;});
await p.goto(BASE+'/betting/index.html',{waitUntil:'networkidle'});

console.log('\nAmerican → decimal odds');
check('+150', await p.evaluate(()=>amToDec(150)), 2.5);
check('-110', await p.evaluate(()=>amToDec(-110)), 1.9090909, 1e-5);
check('-200', await p.evaluate(()=>amToDec(-200)), 1.5);
check('+100', await p.evaluate(()=>amToDec(100)), 2.0);

console.log('\ndecimal → American (round-trip)');
check('2.5 → +150', await p.evaluate(()=>decToAm(2.5)), '+150');
check('1.5 → -200', await p.evaluate(()=>decToAm(1.5)), '-200');

console.log('\nNo-vig devig');
let d = await p.evaluate(()=>devig(-110,-110));
check('-110/-110 fair A', d.a, 0.5);
check('-110/-110 vig',   d.vig, 0.047619, 1e-5);           // 4.76%
d = await p.evaluate(()=>devig(150,-170));
// imp: 0.4 and 0.629629...; over 1.029629; fairA=0.388489
check('+150/-170 fair A', d.a, 0.388489, 1e-4);
check('+150/-170 fair B', d.b, 0.611510, 1e-4);

console.log('\nExpected value (per $1 stake)');
// your +145 (dec 2.45), fair p 0.425 -> EV = 0.425*2.45 - 1
check('EV +145 @ p=0.425', await p.evaluate(()=>0.425*amToDec(145)-1), 0.04125, 1e-4);
// negative-edge case: -110 (dec 1.9091) at p=0.5 -> 0.5*1.9091-1 = -0.04545
check('EV -110 @ p=0.50', await p.evaluate(()=>0.5*amToDec(-110)-1), -0.045454, 1e-4);

console.log('\nKelly fraction (full)');
// b=1.45,p=0.425,q=0.575 -> (1.45*0.425-0.575)/1.45 = 0.028448
check('full Kelly +145 @0.425', await p.evaluate(()=>kellyFraction(amToDec(145),0.425)), 0.028448, 1e-5);
// no edge -> negative kelly
check('Kelly -110 @0.50 (neg)', await p.evaluate(()=>kellyFraction(amToDec(-110),0.5))<0, true);

console.log('\nClosing-line value (betCLV)');
// took +150 (imp .4), closed +120 (dec 2.2, imp .45454) -> (.45454-.4)/.4 = +0.13636
check('CLV took+150 close+120', await p.evaluate(()=>betCLV({odds:150,close:120,closeOpp:null})), 0.136363, 1e-4);
// took -110 close -130 (worse for you: line moved against) -> imp .5652 vs .5238 -> +0.0791? 
// imp taken 0.52381, close -130 dec 1.7692 imp 0.56522 -> (0.56522-0.52381)/0.52381 = +0.0791 (you beat close: you got -110 vs it closing -130)
check('CLV took-110 close-130', await p.evaluate(()=>betCLV({odds:-110,close:-130,closeOpp:null})), 0.079070, 1e-4);
// devigged close: close +120 / opp -140 -> devig fairA then CLV
check('CLV with devig close', await p.evaluate(()=>{
  const dv=devig(120,-140); const pTaken=1/amToDec(150); return (dv.a-pTaken)/pTaken;
}), await p.evaluate(()=>betCLV({odds:150,close:120,closeOpp:-140})), 1e-9);
check('no close → null', await p.evaluate(()=>betCLV({odds:150,close:null})), null);

console.log('\nProfit settlement (betProfit)');
check('won +150 stake100', await p.evaluate(()=>betProfit({result:'won',odds:150,stake:100})), 150);
check('lost stake100',     await p.evaluate(()=>betProfit({result:'lost',odds:150,stake:100})), -100);
check('push stake100',     await p.evaluate(()=>betProfit({result:'push',odds:150,stake:100})), 0);
check('pending stake100',  await p.evaluate(()=>betProfit({result:'pending',odds:150,stake:100})), 0);
check('won -110 stake110', await p.evaluate(()=>betProfit({result:'won',odds:-110,stake:110})), 100, 1e-6);

console.log(`\n${fails===0?'✅ ALL BETTING MATH CORRECT':'❌ '+fails+' MATH CHECK(S) FAILED'}`);
await br.close();
process.exit(fails?1:0);
