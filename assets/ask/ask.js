/* Ask the data: answers to the questions on /ask/, computed in the browser from /assets/ask/data.json.

   No language model, no server and no request outside this site. Every number is a lookup, sum, rank or
   ratio of the derived figures in data.json, which tools/build_ask.py builds from the validated IRA panel.

   ENGINE has no DOM code. tools/check_ask.py runs it in Node and compares every answer with
   tools/ask_answers.py, its Python twin, so a change to one must be made to the other.

   The charts copy the markup of tools/viz.py (figure, key, table, nice_ticks, columns, dotrows, split) and of
   bars() in tools/build.py, using only classes from assets/viz.css and assets/site.css. tools/check_ask.py
   fails if a class written here is missing from those files. */
(function () {
  'use strict';

  var MP = 'Motor Private', MC = 'Motor Commercial';
  var PILLARS = ['Balance sheet', 'Operating performance', 'Business profile', 'Return quality'];
  var FLAGS = {
    negative_equity: 'negative equity', below_capital_floor: "equity under IRA's minimum capital",
    combined_ratio_above_110: 'combined ratio above 110%', three_underwriting_losses: 'an underwriting loss in each of the last three years',
    unreliable_return: 'an unreliable return in the last three years', low_retention: 'retention under 25%'
  };
  var MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ');
  var SRC = {
    cls: 'IRA quarterly returns, full years (Q4 year to date), net of reinsurance. Insurers only, micro insurers included; Motor Commercial includes PSV.',
    tot: 'IRA quarterly returns, full years (Q4 year to date). Insurers only, micro insurers included.',
    sc: "Kenya Cedant Scorecard, built from IRA's quarterly returns. Grades are relative screening measures, not credit ratings.",
    tri: 'NAIC Schedule P paid triangles for all US insurers, accident years 1988 to 1997 (CAS Loss Reserving Database). Volume-weighted chain ladder.'
  };
  var LINK = {
    lossmap: ['/ira-kenya-insurance/page/kenya-insurance-loss-map.html', 'Open the Loss Map'],
    structure: ['/ira-kenya-insurance/page/kenya-insurance-market-structure.html', 'Open Market Structure'],
    scorecard: ['/ira-kenya-reinsurance/page/kenya-cedant-scorecard.html', 'Open the Cedant Scorecard'],
    explorer: ['/ira-kenya-data/explorer/kenya-insurer-explorer.html', 'Open the Insurer Explorer'],
    series: ['/kenya-insurance/', 'Read the Kenya series'],
    tri: ['/#tri-h', 'See the triangle worked out on the home page'],
    ifrs: ['/work/ifrs17-measurement/', 'Read the IFRS 17 case study']
  };

  /* ---------------------------------------------------------------- formatting (as tools/ask_answers.py) */
  function rhu(a, dp) { return Math.floor(a * Math.pow(10, dp) + 0.5); }
  function group3(s) { return s.replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function fix(v, dp, signed) {
    var p = Math.pow(10, dp), r = rhu(Math.abs(v), dp), ip = Math.floor(r / p), fp = r - ip * p;
    var s = group3(String(ip)) + (dp ? '.' + ('0000' + fp).slice(-dp) : '');
    return (r === 0 ? '' : v < 0 ? '-' : signed ? '+' : '') + s;
  }
  function money(k, signed) {
    var a = Math.abs(k);
    if (a >= 1e6) return 'KSh ' + fix(k / 1e6, 1, signed) + 'bn';
    if (a >= 1e4) return 'KSh ' + fix(k / 1e3, 0, signed) + 'm';
    return 'KSh ' + fix(k / 1e3, 1, signed) + 'm';
  }
  function usd(k) { return Math.abs(k) >= 1e6 ? 'US$' + fix(k / 1e6, 2) + 'bn' : 'US$' + fix(k / 1e3, 1) + 'm'; }
  function pct(r, signed) {
    if (r === null) return 'n/a';
    if (r > 0 && r < 0.0005) return 'under 0.1%';   // would print as 0.0%
    return fix(r * 100, 1, signed) + '%';
  }
  function ordinal(n) {
    var t = n % 100, u = n % 10;
    return n + (t > 10 && t < 14 ? 'th' : u === 1 ? 'st' : u === 2 ? 'nd' : u === 3 ? 'rd' : 'th');
  }
  function span(ys, all) {   // [2018, 2019, 2020, 2023] -> "2018 to 2020, 2023", runs of neighbours in the list all
    var out = [], i = 0;
    while (i < ys.length) {
      var j = i;
      while (j + 1 < ys.length && all.indexOf(ys[j + 1]) === all.indexOf(ys[j]) + 1) j++;
      out.push(j > i ? ys[i] + ' to ' + ys[j] : String(ys[i]));
      i = j + 1;
    }
    return out.join(', ');
  }
  function slug(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''); }
  function sum(xs) { var v = 0; for (var i = 0; i < xs.length; i++) v += xs[i]; return v; }
  function argmax(xs) { var b = 0; for (var i = 1; i < xs.length; i++) if (xs[i] > xs[b]) b = i; return b; }
  function argmin(xs) { var b = 0; for (var i = 1; i < xs.length; i++) if (xs[i] < xs[b]) b = i; return b; }

  /* ---------------------------------------------------------------- the data */
  function ctx(D) {
    if (D._ctx) return D._ctx;
    var c = { byId: {} }, sy = {};
    D.ins.forEach(function (x) { c.byId[x.id] = x; });
    Object.keys(D.sc).forEach(function (id) { Object.keys(D.sc[id]).forEach(function (y) { sy[y] = 1; }); });
    c.scyears = Object.keys(sy).map(Number).sort(function (a, b) { return a - b; });
    c.gyears = D.years.filter(function (y, i) { return i > 0 && D.years[i - 1] === y - 1; });
    c.sorted = D.ins.slice().sort(function (a, b) { var x = a.s.toLowerCase(), z = b.s.toLowerCase(); return x < z ? -1 : x > z ? 1 : 0; });
    Object.defineProperty(D, '_ctx', { value: c });
    return c;
  }
  function tot(D, id, y) { var t = D.tot[id]; return (t && t[y]) || null; }
  function cls(D, id, y, ci) { var t = D.cls[id], e = t && t[y]; return (e && e[ci]) || null; }
  function active(D, id, y) { var e = tot(D, id, y); return !!e && e.some(function (v) { return v !== 0; }); }
  function sn(D, id) { return ctx(D).byId[id].s; }
  function cr(e) { return e[1] > 0 ? (e[2] + e[3]) / e[1] : null; }
  function totSum(D, y, f) { var v = 0; D.ins.forEach(function (x) { var e = tot(D, x.id, y); if (e) v += e[f]; }); return v; }
  function clsSum(D, ys, ci, f) {
    var v = 0;
    D.ins.forEach(function (x) { ys.forEach(function (y) { var e = cls(D, x.id, y, ci); if (e) v += e[f]; }); });
    return v;
  }
  function missing(D, id, y) {
    var s = sn(D, id);
    if ((D.nf[id] || []).indexOf(+y) > -1) return s + ' filed no Q4 return for ' + y + ', so there is no full-year figure.';
    if (!tot(D, id, y)) return s + " does not appear in IRA's returns for " + y + '.';
    if (!active(D, id, y)) return s + ' reported no business in ' + y + '.';
    return null;
  }
  function has(D, id) {
    var ys = D.years.filter(function (y) { return active(D, id, String(y)); });
    return ys.length ? 'It has full-year figures for ' + span(ys, D.years) + '.' : 'It has no full-year figures in this data.';
  }
  // Mergers, as ira-kenya-insurance counts them (D.mg: absorbed company -> the company it merged into).
  function mergedYear(D, a) {   // the first full year after the absorbed company's last one
    var ys = D.years.filter(function (y) { return active(D, a, String(y)); }), i = D.years.indexOf(ys[ys.length - 1]);
    return i + 1 < D.years.length ? D.years[i + 1] : D.years[i] + 1;
  }
  function mergerNote(D, id) {
    var into = Object.keys(D.mg).filter(function (a) { return D.mg[a] === id; });
    if (D.mg[id]) return sn(D, id) + ' merged into ' + sn(D, D.mg[id]) + ' in ' + mergedYear(D, id) + '.';
    if (!into.length) return '';
    return 'Figures are as filed. ' + into.map(function (a) { return sn(D, a) + ' merged into it in ' + mergedYear(D, a); }).join(' and ')
      + ', so its figures include that business from then on.';
  }
  function proForma(D, id, y) {   // written premium with the companies merged into it added
    var v = 0, e = tot(D, id, y);
    if (e && e[0] > 0) v += e[0];
    Object.keys(D.mg).forEach(function (a) { if (D.mg[a] === id) { var f = tot(D, a, y); if (f && f[0] > 0) v += f[0]; } });
    return v;
  }
  function largest(D) {
    var y = String(D.years[D.years.length - 1]), best = null, bv = 0;
    D.ins.forEach(function (x) { var e = tot(D, x.id, y); if (e && (best === null || e[0] > bv)) { best = x.id; bv = e[0]; } });
    return best;
  }

  /* ---------------------------------------------------------------- slots */
  function question(B, q) { for (var i = 0; i < B.questions.length; i++) if (B.questions[i].id === q) return B.questions[i]; return null; }
  function choices(D, B, kind) {
    var c = ctx(D), ys = function (l) { return l.map(function (y) { return [String(y), String(y)]; }); };
    if (kind === 'years') return ys(D.years);
    if (kind === 'cyears') return ys(D.cyears);
    if (kind === 'scyears') return ys(c.scyears);
    if (kind === 'gyears') return ys(c.gyears);
    if (kind === 'ins') return c.sorted.map(function (x) { return [x.id, x.s]; });
    if (kind === 'cls') return D.classes.map(function (n) { return [slug(n), n]; });
    if (kind === 'line') return D.tri.map(function (t) { return [slug(t[0]), t[0]]; });
    if (kind === 'topic') return B.topics.map(function (t) { return [t[0], t[1]]; });
    return [];
  }
  function defaults(D, B, q) {
    var Q = question(B, q), s = {};
    Object.keys(Q.slots).forEach(function (k) {
      var kind = Q.slots[k], ch = choices(D, B, kind);
      if (kind === 'ins') s[k] = largest(D);
      else if (kind === 'cls') s[k] = slug(MP);
      else if (kind === 'line' || kind === 'topic' || k === 'y1') s[k] = ch[0][0];
      else s[k] = ch[ch.length - 1][0];
    });
    return s;
  }
  function normalize(D, B, q, s) {
    var Q = question(B, q), d = defaults(D, B, q), out = {};
    Object.keys(Q.slots).forEach(function (k) {
      var ok = choices(D, B, Q.slots[k]).some(function (c) { return c[0] === String(s[k]); });
      out[k] = ok ? String(s[k]) : d[k];
    });
    if (out.y1 && out.y2 && +out.y1 > +out.y2) { var t = out.y1; out.y1 = out.y2; out.y2 = t; }
    return out;
  }
  function label(D, B, kind, v) {
    var ch = choices(D, B, kind);
    for (var i = 0; i < ch.length; i++) if (ch[i][0] === v) return ch[i][1];
    return v;
  }
  function title(D, B, q, s) {
    var Q = question(B, q);
    return Q.t.replace(/\{(\w+)\}/g, function (m, k) { return label(D, B, Q.slots[k], s[k]); });
  }

  /* ---------------------------------------------------------------- the answers */
  var A = {};

  A['class-range'] = function (D, B, s, o) {
    var y1 = +s.y1, y2 = +s.y2, ys = D.cyears.filter(function (y) { return y >= y1 && y <= y2; }).map(String);
    var res = D.classes.map(function (c, i) { return clsSum(D, ys, String(i), 3); });
    var lo = argmin(res), hi = argmax(res), total = sum(res), when = y1 === y2 ? String(y1) : y1 + ' to ' + y2;
    o.say.push((y1 === y2 ? 'In ' + y1 : 'From ' + y1 + ' to ' + y2) + ', ' + D.classes[lo] + ' lost the most: an underwriting result of ' + money(res[lo], true) + '.');
    o.say.push(res[hi] > 0 ? D.classes[hi] + ' made the most: ' + money(res[hi], true) + '.'
      : 'No class made an underwriting profit; the smallest loss was ' + D.classes[hi] + ', at ' + money(res[hi], true) + '.');
    o.say.push('All ' + D.classes.length + ' classes together: ' + money(total, true) + '.');
    o.nums = [['worst', D.classes[lo], money(res[lo], true)], ['best', D.classes[hi], money(res[hi], true)], ['total', 'All classes', money(total, true)]];
    var order = res.map(function (v, i) { return i; }).sort(function (a, b) { return res[a] - res[b] || a - b; });
    o.chart = { type: 'bars', title: 'Underwriting result by class, ' + when + ', KSh bn', items: order.map(function (i) { return [D.classes[i], res[i] / 1e6]; }) };
    o.table = { head: ['Class', 'Underwriting result'], rows: order.map(function (i) { return [D.classes[i], money(res[i], true)]; }) };
    o.src = SRC.cls; o.link = [LINK.lossmap];
  };

  A['uw-inv'] = function (D, B, s, o) {
    var y = s.yr, uw = totSum(D, y, 4), inv = totSum(D, y, 5), op = uw + inv;
    o.say.push('In ' + y + ' insurers ' + (uw < 0 ? 'lost ' + money(-uw) : 'made ' + money(uw)) + ' on underwriting and '
      + (inv < 0 ? 'lost ' + money(-inv) + ' on' : 'earned ' + money(inv) + ' from') + ' investments.');
    o.say.push(uw < 0 && op > 0 ? 'Investment income covered the underwriting loss, leaving an operating result of ' + money(op, true) + '.'
      : uw < 0 ? 'Investment income did not cover the underwriting loss: the operating result was ' + money(op, true) + '.'
      : 'The operating result was ' + money(op, true) + '.');
    o.nums = [['uw', 'Underwriting result', money(uw, true)], ['inv', 'Investment income', money(inv)], ['op', 'Operating result', money(op, true)]];
    var ys = D.years.map(String), U = ys.map(function (z) { return totSum(D, z, 4); }), I = ys.map(function (z) { return totSum(D, z, 5); });
    o.chart = { type: 'columns', title: 'Underwriting result and investment income, KSh bn', cats: ys, unit: 'bn',
      series: [['sign', 'Underwriting result', U.map(function (v) { return v / 1e6; })], ['neu', 'Investment income', I.map(function (v) { return v / 1e6; })]],
      key: [['pos', 'Underwriting profit'], ['neg', 'Underwriting loss'], ['neu', 'Investment income']] };
    o.table = { head: ['Year', 'Underwriting result', 'Investment income', 'Operating result'],
      rows: ys.map(function (z, i) { return [z, money(U[i], true), money(I[i]), money(U[i] + I[i], true)]; }) };
    o.src = SRC.tot; o.link = [LINK.series, LINK.explorer];
  };

  function filed(D, y) { var u = []; D.ins.forEach(function (x) { var e = tot(D, x.id, y); if (e && e[4] !== 0) u.push(e[4]); }); return u; }
  A['profit-count'] = function (D, B, s, o) {
    var y = s.yr, u = filed(D, y), n = u.length, p = u.filter(function (v) { return v > 0; }).length;
    o.say.push('In ' + y + ', ' + p + ' of the ' + n + ' insurers that filed a full year made an underwriting profit.');
    if (n - p > 0) o.say.push('The other ' + (n - p) + ' made a loss.');
    o.nums = [['profit', 'Made a profit', String(p)], ['filed', 'Filed a full year', String(n)], ['share', 'Share in profit', pct(n ? p / n : null)]];
    var ys = D.years.map(String), P = [], N = [];
    ys.forEach(function (z) { var v = filed(D, z); N.push(v.length); P.push(v.filter(function (w) { return w > 0; }).length); });
    o.chart = { type: 'columns', title: 'Insurers with an underwriting profit', cats: ys, unit: 'n',
      series: [['pos', 'Made an underwriting profit', P], ['ctx', 'Filed a full year', N]],
      key: [['pos', 'Made an underwriting profit'], ['ctx', 'Filed a full year']] };
    o.table = { head: ['Year', 'Made a profit', 'Filed a full year'], rows: ys.map(function (z, i) { return [z, String(P[i]), String(N[i])]; }) };
    o.src = SRC.tot; o.link = [LINK.explorer];
  };

  function conc(D, y) {
    var w = [];
    D.ins.forEach(function (x) { var e = tot(D, x.id, y); if (e && e[0] > 0) w.push(e[0]); });
    var t = sum(w), big = w.filter(function (v) { return v >= 1e7; }), top = w.slice().sort(function (a, b) { return b - a; }).slice(0, 5), h = 0;
    w.forEach(function (v) { var q = v / t; h += q * q; });
    return { n: w.length, t: t, nb: big.length, bs: sum(big) / t, top5: sum(top) / t, hhi: h * 1e4 };
  }
  A.concentration = function (D, B, s, o) {
    var y = s.yr, c = conc(D, y);
    o.say.push(c.nb === 0 ? 'In ' + y + ', no insurer wrote KSh 10bn or more; the market wrote ' + money(c.t) + '.'
      : 'In ' + y + ', ' + c.nb + ' of the ' + c.n + ' insurers that wrote premium wrote KSh 10bn or more, and '
        + (c.nb === 1 ? 'it held ' : 'together they held ') + pct(c.bs) + " of the market's " + money(c.t) + '.');
    o.say.push('The five largest held ' + pct(c.top5) + ', and the Herfindahl index was ' + fix(c.hhi, 0) + '.');
    o.nums = [['nb', 'Insurers at KSh 10bn or more', String(c.nb)], ['bs', 'Their share', pct(c.bs)], ['top5', 'Five largest', pct(c.top5)],
      ['hhi', 'Herfindahl index', fix(c.hhi, 0)], ['total', 'Written premium', money(c.t)]];
    var ys = D.years.map(String), C = ys.map(function (z) { return conc(D, z); });
    o.chart = { type: 'columns', title: 'Share of written premium held by insurers writing KSh 10bn or more', cats: ys, unit: 'pct',
      series: [['neu', 'Share held', C.map(function (k) { return k.bs * 100; })]] };
    o.table = { head: ['Year', 'Insurers at KSh 10bn or more', 'Their share', 'Five largest', 'Herfindahl index', 'Written premium'],
      rows: ys.map(function (z, i) { var k = C[i]; return [z, String(k.nb), pct(k.bs), pct(k.top5), fix(k.hhi, 0), money(k.t)]; }) };
    o.src = SRC.tot; o.link = [LINK.structure];
  };

  A['motor-lr'] = function (D, B, s, o) {
    var ks = [String(D.classes.indexOf(MP)), String(D.classes.indexOf(MC))], ys = D.cyears.map(String), L = [], E = [], Cl = [];
    ys.forEach(function (y) {
      var c = 0, e = 0;
      D.ins.forEach(function (x) { ks.forEach(function (k) { var f = cls(D, x.id, y, k); if (f) { c += f[2]; e += f[1]; } }); });
      Cl.push(c); E.push(e); L.push(e > 0 ? c / e : null);
    });
    var n = ys.length - 1, lo = argmin(L), hi = argmax(L);
    o.say.push("Motor's loss ratio, private and commercial together, was " + pct(L[n]) + ' in ' + ys[n] + '.');
    o.say.push('From ' + ys[0] + ' to ' + ys[n] + ' it ran from ' + pct(L[lo]) + ' in ' + ys[lo] + ' to ' + pct(L[hi]) + ' in ' + ys[hi] + '.');
    o.nums = [['last', ys[n], pct(L[n])], ['low', 'Lowest, ' + ys[lo], pct(L[lo])], ['high', 'Highest, ' + ys[hi], pct(L[hi])]];
    o.chart = { type: 'columns', title: 'Motor loss ratio, private and commercial together', cats: ys, unit: 'pct',
      series: [['neu', 'Loss ratio', L.map(function (v) { return v === null ? null : v * 100; })]] };
    o.table = { head: ['Year', 'Loss ratio', 'Net earned premium', 'Incurred claims'], rows: ys.map(function (y, i) { return [y, pct(L[i]), money(E[i]), money(Cl[i])]; }) };
    o.src = SRC.cls; o.link = [LINK.lossmap];
  };

  function scale(vals) {   // KSh bn when any value reaches a billion, else KSh m
    var big = vals.some(function (v) { return v !== null && Math.abs(v) >= 1e6; });
    return big ? ['bn', 1e6] : ['m', 1e3];
  }

  A['ins-class-year'] = function (D, B, s, o) {
    var id = s.ins, y = s.yr, ci = String(D.classes.map(slug).indexOf(s.cls)), C = D.classes[+ci], S = sn(D, id);
    o.cav = true; o.link = [LINK.explorer, LINK.lossmap]; o.src = SRC.cls;
    var miss = missing(D, id, y);
    if (miss) { o.ok = false; o.say.push(miss, has(D, id)); return; }
    var e = cls(D, id, y, ci);
    if (!e) {
      o.ok = false;
      o.say.push(S + ' reported no ' + C + ' business in ' + y + '.');
      var g = D.classes.map(function (c, i) { var f = cls(D, id, y, String(i)); return f ? f[0] : 0; }), b = argmax(g);
      if (g[b] > 0) o.say.push('Its largest class that year was ' + D.classes[b] + ', with ' + money(g[b]) + ' of gross premium.');
      return;
    }
    var gp = e[0], lr = e[1] > 0 ? e[2] / e[1] : null, n = 0, above = 0, tie = 0, mc = 0, me = 0;
    D.ins.forEach(function (x) {
      var f = cls(D, x.id, y, ci);
      if (!f) return;
      mc += f[2]; me += f[1];
      if (f[0] > 0) { n++; if (f[0] > gp) above++; else if (f[0] === gp && x.id !== id) tie++; }
    });
    var rank = gp > 0 ? above + 1 : null, mlr = me > 0 ? mc / me : null;
    o.say.push('In ' + y + ' ' + S + ' wrote ' + money(gp) + ' of ' + C + ' gross premium'
      + (rank ? ', ' + (tie ? 'joint ' : '') + ordinal(rank) + ' of the ' + n + ' insurers writing the class.' : '.'));
    o.say.push(lr !== null ? 'Its loss ratio was ' + pct(lr) + ', against ' + pct(mlr) + ' for the market, and its underwriting result was ' + money(e[3], true) + '.'
      : 'It had no positive net earned premium in the class, so it has no loss ratio; its underwriting result was ' + money(e[3], true) + '.');
    o.nums = [['gp', 'Gross premium', money(gp)], ['lr', 'Loss ratio', pct(lr)], ['uw', 'Underwriting result', money(e[3], true)],
      ['rank', 'Rank in the class', rank ? (tie ? 'joint ' : '') + rank + ' of ' + n : 'n/a'], ['mlr', 'Market loss ratio', pct(mlr)]];
    var ys = D.cyears.map(String), U = ys.map(function (z) { var f = cls(D, id, z, ci); return f ? f[3] : null; }), sc = scale(U);
    o.chart = { type: 'columns', title: S + ', ' + C + ': underwriting result, KSh ' + sc[0], cats: ys, unit: sc[0],
      series: [['sign', 'Underwriting result', U.map(function (v) { return v === null ? null : v / sc[1]; })]],
      key: [['pos', 'Profit'], ['neg', 'Loss']] };
    o.table = { head: ['Year', 'Gross premium', 'Loss ratio', 'Underwriting result'], rows: [] };
    ys.forEach(function (z) { var f = cls(D, id, z, ci); if (f) o.table.rows.push([z, money(f[0]), pct(f[1] > 0 ? f[2] / f[1] : null), money(f[3], true)]); });
  };

  A['ins-trend'] = function (D, B, s, o) {
    var id = s.ins, S = sn(D, id), y1 = +s.y1, y2 = +s.y2;
    var ys = D.years.filter(function (y) { return y >= y1 && y <= y2; }).map(String), act = ys.filter(function (y) { return active(D, id, y); });
    o.cav = true; o.link = [LINK.explorer]; o.src = SRC.tot;
    if (!act.length) { o.ok = false; o.say.push(S + ' has no full-year figures from ' + y1 + ' to ' + y2 + '.', has(D, id)); return; }
    var E = act.map(function (y) { return tot(D, id, y); }), f = act[0], l = act[act.length - 1], ef = E[0], el = E[E.length - 1];
    var uws = E.map(function (e) { return e[4]; }), total = sum(uws), nl = uws.filter(function (v) { return v < 0; }).length;
    o.say.push(f === l ? 'In ' + f + ' ' + S + ' wrote ' + money(ef[0]) + ' of premium.'
      : S + "'s written premium went from " + money(ef[0]) + ' in ' + f + ' to ' + money(el[0]) + ' in ' + l + '.');
    o.say.push('Its combined ratio was ' + pct(cr(ef)) + ' in ' + f + (f !== l ? ' and ' + pct(cr(el)) + ' in ' + l : '') + '.');
    o.say.push(f === l ? 'Its underwriting result was ' + money(total, true) + '.'
      : 'Its underwriting result over those ' + act.length + ' years added up to ' + money(total, true) + ', with a loss in ' + nl + ' of them.');
    var gaps = ys.filter(function (y) { return act.indexOf(y) < 0; }).map(Number);
    var nfg = gaps.filter(function (y) { return (D.nf[id] || []).indexOf(y) > -1; });
    if (gaps.length) o.say.push('No full-year figures for ' + span(gaps, D.years) + (nfg.length ? '; it filed no Q4 return for ' + span(nfg, D.years) : '') + '.');
    o.nums = [['wp1', 'Written premium, ' + f, money(ef[0])], ['wp2', 'Written premium, ' + l, money(el[0])],
      ['cr1', 'Combined ratio, ' + f, pct(cr(ef))], ['cr2', 'Combined ratio, ' + l, pct(cr(el))],
      ['uw', 'Underwriting result, total', money(total, true)], ['nl', 'Years with a loss', nl + ' of ' + act.length]];
    var U = ys.map(function (y) { var e = act.indexOf(y) > -1 ? tot(D, id, y) : null; return e ? e[4] : null; }), sc = scale(U);
    o.chart = { type: 'columns', title: S + ': underwriting result, KSh ' + sc[0], cats: ys, unit: sc[0],
      series: [['sign', 'Underwriting result', U.map(function (v) { return v === null ? null : v / sc[1]; })]], key: [['pos', 'Profit'], ['neg', 'Loss']] };
    o.table = { head: ['Year', 'Written premium', 'Combined ratio', 'Underwriting result'],
      rows: act.map(function (y, i) { return [y, money(E[i][0]), pct(cr(E[i])), money(E[i][4], true)]; }) };
  };

  function rankIn(D, y, id) {   // [rank, of, joint, share, premium] by written premium, or null
    var w = [], mine = null;
    D.ins.forEach(function (x) { var e = tot(D, x.id, y); if (e && e[0] > 0) { w.push(e[0]); if (x.id === id) mine = e[0]; } });
    if (mine === null) return null;
    var above = w.filter(function (v) { return v > mine; }).length, same = w.filter(function (v) { return v === mine; }).length;
    return [above + 1, w.length, same > 1, mine / sum(w), mine];
  }
  A['ins-rank'] = function (D, B, s, o) {
    var id = s.ins, S = sn(D, id), y = s.yr;
    o.cav = true; o.link = [LINK.structure, LINK.explorer]; o.src = SRC.tot;
    var r = rankIn(D, y, id);
    if (!r) { o.ok = false; o.say.push(missing(D, id, y) || S + ' wrote no premium in ' + y + '.', has(D, id)); return; }
    o.say.push('In ' + y + ' ' + S + ' was ' + (r[2] ? 'joint ' : '') + ordinal(r[0]) + ' of the ' + r[1] + ' insurers by written premium, with '
      + pct(r[3]) + ' of the market (' + money(r[4]) + ').');
    var ys = D.years.map(String), R = ys.map(function (z) { return rankIn(D, z, id); }), have = ys.filter(function (z, i) { return R[i]; });
    var fi = ys.indexOf(have[0]), li = ys.indexOf(have[have.length - 1]);
    if (fi !== li) o.say.push('Its share was ' + pct(R[fi][3]) + ' in ' + ys[fi] + ' and ' + pct(R[li][3]) + ' in ' + ys[li] + '.');
    o.nums = [['rank', 'Rank by written premium', (r[2] ? 'joint ' : '') + r[0] + ' of ' + r[1]], ['share', 'Market share', pct(r[3])],
      ['wp', 'Written premium', money(r[4])], ['s1', 'Share, ' + ys[fi], pct(R[fi][3])], ['s2', 'Share, ' + ys[li], pct(R[li][3])]];
    o.chart = { type: 'columns', title: S + ': share of written premium', cats: ys, unit: 'pct',
      series: [['neu', 'Market share', R.map(function (k) { return k ? k[3] * 100 : null; })]] };
    o.table = { head: ['Year', 'Rank', 'Market share', 'Written premium'], rows: [] };
    ys.forEach(function (z, i) { var k = R[i]; if (k) o.table.rows.push([z, (k[2] ? 'joint ' : '') + k[0] + ' of ' + k[1], pct(k[3]), money(k[4])]); });
  };

  A['ins-mix'] = function (D, B, s, o) {
    var id = s.ins, S = sn(D, id), y = s.yr;
    o.cav = true; o.link = [LINK.explorer]; o.src = SRC.cls;
    var miss = missing(D, id, y);
    if (miss) { o.ok = false; o.say.push(miss, has(D, id)); return; }
    var it = [];
    D.classes.forEach(function (c, i) { var f = cls(D, id, y, String(i)); if (f && f[0] > 0) it.push([i, f[0]]); });
    if (!it.length) { o.ok = false; o.say.push(S + ' reported no gross premium by class in ' + y + '.'); return; }
    var t = sum(it.map(function (v) { return v[1]; }));
    it.sort(function (a, b) { return b[1] - a[1] || a[0] - b[0]; });
    var nm = function (k) { return D.classes[it[k][0]]; }, sh = function (k) { return pct(it[k][1] / t); };
    o.say.push('In ' + y + ' ' + S + "'s largest class was " + nm(0) + ', with ' + sh(0) + ' of its gross premium (' + money(it[0][1]) + ').');
    if (it.length >= 3) o.say.push('Next came ' + nm(1) + ' (' + sh(1) + ') and ' + nm(2) + ' (' + sh(2) + ').');
    else if (it.length === 2) o.say.push('Next came ' + nm(1) + ' (' + sh(1) + ').');
    o.say.push('It wrote ' + it.length + ' of the ' + D.classes.length + ' classes.');
    o.nums = it.slice(0, 3).map(function (v, k) { return ['c' + (k + 1), nm(k), sh(k)]; }).concat([['k', 'Classes written', String(it.length)]]);
    o.chart = { type: 'dots', title: S + ': share of gross premium by class, ' + y, unit: 'pct',
      rows: it.map(function (v) { return [D.classes[v[0]], v[1] / t * 100]; }) };
    o.table = { head: ['Class', 'Gross premium', 'Share'], rows: it.map(function (v) { return [D.classes[v[0]], money(v[1]), pct(v[1] / t)]; }) };
  };

  A.scorecard = function (D, B, s, o) {
    var id = s.ins, S = sn(D, id), y = s.yr, r = (D.sc[id] || {})[y];
    o.cav = true; o.link = [LINK.scorecard]; o.src = SRC.sc;
    if (!r) {
      o.ok = false;
      var why = (D.ns[id] || {})[y];
      o.say.push(why ? S + ' was not scored in ' + y + ': ' + why + '.' : S + ' is not in the scorecard for ' + y + '.');
      var gs = Object.keys(D.sc[id] || {}).map(function (z) { return z + ' ' + D.sc[id][z][0]; });
      if (gs.length) o.say.push('Its grades in the years it was scored: ' + gs.join(', ') + '.');
      return;
    }
    var p = r.slice(5, 9), fl = r[9] ? r[9].split(';') : [];
    o.say.push('In ' + y + ' ' + S + ' scored ' + fix(r[4], 1) + ' out of 100 and was graded ' + r[0] + ', ' + ordinal(r[2]) + ' of the ' + r[3] + ' insurers scored.');
    var av = [0, 1, 2, 3].filter(function (i) { return p[i] !== null; });
    if (av.length > 1) {
      var hi = av[0], lo = av[0];
      av.forEach(function (i) { if (p[i] > p[hi]) hi = i; if (p[i] < p[lo]) lo = i; });
      o.say.push('Its strongest pillar was ' + PILLARS[hi] + ' (' + fix(p[hi], 1) + '), its weakest ' + PILLARS[lo] + ' (' + fix(p[lo], 1) + ').');
    }
    var cap = fl.indexOf('negative_equity') > -1 ? 'negative_equity' : 'below_capital_floor';
    if (r[0] !== r[1]) o.say.push('The score alone would give ' + r[1] + '; ' + FLAGS[cap] + ' caps the grade at D.');
    var rest = fl.filter(function (f) { return r[0] === r[1] || f !== cap; });   // the cap's own flag is said once
    if (rest.length) o.say.push((r[0] !== r[1] ? 'Other watch flags: ' : 'Watch flags: ') + rest.map(function (f) { return FLAGS[f] || f; }).join('; ') + '.');
    o.nums = [['grade', 'Grade', r[0]], ['rank', 'Rank', r[2] + ' of ' + r[3]], ['score', 'Score', fix(r[4], 1)]]
      .concat(p.map(function (v, i) { return ['p' + i, PILLARS[i], v === null ? 'n/a' : fix(v, 1)]; }));
    o.chart = { type: 'dots', title: S + ': scorecard pillars, ' + y + ', out of 100', unit: 'score', lo: 0, hi: 100, ticks: [0, 25, 50, 75, 100],
      rows: av.map(function (i) { return [PILLARS[i], p[i]]; }).concat([['Total score', r[4], 'neu ring']]) };
    o.table = { head: ['Pillar', 'Score'], rows: p.map(function (v, i) { return [PILLARS[i], v === null ? 'n/a' : fix(v, 1)]; }).concat([['Total score', fix(r[4], 1)]]) };
  };

  A.growth = function (D, B, s, o) {
    // growth counts merged companies together in both years, as the Market Structure page does
    var y = s.yr, p = String(+y - 1), it = [], A0 = 0, A1 = 0;
    D.ins.forEach(function (x, k) {
      var a = tot(D, x.id, p), b = tot(D, x.id, y);
      if (a && a[0] > 0) A0 += a[0];
      if (b && b[0] > 0) A1 += b[0];
      if (D.mg[x.id]) return;
      var pa = proForma(D, x.id, p), pb = proForma(D, x.id, y);
      // its own return in both years: a missing base year would make a merged-in company look like growth
      if (a && a[0] > 0 && b && b[0] > 0 && pa >= 5e5) it.push([k, pb / pa - 1, cr(b), pb, x.id]);
    });
    o.cav = true; o.link = [LINK.structure]; o.src = SRC.tot;
    it.sort(function (u, v) { return v[1] - u[1] || u[0] - v[0]; });
    var top = it.slice(0, 5), mg = A0 > 0 ? A1 / A0 - 1 : null;
    if (!top.length) { o.ok = false; o.say.push('No insurer had KSh 500m of premium in ' + p + ' and premium in ' + y + '.'); return; }
    o.say.push('In ' + y + ' the fastest growth among insurers with at least KSh 500m of premium in ' + p + ' was ' + sn(D, top[0][4]) + "'s: "
      + pct(top[0][1], true) + ', at a combined ratio of ' + pct(top[0][2]) + '.');
    o.say.push("The market's written premium changed by " + pct(mg, true) + '. Companies that merged are counted together in both years, as on the Market Structure page.');
    var k = top.filter(function (t) { return t[2] !== null && t[2] > 1; }).length;
    o.say.push('Of these ' + top.length + ', ' + k + ' wrote at a combined ratio above 100%, that is at an underwriting loss.');
    o.nums = [];
    top.forEach(function (t, i) { o.nums.push(['g' + (i + 1), sn(D, t[4]), pct(t[1], true)], ['cr' + (i + 1), sn(D, t[4]) + ', combined ratio', pct(t[2])]); });
    o.nums.push(['mg', 'Market', pct(mg, true)]);
    o.chart = { type: 'dots', title: 'Growth in written premium, ' + p + ' to ' + y, unit: 'pct', rows: top.map(function (t) { return [sn(D, t[4]), t[1] * 100]; }) };
    o.table = { head: ['Insurer', 'Growth', 'Combined ratio', 'Written premium'], rows: top.map(function (t) { return [sn(D, t[4]), pct(t[1], true), pct(t[2]), money(t[3])]; }) };
  };

  A.backtest = function (D, B, s, o) {
    var R = D.bt, n = R.length, nb = R.filter(function (b) { return b[7]; }).length;
    var yrs = R.map(function (b) { return +b[2].slice(0, 4); }), ev = [];
    R.forEach(function (b) { if (ev.indexOf(b[1]) < 0) ev.push(b[1]); });
    var mon = function (d) { return MONTHS[+d.slice(5, 7) - 1] + ' ' + d.slice(0, 4); };
    o.say.push('The regulator acted on ' + n + ' insurers between ' + Math.min.apply(null, yrs) + ' and ' + Math.max.apply(null, yrs) + ': ' + ev.join(' or ') + '.');
    o.say.push(nb + ' of them were in the bottom fifth of the scorecard in their last scored year before it acted.');
    R.forEach(function (b) {
      if (!b[7]) o.say.push(sn(D, b[0]) + ' was ' + ordinal(b[5]) + ' of ' + b[6] + ' in ' + b[3] + '.' + (b[8] ? ' It was not scored after that: ' + b[8] + '.' : ''));
    });
    o.nums = [['bottom', 'In the bottom fifth', nb + ' of ' + n]];
    o.chart = { type: 'dots', title: 'Place in the table in the last scored year, top to bottom', unit: 'place', lo: 0, hi: 100, ticks: [0, 20, 40, 60, 80, 100],
      band: [80, 100, 'Bottom fifth'], rows: R.map(function (b) { return [sn(D, b[0]), b[5] / b[6] * 100, '', b[5] + ' of ' + b[6]]; }) };
    o.table = { head: ['Insurer', 'Regulator acted', 'Last scored', 'Grade', 'Rank', 'Bottom fifth'],
      rows: R.map(function (b) { return [sn(D, b[0]), b[1] + ', ' + mon(b[2]), String(b[3]), b[4], b[5] + ' of ' + b[6], b[7] ? 'Yes' : 'No']; }) };
    o.cav = true; o.link = [LINK.scorecard]; o.src = SRC.sc;
  };

  A['tri-largest'] = function (D, B, s, o) {
    var T = D.tri, res = T.map(function (t) { return t[3]; }), ult = T.map(function (t) { return t[2]; });
    var un = T.map(function (t) { return t[3] / t[2]; }), L = argmax(res), U = argmax(ult), Sx = argmax(un), total = sum(res);
    o.say.push(T[L][0] + ' needs the largest reserve: ' + usd(res[L]) + " of the six lines' " + usd(total) + '.');
    o.say.push(L === U ? 'It is also the largest line, with ' + usd(ult[L]) + ' of ultimate claims, of which ' + pct(un[L]) + ' is still unpaid.'
      : 'It is not the largest line by ultimate claims (' + T[U][0] + ' is); ' + pct(un[L]) + ' of its ' + usd(ult[L]) + ' ultimate is still unpaid.');
    if (Sx !== L) o.say.push(T[Sx][0] + ' has the largest share still unpaid, ' + pct(un[Sx]) + ', but its ultimate is ' + (ult[Sx] < ult[L] ? 'smaller' : 'larger') + ': ' + usd(ult[Sx]) + '.');
    o.say.push('A reserve is the ultimate less what has been paid, so it is large where a line is large or slow to pay.');
    o.nums = [['line', T[L][0], usd(res[L])], ['total', 'Six lines', usd(total)], ['ult', 'Its ultimate', usd(ult[L])], ['un', 'Its share unpaid', pct(un[L])],
      ['slow', T[Sx][0] + ', share unpaid', pct(un[Sx])]];
    var order = res.map(function (v, i) { return i; }).sort(function (a, b) { return res[b] - res[a] || a - b; });
    o.chart = { type: 'dots', title: 'Reserve by line, US$bn', unit: 'usdbn', rows: order.map(function (i) { return [T[i][0], res[i] / 1e6]; }) };
    o.table = { head: ['Line', 'Paid to date', 'Ultimate', 'Reserve', 'Share unpaid'], rows: order.map(function (i) { return [T[i][0], usd(T[i][1]), usd(ult[i]), usd(res[i]), pct(un[i])]; }) };
    o.src = SRC.tri; o.link = [LINK.tri, LINK.ifrs];
  };

  A['tri-unpaid'] = function (D, B, s, o) {
    var i = D.tri.map(function (t) { return slug(t[0]); }).indexOf(s.line), t = D.tri[i];
    o.say.push('Of ' + t[0] + "'s " + usd(t[2]) + ' of ultimate claims, ' + usd(t[3]) + ' is still unpaid: ' + pct(t[3] / t[2]) + '.');
    o.say.push(usd(t[1]) + ' has been paid to date.');
    o.nums = [['ult', 'Ultimate', usd(t[2])], ['res', 'Still unpaid', usd(t[3])], ['un', 'Share unpaid', pct(t[3] / t[2])], ['paid', 'Paid to date', usd(t[1])]];
    o.chart = { type: 'split', title: t[0] + ': paid and unpaid, US$', parts: [['ctx', 'Paid to date', t[1], usd(t[1])], ['neu', 'Still unpaid', t[3], usd(t[3])]] };
    o.table = { head: ['', 'Amount'], rows: [['Paid to date', usd(t[1])], ['Still unpaid', usd(t[3])], ['Ultimate', usd(t[2])]] };
    o.src = SRC.tri; o.link = [LINK.tri];
  };

  A['tri-sum'] = function (D, B, s, o) {
    var T = D.tri, res = T.map(function (t) { return t[3]; }), total = sum(res), L = argmax(res), i17 = D.i17;
    o.say.push('The six chain ladder reserves add up to ' + usd(total) + ', ' + pct(res[L] / total) + ' of it in ' + T[L][0] + '.');
    o.say.push(fix(total / 1e6, 2) === fix(i17[0], 2) ? 'That is the undiscounted reserve the IFRS 17 case study starts from.'
      : 'The IFRS 17 case study starts from US$' + fix(i17[0], 2) + 'bn.');
    o.say.push('Discounting at ' + fix(i17[2], 1) + '% takes US$' + fix(-i17[1], 2) + 'bn off it, and a risk adjustment at the 75th percentile adds US$' + fix(i17[3], 0) + 'm.');
    o.nums = [['total', 'Six reserves', usd(total)], ['case', 'IFRS 17 case study, undiscounted', 'US$' + fix(i17[0], 2) + 'bn'],
      ['disc', 'Discounting', 'US$' + fix(i17[1], 2) + 'bn'], ['ra', 'Risk adjustment, 75th percentile', 'US$' + fix(i17[3], 0) + 'm']];
    var order = res.map(function (v, i) { return i; }).sort(function (a, b) { return res[b] - res[a] || a - b; });
    o.chart = { type: 'dots', title: 'Reserve by line, US$bn', unit: 'usdbn', rows: order.map(function (i) { return [T[i][0], res[i] / 1e6]; }) };
    o.table = { head: ['Line', 'Reserve'], rows: order.map(function (i) { return [T[i][0], usd(res[i])]; }).concat([['Six lines', usd(total)]]) };
    o.src = SRC.tri; o.link = [LINK.ifrs, LINK.tri];
  };

  function about(D, B, s, o, item) {
    o.say.push(item.lead);
    o.points = item.points;
  }
  A['about-done'] = function (D, B, s, o) { about(D, B, s, o, B.about['about-done'][s.topic]); };
  ['about-tools', 'about-checks', 'about-open', 'about-contact'].forEach(function (q) {
    A[q] = function (D, B, s, o) { about(D, B, s, o, B.about[q]); };
  });

  function answer(D, B, q, s0) {
    if (!question(B, q) || !A[q]) return null;
    var s = normalize(D, B, q, s0 || {});
    var o = { q: q, slots: s, title: title(D, B, q, s), ok: true, say: [], nums: [], points: null, chart: null, table: null, src: '', link: [], cav: false, note: '' };
    A[q](D, B, s, o);
    if (s.ins) {
      var m = mergerNote(D, s.ins);
      o.note = (m ? m + ' ' : '') + "Names in IRA's returns: " + ctx(D).byId[s.ins].a.join('; ') + '.';
    }
    return o;
  }

  var ENGINE = { answer: answer, defaults: defaults, normalize: normalize, choices: choices, title: title, question: question,
    fmt: { fix: fix, money: money, usd: usd, pct: pct, ordinal: ordinal, span: span, slug: slug }, LINK: LINK, SRC: SRC };
  if (typeof module !== 'undefined' && module.exports) module.exports = ENGINE;
  if (typeof document === 'undefined') return;

  /* ================================================================ the page */
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  /* --- charts: the markup of tools/viz.py and of bars() in tools/build.py --- */
  function niceTicks(lo, hi, n) {
    n = n || 4;
    var spanv = (hi - lo) || Math.abs(hi) || 1, raw = spanv / n, mag = Math.pow(10, Math.floor(Math.log10(raw))), step = 10 * mag;
    [1, 2, 2.5, 5, 10].some(function (m) { if (m * mag >= raw) { step = m * mag; return true; } return false; });
    var t = Math.floor(lo / step) * step, out = [];
    while (t < hi + step * 0.999) { out.push(Math.round(t * 1e10) / 1e10); t += step; }
    return out;
  }
  function unitFmt(u) {
    var dec = function (v) { return Math.abs(v - Math.round(v)) > 1e-9 ? 1 : 0; };
    return {
      bn: [function (v) { return fix(v, 1, true); }, function (t) { return fix(t, dec(t), false); }],
      m: [function (v) { return fix(v, Math.abs(v) < 10 ? 1 : 0, true); }, function (t) { return fix(t, dec(t), false); }],
      pct: [function (v) { return fix(v, 1) + '%'; }, function (t) { return fix(t, dec(t)) + '%'; }],
      n: [function (v) { return String(v); }, function (t) { return fix(t, 0); }],
      score: [function (v) { return fix(v, 1); }, function (t) { return fix(t, 0); }],
      place: [function (v) { return fix(v, 0) + '%'; }, function (t) { return t === 0 ? 'top' : t === 100 ? 'bottom' : fix(t, 0) + '%'; }],
      usdbn: [function (v) { return fix(v, 2); }, function (t) { return fix(t, dec(t)); }]
    }[u];
  }
  function vzFigure(t, plot, key, table) {
    return '<figure class="panel vz"><h3>' + esc(t) + '</h3>' + plot + (key || '') + (table || '') + '</figure>';
  }
  function vzKey(items) { return '<ul class="vz-key">' + items.map(function (k) { return '<li><i class="' + k[0] + '"></i>' + esc(k[1]) + '</li>'; }).join('') + '</ul>'; }
  function vzTable(tb) {
    var th = tb.head.map(function (h) { return '<th scope="col">' + esc(h) + '</th>'; }).join('');
    var tr = tb.rows.map(function (r) { return '<tr>' + r.map(function (c, i) { return i === 0 ? '<th scope="row">' + esc(c) + '</th>' : '<td>' + esc(c) + '</td>'; }).join('') + '</tr>'; }).join('');
    return '<details class="vz-tab"><summary>Show the numbers</summary><div class="vz-scroll"><table class="data"><thead><tr>' + th + '</tr></thead><tbody>' + tr + '</tbody></table></div></details>';
  }
  function vzColumns(c, label) {
    var f = unitFmt(c.unit), vals = [];
    c.series.forEach(function (s) { s[2].forEach(function (v) { if (v !== null) vals.push(v); }); });
    var lo = Math.min(0, Math.min.apply(null, vals)), hi = Math.max(0, Math.max.apply(null, vals)), ticks = niceTicks(lo, hi);
    lo = Math.min(lo, ticks[0]); hi = Math.max(hi, ticks[ticks.length - 1]);
    var spanv = hi - lo, y = function (v) { return (hi - v) / spanv * 100; };
    var grid = ticks.map(function (t) { return '<span class="vz-tick' + (t === 0 ? ' z' : '') + '" style="top:' + y(t).toFixed(2) + '%"><b>' + f[1](t) + '</b></span>'; }).join('');
    var groups = c.cats.map(function (cat, ci) {
      return '<span class="vz-g">' + c.series.map(function (s) {
        var v = s[2][ci];
        if (v === null) return '<span class="vz-lane"></span>';
        var up = v >= 0, top = up ? y(v) : y(0), h = up ? y(0) - y(v) : y(v) - y(0), mc = s[0] === 'sign' ? (up ? 'pos' : 'neg') : s[0];
        return '<span class="vz-lane"><i class="vz-col ' + mc + ' ' + (up ? 'up' : 'dn') + '" style="top:' + top.toFixed(2) + '%;height:' + Math.max(h, 0.6).toFixed(2) + '%" title="'
          + esc(s[1] + ', ' + cat + ': ' + f[0](v)) + '"></i></span>';
      }).join('') + '</span>';
    }).join('');
    var xl = c.cats.map(function (cat) { return '<span><b class="f">' + esc(cat) + '</b><b class="s">' + esc(/^\d{4}$/.test(cat) ? "'" + cat.slice(2) : cat) + '</b></span>'; }).join('');
    return '<div class="vz-colchart" style="--h:200px"><div class="vz-plot" role="img" aria-label="' + esc(label) + '">' + grid
      + '<div class="vz-gs">' + groups + '</div></div><div class="vz-x" aria-hidden="true">' + xl + '</div></div>';
  }
  function vzDots(c, label) {
    var f = unitFmt(c.unit), vals = c.rows.map(function (r) { return r[1]; });
    var ticks = c.ticks || niceTicks(Math.min(0, Math.min.apply(null, vals)), Math.max(0, Math.max.apply(null, vals)));
    var lo = c.lo !== undefined ? c.lo : ticks[0], hi = c.hi !== undefined ? c.hi : ticks[ticks.length - 1];
    var x = function (v) { return (v - lo) / (hi - lo) * 100; };
    var under = ticks.map(function (t) { return '<span class="vz-vt" style="left:' + x(t).toFixed(2) + '%"></span>'; }).join('');
    if (c.band) under += '<span class="vz-band" style="left:' + x(c.band[0]).toFixed(2) + '%;width:' + (x(c.band[1]) - x(c.band[0])).toFixed(2) + '%"></span>';
    var rows = c.rows.map(function (r) {
      var lab = r[3] !== undefined ? r[3] : f[0](r[1]);
      return '<div class="vz-row"><span class="vz-name">' + esc(r[0]) + '</span><span class="vz-track">' + under
        + '<i class="vz-dot ' + (r[2] || 'neu') + '" style="left:' + x(r[1]).toFixed(2) + '%" title="' + esc(r[0] + ': ' + lab) + '"><b class="'
        + (x(r[1]) > 70 ? 'l' : 'r') + '">' + esc(lab) + '</b></i></span></div>';   // near the right end the label goes on the left
    }).join('');
    var axis = ticks.map(function (t, i) { return '<span class="' + (i % 2 ? 'o' : '') + '" style="left:' + x(t).toFixed(2) + '%">' + f[1](t) + '</span>'; }).join('');
    var tops = c.band ? '<span class="vz-bandlab" style="left:' + x((c.band[0] + c.band[1]) / 2).toFixed(2) + '%">' + esc(c.band[2]) + '</span>' : '';
    return '<div class="vz-dots" role="img" aria-label="' + esc(label) + '"><div class="vz-row vz-top" aria-hidden="true"><span></span><span class="vz-track">' + tops + '</span></div>'
      + rows + '<div class="vz-row vz-axis" aria-hidden="true"><span></span><span class="vz-track">' + axis + '</span></div></div>';
  }
  function vzSplit(c, label) {
    var t = sum(c.parts.map(function (p) { return p[2]; }));
    var fits = function (v, s) { return s && v / t * 100 >= 2.4 * s.length + 4; };
    return '<div class="vz-split" role="img" aria-label="' + esc(label) + '">' + c.parts.map(function (p) {
      return '<span class="vz-seg ' + p[0] + '" style="flex:' + (p[2] / t * 100).toFixed(3) + ' 1 0" title="' + esc(p[1] + ': ' + p[3]) + '">' + (fits(p[2], p[3]) ? '<b>' + esc(p[3]) + '</b>' : '') + '</span>';
    }).join('') + '</div>';
  }
  function siteBars(c, label) {   // bars() in tools/build.py: diverging bars with their values as text
    var vs = c.items.map(function (i) { return i[1]; }), lo = Math.min(0, Math.min.apply(null, vs)), hi = Math.max(0, Math.max.apply(null, vs)), spanv = hi - lo, zero = -lo / spanv * 100;
    return '<div class="bars" role="img" aria-label="' + esc(label) + '">' + c.items.map(function (it) {
      var w = Math.max(Math.abs(it[1]) / spanv * 100, 0.5), side = it[1] < 0 ? 'neg' : 'pos', inn = it[1] < 0 && w / 100 > 0.3 ? ' in' : '';
      return '<span class="lab">' + esc(it[0]) + '</span><span class="track" style="--zero:' + zero.toFixed(2) + '%;--w:' + w.toFixed(2) + '%"><span class="bar ' + side
        + '"></span><span class="val ' + side + inn + '">' + fix(it[1], 1, true) + '</span></span>';
    }).join('') + '</div>';
  }
  function chartHtml(o) {
    var c = o.chart, summary = c.title + '. ' + o.say[0];
    var plot = c.type === 'columns' ? vzColumns(c, summary) : c.type === 'dots' ? vzDots(c, summary) : c.type === 'split' ? vzSplit(c, summary) : siteBars(c, summary);
    var key = c.key ? vzKey(c.key) : c.type === 'split' ? vzKey(c.parts.map(function (p) { return [p[0], p[1] + ', ' + p[3]]; })) : '';
    return vzFigure(c.title, plot, key, o.table ? vzTable(o.table) : '');
  }

  /* --- the thread --- */
  var D = null, B = null, thread, status, n = 0;

  function answerHtml(o) {
    var h = '<p class="ask-who">Answer</p>' + o.say.map(function (p) { return '<p class="ask-say">' + esc(p) + '</p>'; }).join('');
    // About answers: quotes from pages on this site, a heading and what it says, then the link
    if (o.points) h += '<ul class="ask-points">' + o.points.map(function (p) {
      var q = p[0].length > 1 ? '<b>' + esc(p[0][0]) + '</b>: ' + esc(p[0].slice(1).join(' ')) : esc(p[0][0]);
      return '<li>' + q + ' <a href="' + esc(p[1]) + '">' + esc(p[2]) + '</a></li>';
    }).join('') + '</ul>';
    if (o.nums.length) h += '<dl class="ask-nums">' + o.nums.map(function (x) { return '<div data-k="' + esc(x[0]) + '"><dt>' + esc(x[1]) + '</dt><dd>' + esc(x[2]) + '</dd></div>'; }).join('') + '</dl>';
    if (o.chart) h += chartHtml(o);
    else if (o.table) h += vzTable(o.table);
    if (o.src) h += '<p class="ask-src"><b>Source</b> ' + esc(o.src) + '</p>';
    if (o.cav) h += '<p class="ask-cav">' + esc(B.caveat) + '</p>';
    if (o.note) h += '<p class="ask-note">' + esc(o.note) + '</p>';
    if (o.link.length) h += '<p class="ask-links">' + o.link.map(function (l) { return '<a href="' + esc(l[0]) + '">' + esc(l[1]) + '</a>'; }).join('') + '</p>';
    return h;
  }
  function post(html, cls) {
    var el = document.createElement('div');
    el.className = 'ask-msg ' + cls;
    el.innerHTML = html;
    thread.appendChild(el);
    thread.hidden = false;
    document.getElementById('ask-empty').hidden = true;
    document.getElementById('ask-reset').hidden = false;
    return el;
  }
  function hashFor(q, s) {
    return '#q=' + encodeURIComponent(q) + Object.keys(s).map(function (k) { return '&' + k + '=' + encodeURIComponent(s[k]); }).join('');
  }
  function show(el) {
    var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    el.scrollIntoView({ behavior: still ? 'auto' : 'smooth', block: 'start' });
  }
  function ask(q, s) {
    var o = answer(D, B, q, s);
    if (!o) return;
    n += 1;
    post('<p class="ask-who">You asked</p><p class="ask-qt">' + esc(o.title) + '</p>', 'ask-q');
    var el = post(answerHtml(o), 'ask-a' + (o.ok ? '' : ' ask-none'));
    el.setAttribute('data-q', q);
    el.setAttribute('data-n', String(n));
    status.textContent = o.say.join(' ');
    try { history.replaceState(history.state, '', hashFor(q, o.slots)); } catch (e) { /* a file:// page may refuse */ }
    show(el.previousSibling);
  }

  /* --- the question chips --- */
  function slotSelect(q, k, kind, v) {
    var names = { y1: 'First year', y2: 'Last year', yr: 'Year', ins: 'Insurer', cls: 'Class', line: 'Line', topic: 'Topic' };
    return '<select data-slot="' + k + '" aria-label="' + names[k] + '">' + choices(D, B, kind).map(function (c) {
      return '<option value="' + esc(c[0]) + '"' + (c[0] === v ? ' selected' : '') + '>' + esc(c[1]) + '</option>';
    }).join('') + '</select>';
  }
  function chipHtml(Q, s) {
    if (!Object.keys(Q.slots).length) return '<button type="button" class="ask-chip ask-one" data-q="' + Q.id + '">' + esc(Q.t) + '</button>';
    var text = esc(Q.t).replace(/\{(\w+)\}/g, function (m, k) { return slotSelect(Q.id, k, Q.slots[k], s[k]); });
    return '<div class="ask-chip" data-q="' + Q.id + '"><span class="ask-chip-t">' + text + '</span><button type="button" class="ask-go">Ask</button></div>';
  }
  function readChip(el) {
    var s = {};
    [].forEach.call(el.querySelectorAll('select[data-slot]'), function (x) { s[x.getAttribute('data-slot')] = x.value; });
    return s;
  }
  function drawBank() {
    var box = document.getElementById('ask-bank');
    box.innerHTML = B.groups.map(function (g) {
      var qs = B.questions.filter(function (Q) { return Q.g === g[0]; });
      return '<div class="ask-group"><h3 class="tag">' + esc(g[1]) + '</h3><div class="ask-chips">'
        + qs.map(function (Q) { return chipHtml(Q, defaults(D, B, Q.id)); }).join('') + '</div></div>';
    }).join('');
    box.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      var chip = b.closest('[data-q]');
      ask(chip.getAttribute('data-q'), readChip(chip));
    });
  }

  /* --- typed questions: matched to a chip by keywords, never answered by guess --- */
  var STOP = ['insurance', 'assurance', 'company', 'limited', 'ltd', 'kenya', 'the', 'of', 'k', 'general', 'micro'];
  function norm(t) { return ' ' + String(t).toLowerCase().replace(/[^a-z0-9$']+/g, ' ').replace(/\s+/g, ' ').trim() + ' '; }
  function aliases(x) {
    var out = {};
    [x.s, x.n.split(' (')[0]].concat(x.a).forEach(function (a) {
      var w = norm(a).trim();
      if (w.length > 1) out[w] = 1;
      var r = w.split(' ').filter(function (t) { return STOP.indexOf(t) < 0; }).join(' ');
      if (r.length > 1) out[r] = 1;
    });
    return Object.keys(out);
  }
  function longest(t, table) {   // table: [[value, [words]]]; the value whose word appears longest in t
    var best = null, bl = 0;
    table.forEach(function (r) { r[1].forEach(function (w) { var k = norm(w).trim(); if (k && t.indexOf(' ' + k + ' ') > -1 && k.length > bl) { best = r[0]; bl = k.length; } }); });
    return best;
  }
  function hit(t, k) { k = norm(k).trim(); return k.length <= 2 ? t.indexOf(' ' + k + ' ') > -1 : t.indexOf(' ' + k) > -1; }
  function match(text) {
    var t = norm(text);
    if (t.trim().length < 2) return null;
    var found = {};
    found.ins = longest(t, D.ins.map(function (x) { return [x.id, aliases(x)]; }));
    found.cls = longest(t, D.classes.map(function (c) { return [slug(c), [c].concat(B.classWords[c] || [])]; }));
    found.line = longest(t, D.tri.map(function (l) { return [slug(l[0]), [l[0]].concat(B.lineWords[l[0]] || [])]; }));
    found.topic = longest(t, B.topics.map(function (p) { return [p[0], p[2]]; }));
    var ys = (text.match(/\b(19|20)\d{2}\b/g) || []).map(Number);
    var best = null, bs = 0;
    B.questions.forEach(function (Q) {
      var sl = Q.slots, sc = 0;
      Q.kw.forEach(function (k) { if (hit(t, k)) sc += 2; });
      if (sl.ins) { if (!found.ins) return; sc += 3; } else if (found.ins) sc -= 2;
      if (sl.cls && found.cls) sc += 2;
      if (sl.line && found.line) sc += 2;
      if (sl.topic && found.topic) sc += 2;
      if (sc > bs) { best = Q; bs = sc; }
    });
    if (!best || bs < 2) return null;
    var s = defaults(D, B, best.id);
    ['ins', 'cls', 'line', 'topic'].forEach(function (k) { if (best.slots[k] && found[k]) s[k] = found[k]; });
    if (ys.length) {
      if (best.slots.yr) s.yr = String(ys[ys.length - 1]);
      if (best.slots.y1) {
        if (ys.length > 1) { s.y1 = String(Math.min.apply(null, ys)); s.y2 = String(Math.max.apply(null, ys)); }
        else if (/\b(since|from|after)\b/.test(text.toLowerCase())) s.y1 = String(ys[0]);
        else s.y2 = String(ys[0]);
      }
    }
    return { q: best.id, s: normalize(D, B, best.id, s) };
  }
  function typed(text) {
    if (!text.trim()) return;
    post('<p class="ask-who">You typed</p><p class="ask-qt">' + esc(text) + '</p>', 'ask-q');
    var m = match(text), el;
    if (m) {
      el = post('<p class="ask-who">Did you mean</p><div class="ask-chips">' + chipHtml(question(B, m.q), m.s) + '</div>'
        + '<p class="ask-say small">Change anything in the question, then ask it. Nothing is answered until you do.</p>', 'ask-a ask-dym');
      el.addEventListener('click', function (e) {
        var b = e.target.closest('button');
        if (!b) return;
        var chip = b.closest('[data-q]');
        ask(chip.getAttribute('data-q'), readChip(chip));
      });
      status.textContent = 'Did you mean: ' + title(D, B, m.q, m.s);
    } else {
      el = post('<p class="ask-who">No match</p><p class="ask-say">None of the questions here matches that, so there is no answer to give. The questions cover '
        + B.groups.map(function (g) { return esc(g[1].toLowerCase()); }).join(', ') + '. <a href="#ask-bank">Choose one</a>.</p>', 'ask-a ask-none');
      status.textContent = 'No question matches that.';
    }
    show(el.previousSibling);
  }

  function fromHash() {
    var h = location.hash.replace(/^#/, ''), p = {};
    if (h.indexOf('q=') !== 0) return;
    h.split('&').forEach(function (kv) { var i = kv.indexOf('='); if (i > 0) p[kv.slice(0, i)] = decodeURIComponent(kv.slice(i + 1)); });
    if (p.q && question(B, p.q)) { var q = p.q; delete p.q; ask(q, p); }
  }

  function start() {
    thread = document.getElementById('ask-thread');
    status = document.getElementById('ask-status');
    B = JSON.parse(document.getElementById('ask-bank-data').textContent);
    var note = document.getElementById('ask-loading');
    note.hidden = false;
    fetch('/assets/ask/data.json').then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (d) {
      D = d;
      note.hidden = true;
      drawBank();
      document.getElementById('ask-form').hidden = false;
      document.getElementById('ask-form').addEventListener('submit', function (e) {
        e.preventDefault();
        var f = document.getElementById('ask-text');
        typed(f.value);
        f.value = '';
      });
      document.getElementById('ask-reset').addEventListener('click', function () {
        thread.innerHTML = ''; thread.hidden = true; this.hidden = true; status.textContent = 'The thread is cleared.';
        document.getElementById('ask-empty').hidden = false;
        try { history.replaceState(history.state, '', location.pathname); } catch (e) { /* ignore */ }
      });
      addEventListener('hashchange', fromHash);
      fromHash();
      document.documentElement.setAttribute('data-ask', 'ready');
    }).catch(function () {
      note.textContent = 'The figures could not be loaded, so no question can be answered here. The pages linked below show the same data.';
      document.documentElement.setAttribute('data-ask', 'failed');
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
}());
