// Run the answer engine of assets/ask/ask.js in Node for tools/check_ask.py.
// Reads {D, B, cases: [[question, slots], ...]} on stdin; writes the answers as JSON on stdout.
const fs = require('fs');
const path = require('path');
const E = require(path.join(__dirname, '..', 'assets', 'ask', 'ask.js'));
const inp = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = inp.cases.map(([q, s]) => {
  const o = E.answer(inp.D, inp.B, q, s);
  if (!o) return null;
  return { title: o.title, slots: o.slots, ok: o.ok, say: o.say, nums: o.nums, table: o.table, points: o.points, src: o.src,
    link: o.link, cav: o.cav, note: o.note, chart: o.chart && { type: o.chart.type, title: o.chart.title } };
});
process.stdout.write(JSON.stringify(out));
