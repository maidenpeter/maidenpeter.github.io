"""The answers on /ask/, computed in Python: the twin of ENGINE in assets/ask/ask.js.

tools/check_ask.py runs both on the same questions and fails on any difference, and runs this one on figures
rebuilt straight from the processed tables. Keep the two in step: same sentences, same numbers, same order of
addition (so the floating point sums agree to the last bit).
"""
import math, re

MP, MC = "Motor Private", "Motor Commercial"
PILLARS = ["Balance sheet", "Operating performance", "Business profile", "Return quality"]
FLAGS = {
    "negative_equity": "negative equity", "below_capital_floor": "equity under IRA's minimum capital",
    "combined_ratio_above_110": "combined ratio above 110%", "three_underwriting_losses": "an underwriting loss in each of the last three years",
    "unreliable_return": "an unreliable return in the last three years", "low_retention": "retention under 25%",
}
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(" ")
SRC = dict(
    cls="IRA quarterly returns, full years (Q4 year to date), net of reinsurance. Insurers only, micro insurers included; Motor Commercial includes PSV.",
    tot="IRA quarterly returns, full years (Q4 year to date). Insurers only, micro insurers included.",
    sc="Kenya Cedant Scorecard, built from IRA's quarterly returns. Grades are relative screening measures, not credit ratings.",
    tri="NAIC Schedule P paid triangles for all US insurers, accident years 1988 to 1997 (CAS Loss Reserving Database). Volume-weighted chain ladder.",
)
LINK = dict(
    lossmap=["/ira-kenya-insurance/page/kenya-insurance-loss-map.html", "Open the Loss Map"],
    structure=["/ira-kenya-insurance/page/kenya-insurance-market-structure.html", "Open Market Structure"],
    scorecard=["/ira-kenya-reinsurance/page/kenya-cedant-scorecard.html", "Open the Cedant Scorecard"],
    explorer=["/ira-kenya-data/explorer/kenya-insurer-explorer.html", "Open the Insurer Explorer"],
    series=["/kenya-insurance/", "Read the Kenya series"],
    tri=["/#tri-h", "See the triangle worked out on the home page"],
    ifrs=["/work/ifrs17-measurement/", "Read the IFRS 17 case study"],
)


# ------------------------------------------------------------------ formatting (as ask.js)
def fix(v, dp, signed=False):
    p = 10 ** dp
    r = math.floor(abs(v) * p + 0.5)
    ip, fp = divmod(r, p)
    s = f"{ip:,}" + ("." + ("0000" + str(fp))[-dp:] if dp else "")
    return ("" if r == 0 else "-" if v < 0 else "+" if signed else "") + s


def money(k, signed=False):
    a = abs(k)
    if a >= 1e6:
        return "KSh " + fix(k / 1e6, 1, signed) + "bn"
    if a >= 1e4:
        return "KSh " + fix(k / 1e3, 0, signed) + "m"
    return "KSh " + fix(k / 1e3, 1, signed) + "m"


def usd(k):
    return "US$" + fix(k / 1e6, 2) + "bn" if abs(k) >= 1e6 else "US$" + fix(k / 1e3, 1) + "m"


def pct(r, signed=False):
    if r is None:
        return "n/a"
    if 0 < r < 0.0005:   # would print as 0.0%
        return "under 0.1%"
    return fix(r * 100, 1, signed) + "%"


def ordinal(n):
    t, u = n % 100, n % 10
    return str(n) + ("th" if 10 < t < 14 else "st" if u == 1 else "nd" if u == 2 else "rd" if u == 3 else "th")


def span(ys, all_):
    out, i = [], 0
    while i < len(ys):
        j = i
        while j + 1 < len(ys) and all_.index(ys[j + 1]) == all_.index(ys[j]) + 1:
            j += 1
        out.append(f"{ys[i]} to {ys[j]}" if j > i else str(ys[i]))
        i = j + 1
    return ", ".join(out)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def ssum(xs):
    v = 0
    for x in xs:
        v += x
    return v


def argmax(xs):
    b = 0
    for i in range(1, len(xs)):
        if xs[i] > xs[b]:
            b = i
    return b


def argmin(xs):
    b = 0
    for i in range(1, len(xs)):
        if xs[i] < xs[b]:
            b = i
    return b


# ------------------------------------------------------------------ the data
class Ctx:
    def __init__(self, D):
        self.by_id = {x["id"]: x for x in D["ins"]}
        sy = set()
        for id_ in D["sc"]:
            sy |= set(D["sc"][id_])
        self.scyears = sorted(int(y) for y in sy)
        self.gyears = [y for i, y in enumerate(D["years"]) if i > 0 and D["years"][i - 1] == y - 1]
        self.sorted = sorted(D["ins"], key=lambda x: x["s"].lower())


_CTX = {}


def ctx(D):
    if id(D) not in _CTX:
        _CTX[id(D)] = Ctx(D)
    return _CTX[id(D)]


def tot(D, id_, y):
    return D["tot"].get(id_, {}).get(y)


def cls(D, id_, y, ci):
    return D["cls"].get(id_, {}).get(y, {}).get(ci)


def active(D, id_, y):
    e = tot(D, id_, y)
    return bool(e) and any(v != 0 for v in e)


def sn(D, id_):
    return ctx(D).by_id[id_]["s"]


def cr(e):
    return (e[2] + e[3]) / e[1] if e[1] > 0 else None


def tot_sum(D, y, f):
    v = 0
    for x in D["ins"]:
        e = tot(D, x["id"], y)
        if e:
            v += e[f]
    return v


def cls_sum(D, ys, ci, f):
    v = 0
    for x in D["ins"]:
        for y in ys:
            e = cls(D, x["id"], y, ci)
            if e:
                v += e[f]
    return v


def missing(D, id_, y):
    s = sn(D, id_)
    if int(y) in D["nf"].get(id_, []):
        return f"{s} filed no Q4 return for {y}, so there is no full-year figure."
    if not tot(D, id_, y):
        return f"{s} does not appear in IRA's returns for {y}."
    if not active(D, id_, y):
        return f"{s} reported no business in {y}."
    return None


def has(D, id_):
    ys = [y for y in D["years"] if active(D, id_, str(y))]
    return f"It has full-year figures for {span(ys, D['years'])}." if ys else "It has no full-year figures in this data."


def merged_year(D, a):
    ys = [y for y in D["years"] if active(D, a, str(y))]
    i = D["years"].index(ys[-1])
    return D["years"][i + 1] if i + 1 < len(D["years"]) else D["years"][i] + 1


def merger_note(D, id_):
    into = [a for a in D["mg"] if D["mg"][a] == id_]
    if id_ in D["mg"]:
        return f"{sn(D, id_)} merged into {sn(D, D['mg'][id_])} in {merged_year(D, id_)}."
    if not into:
        return ""
    return "Figures are as filed. " + " and ".join(f"{sn(D, a)} merged into it in {merged_year(D, a)}" for a in into) + \
        ", so its figures include that business from then on."


def pro_forma(D, id_, y):
    v = 0
    e = tot(D, id_, y)
    if e and e[0] > 0:
        v += e[0]
    for a in D["mg"]:
        if D["mg"][a] == id_:
            f = tot(D, a, y)
            if f and f[0] > 0:
                v += f[0]
    return v


def largest(D):
    y = str(D["years"][-1])
    best, bv = None, 0
    for x in D["ins"]:
        e = tot(D, x["id"], y)
        if e and (best is None or e[0] > bv):
            best, bv = x["id"], e[0]
    return best


# ------------------------------------------------------------------ slots
def question(B, q):
    return next((Q for Q in B["questions"] if Q["id"] == q), None)


def choices(D, B, kind):
    c = ctx(D)
    ys = lambda l: [[str(y), str(y)] for y in l]
    if kind == "years":
        return ys(D["years"])
    if kind == "cyears":
        return ys(D["cyears"])
    if kind == "scyears":
        return ys(c.scyears)
    if kind == "gyears":
        return ys(c.gyears)
    if kind == "ins":
        return [[x["id"], x["s"]] for x in c.sorted]
    if kind == "cls":
        return [[slug(n), n] for n in D["classes"]]
    if kind == "line":
        return [[slug(t[0]), t[0]] for t in D["tri"]]
    if kind == "topic":
        return [[t[0], t[1]] for t in B["topics"]]
    return []


def defaults(D, B, q):
    Q, s = question(B, q), {}
    for k, kind in Q["slots"].items():
        ch = choices(D, B, kind)
        if kind == "ins":
            s[k] = largest(D)
        elif kind == "cls":
            s[k] = slug(MP)
        elif kind in ("line", "topic") or k == "y1":
            s[k] = ch[0][0]
        else:
            s[k] = ch[-1][0]
    return s


def normalize(D, B, q, s):
    Q, d, out = question(B, q), defaults(D, B, q), {}
    for k, kind in Q["slots"].items():
        ok = any(c[0] == str(s.get(k)) for c in choices(D, B, kind))
        out[k] = str(s[k]) if ok else d[k]
    if out.get("y1") and out.get("y2") and int(out["y1"]) > int(out["y2"]):
        out["y1"], out["y2"] = out["y2"], out["y1"]
    return out


def label(D, B, kind, v):
    return next((c[1] for c in choices(D, B, kind) if c[0] == v), v)


def title(D, B, q, s):
    Q = question(B, q)
    return re.sub(r"\{(\w+)\}", lambda m: label(D, B, Q["slots"][m.group(1)], s[m.group(1)]), Q["t"])


# ------------------------------------------------------------------ the answers
A = {}


def answer_for(name):
    def reg(f):
        A[name] = f
        return f
    return reg


@answer_for("class-range")
def _class_range(D, B, s, o):
    y1, y2 = int(s["y1"]), int(s["y2"])
    ys = [str(y) for y in D["cyears"] if y1 <= y <= y2]
    C = D["classes"]
    res = [cls_sum(D, ys, str(i), 3) for i in range(len(C))]
    lo, hi, total = argmin(res), argmax(res), ssum(res)
    when = str(y1) if y1 == y2 else f"{y1} to {y2}"
    o["say"].append((f"In {y1}" if y1 == y2 else f"From {y1} to {y2}") + f", {C[lo]} lost the most: an underwriting result of {money(res[lo], True)}.")
    o["say"].append(f"{C[hi]} made the most: {money(res[hi], True)}." if res[hi] > 0
                    else f"No class made an underwriting profit; the smallest loss was {C[hi]}, at {money(res[hi], True)}.")
    o["say"].append(f"All {len(C)} classes together: {money(total, True)}.")
    o["nums"] = [["worst", C[lo], money(res[lo], True)], ["best", C[hi], money(res[hi], True)], ["total", "All classes", money(total, True)]]
    order = sorted(range(len(C)), key=lambda i: (res[i], i))
    o["chart"] = dict(type="bars", title=f"Underwriting result by class, {when}, KSh bn")
    o["table"] = dict(head=["Class", "Underwriting result"], rows=[[C[i], money(res[i], True)] for i in order])
    o["src"], o["link"] = SRC["cls"], [LINK["lossmap"]]


@answer_for("uw-inv")
def _uw_inv(D, B, s, o):
    y = s["yr"]
    uw, inv = tot_sum(D, y, 4), tot_sum(D, y, 5)
    op = uw + inv
    o["say"].append(f"In {y} insurers " + (f"lost {money(-uw)}" if uw < 0 else f"made {money(uw)}") + " on underwriting and "
                    + (f"lost {money(-inv)} on" if inv < 0 else f"earned {money(inv)} from") + " investments.")
    o["say"].append(f"Investment income covered the underwriting loss, leaving an operating result of {money(op, True)}." if uw < 0 and op > 0
                    else f"Investment income did not cover the underwriting loss: the operating result was {money(op, True)}." if uw < 0
                    else f"The operating result was {money(op, True)}.")
    o["nums"] = [["uw", "Underwriting result", money(uw, True)], ["inv", "Investment income", money(inv)], ["op", "Operating result", money(op, True)]]
    ys = [str(z) for z in D["years"]]
    U, I = [tot_sum(D, z, 4) for z in ys], [tot_sum(D, z, 5) for z in ys]
    o["chart"] = dict(type="columns", title="Underwriting result and investment income, KSh bn")
    o["table"] = dict(head=["Year", "Underwriting result", "Investment income", "Operating result"],
                      rows=[[z, money(U[i], True), money(I[i]), money(U[i] + I[i], True)] for i, z in enumerate(ys)])
    o["src"], o["link"] = SRC["tot"], [LINK["series"], LINK["explorer"]]


def filed(D, y):
    u = []
    for x in D["ins"]:
        e = tot(D, x["id"], y)
        if e and e[4] != 0:
            u.append(e[4])
    return u


@answer_for("profit-count")
def _profit_count(D, B, s, o):
    y = s["yr"]
    u = filed(D, y)
    n, p = len(u), len([v for v in u if v > 0])
    o["say"].append(f"In {y}, {p} of the {n} insurers that filed a full year made an underwriting profit.")
    if n - p > 0:
        o["say"].append(f"The other {n - p} made a loss.")
    o["nums"] = [["profit", "Made a profit", str(p)], ["filed", "Filed a full year", str(n)], ["share", "Share in profit", pct(p / n if n else None)]]
    ys = [str(z) for z in D["years"]]
    P, N = [], []
    for z in ys:
        v = filed(D, z)
        N.append(len(v))
        P.append(len([w for w in v if w > 0]))
    o["chart"] = dict(type="columns", title="Insurers with an underwriting profit")
    o["table"] = dict(head=["Year", "Made a profit", "Filed a full year"], rows=[[z, str(P[i]), str(N[i])] for i, z in enumerate(ys)])
    o["src"], o["link"] = SRC["tot"], [LINK["explorer"]]


def conc(D, y):
    w = []
    for x in D["ins"]:
        e = tot(D, x["id"], y)
        if e and e[0] > 0:
            w.append(e[0])
    t = ssum(w)
    big = [v for v in w if v >= 1e7]
    top = sorted(w, reverse=True)[:5]
    h = 0
    for v in w:
        q = v / t
        h += q * q
    return dict(n=len(w), t=t, nb=len(big), bs=ssum(big) / t, top5=ssum(top) / t, hhi=h * 1e4)


@answer_for("concentration")
def _concentration(D, B, s, o):
    y = s["yr"]
    c = conc(D, y)
    o["say"].append(f"In {y}, no insurer wrote KSh 10bn or more; the market wrote {money(c['t'])}." if c["nb"] == 0
                    else f"In {y}, {c['nb']} of the {c['n']} insurers that wrote premium wrote KSh 10bn or more, and "
                    + ("it held " if c["nb"] == 1 else "together they held ") + f"{pct(c['bs'])} of the market's {money(c['t'])}.")
    o["say"].append(f"The five largest held {pct(c['top5'])}, and the Herfindahl index was {fix(c['hhi'], 0)}.")
    o["nums"] = [["nb", "Insurers at KSh 10bn or more", str(c["nb"])], ["bs", "Their share", pct(c["bs"])], ["top5", "Five largest", pct(c["top5"])],
                 ["hhi", "Herfindahl index", fix(c["hhi"], 0)], ["total", "Written premium", money(c["t"])]]
    ys = [str(z) for z in D["years"]]
    C = [conc(D, z) for z in ys]
    o["chart"] = dict(type="columns", title="Share of written premium held by insurers writing KSh 10bn or more")
    o["table"] = dict(head=["Year", "Insurers at KSh 10bn or more", "Their share", "Five largest", "Herfindahl index", "Written premium"],
                      rows=[[z, str(k["nb"]), pct(k["bs"]), pct(k["top5"]), fix(k["hhi"], 0), money(k["t"])] for z, k in zip(ys, C)])
    o["src"], o["link"] = SRC["tot"], [LINK["structure"]]


@answer_for("motor-lr")
def _motor_lr(D, B, s, o):
    ks = [str(D["classes"].index(MP)), str(D["classes"].index(MC))]
    ys = [str(y) for y in D["cyears"]]
    L, E, Cl = [], [], []
    for y in ys:
        c = e = 0
        for x in D["ins"]:
            for k in ks:
                f = cls(D, x["id"], y, k)
                if f:
                    c += f[2]
                    e += f[1]
        Cl.append(c)
        E.append(e)
        L.append(c / e if e > 0 else None)
    n, lo, hi = len(ys) - 1, argmin(L), argmax(L)
    o["say"].append(f"Motor's loss ratio, private and commercial together, was {pct(L[n])} in {ys[n]}.")
    o["say"].append(f"From {ys[0]} to {ys[n]} it ran from {pct(L[lo])} in {ys[lo]} to {pct(L[hi])} in {ys[hi]}.")
    o["nums"] = [["last", ys[n], pct(L[n])], ["low", f"Lowest, {ys[lo]}", pct(L[lo])], ["high", f"Highest, {ys[hi]}", pct(L[hi])]]
    o["chart"] = dict(type="columns", title="Motor loss ratio, private and commercial together")
    o["table"] = dict(head=["Year", "Loss ratio", "Net earned premium", "Incurred claims"],
                      rows=[[y, pct(L[i]), money(E[i]), money(Cl[i])] for i, y in enumerate(ys)])
    o["src"], o["link"] = SRC["cls"], [LINK["lossmap"]]


def _scale(vals):
    return ["bn", 1e6] if any(v is not None and abs(v) >= 1e6 for v in vals) else ["m", 1e3]


@answer_for("ins-class-year")
def _ins_class_year(D, B, s, o):
    id_, y = s["ins"], s["yr"]
    ci = str([slug(c) for c in D["classes"]].index(s["cls"]))
    C, S = D["classes"][int(ci)], sn(D, id_)
    o["cav"], o["link"], o["src"] = True, [LINK["explorer"], LINK["lossmap"]], SRC["cls"]
    miss = missing(D, id_, y)
    if miss:
        o["ok"] = False
        o["say"] += [miss, has(D, id_)]
        return
    e = cls(D, id_, y, ci)
    if not e:
        o["ok"] = False
        o["say"].append(f"{S} reported no {C} business in {y}.")
        g = []
        for i in range(len(D["classes"])):
            f = cls(D, id_, y, str(i))
            g.append(f[0] if f else 0)
        b = argmax(g)
        if g[b] > 0:
            o["say"].append(f"Its largest class that year was {D['classes'][b]}, with {money(g[b])} of gross premium.")
        return
    gp = e[0]
    lr = e[2] / e[1] if e[1] > 0 else None
    n = above = tie = 0
    mc = me = 0
    for x in D["ins"]:
        f = cls(D, x["id"], y, ci)
        if not f:
            continue
        mc += f[2]
        me += f[1]
        if f[0] > 0:
            n += 1
            if f[0] > gp:
                above += 1
            elif f[0] == gp and x["id"] != id_:
                tie += 1
    rank = above + 1 if gp > 0 else None
    mlr = mc / me if me > 0 else None
    o["say"].append(f"In {y} {S} wrote {money(gp)} of {C} gross premium"
                    + (f", {'joint ' if tie else ''}{ordinal(rank)} of the {n} insurers writing the class." if rank else "."))
    o["say"].append(f"Its loss ratio was {pct(lr)}, against {pct(mlr)} for the market, and its underwriting result was {money(e[3], True)}." if lr is not None
                    else f"It had no positive net earned premium in the class, so it has no loss ratio; its underwriting result was {money(e[3], True)}.")
    o["nums"] = [["gp", "Gross premium", money(gp)], ["lr", "Loss ratio", pct(lr)], ["uw", "Underwriting result", money(e[3], True)],
                 ["rank", "Rank in the class", f"{'joint ' if tie else ''}{rank} of {n}" if rank else "n/a"], ["mlr", "Market loss ratio", pct(mlr)]]
    ys = [str(z) for z in D["cyears"]]
    sc = _scale([(cls(D, id_, z, ci) or [None] * 4)[3] for z in ys])
    o["chart"] = dict(type="columns", title=f"{S}, {C}: underwriting result, KSh {sc[0]}")
    rows = []
    for z in ys:
        f = cls(D, id_, z, ci)
        if f:
            rows.append([z, money(f[0]), pct(f[2] / f[1] if f[1] > 0 else None), money(f[3], True)])
    o["table"] = dict(head=["Year", "Gross premium", "Loss ratio", "Underwriting result"], rows=rows)


@answer_for("ins-trend")
def _ins_trend(D, B, s, o):
    id_, y1, y2 = s["ins"], int(s["y1"]), int(s["y2"])
    S = sn(D, id_)
    ys = [str(y) for y in D["years"] if y1 <= y <= y2]
    act = [y for y in ys if active(D, id_, y)]
    o["cav"], o["link"], o["src"] = True, [LINK["explorer"]], SRC["tot"]
    if not act:
        o["ok"] = False
        o["say"] += [f"{S} has no full-year figures from {y1} to {y2}.", has(D, id_)]
        return
    E = [tot(D, id_, y) for y in act]
    f, l, ef, el = act[0], act[-1], E[0], E[-1]
    uws = [e[4] for e in E]
    total, nl = ssum(uws), len([v for v in uws if v < 0])
    o["say"].append(f"In {f} {S} wrote {money(ef[0])} of premium." if f == l
                    else f"{S}'s written premium went from {money(ef[0])} in {f} to {money(el[0])} in {l}.")
    o["say"].append(f"Its combined ratio was {pct(cr(ef))} in {f}" + (f" and {pct(cr(el))} in {l}" if f != l else "") + ".")
    o["say"].append(f"Its underwriting result was {money(total, True)}." if f == l
                    else f"Its underwriting result over those {len(act)} years added up to {money(total, True)}, with a loss in {nl} of them.")
    gaps = [int(y) for y in ys if y not in act]
    nfg = [y for y in gaps if y in D["nf"].get(id_, [])]
    if gaps:
        o["say"].append(f"No full-year figures for {span(gaps, D['years'])}" + (f"; it filed no Q4 return for {span(nfg, D['years'])}" if nfg else "") + ".")
    o["nums"] = [["wp1", f"Written premium, {f}", money(ef[0])], ["wp2", f"Written premium, {l}", money(el[0])],
                 ["cr1", f"Combined ratio, {f}", pct(cr(ef))], ["cr2", f"Combined ratio, {l}", pct(cr(el))],
                 ["uw", "Underwriting result, total", money(total, True)], ["nl", "Years with a loss", f"{nl} of {len(act)}"]]
    o["chart"] = dict(type="columns", title=f"{S}: underwriting result, KSh {_scale(uws)[0]}")
    o["table"] = dict(head=["Year", "Written premium", "Combined ratio", "Underwriting result"],
                      rows=[[y, money(e[0]), pct(cr(e)), money(e[4], True)] for y, e in zip(act, E)])


def rank_in(D, y, id_):
    w, mine = [], None
    for x in D["ins"]:
        e = tot(D, x["id"], y)
        if e and e[0] > 0:
            w.append(e[0])
            if x["id"] == id_:
                mine = e[0]
    if mine is None:
        return None
    above, same = len([v for v in w if v > mine]), len([v for v in w if v == mine])
    return [above + 1, len(w), same > 1, mine / ssum(w), mine]


@answer_for("ins-rank")
def _ins_rank(D, B, s, o):
    id_, y = s["ins"], s["yr"]
    S = sn(D, id_)
    o["cav"], o["link"], o["src"] = True, [LINK["structure"], LINK["explorer"]], SRC["tot"]
    r = rank_in(D, y, id_)
    if not r:
        o["ok"] = False
        o["say"] += [missing(D, id_, y) or f"{S} wrote no premium in {y}.", has(D, id_)]
        return
    o["say"].append(f"In {y} {S} was {'joint ' if r[2] else ''}{ordinal(r[0])} of the {r[1]} insurers by written premium, with "
                    f"{pct(r[3])} of the market ({money(r[4])}).")
    ys = [str(z) for z in D["years"]]
    R = [rank_in(D, z, id_) for z in ys]
    have = [z for z, k in zip(ys, R) if k]
    fi, li = ys.index(have[0]), ys.index(have[-1])
    if fi != li:
        o["say"].append(f"Its share was {pct(R[fi][3])} in {ys[fi]} and {pct(R[li][3])} in {ys[li]}.")
    o["nums"] = [["rank", "Rank by written premium", f"{'joint ' if r[2] else ''}{r[0]} of {r[1]}"], ["share", "Market share", pct(r[3])],
                 ["wp", "Written premium", money(r[4])], ["s1", f"Share, {ys[fi]}", pct(R[fi][3])], ["s2", f"Share, {ys[li]}", pct(R[li][3])]]
    o["chart"] = dict(type="columns", title=f"{S}: share of written premium")
    o["table"] = dict(head=["Year", "Rank", "Market share", "Written premium"],
                      rows=[[z, f"{'joint ' if k[2] else ''}{k[0]} of {k[1]}", pct(k[3]), money(k[4])] for z, k in zip(ys, R) if k])


@answer_for("ins-mix")
def _ins_mix(D, B, s, o):
    id_, y = s["ins"], s["yr"]
    S = sn(D, id_)
    o["cav"], o["link"], o["src"] = True, [LINK["explorer"]], SRC["cls"]
    miss = missing(D, id_, y)
    if miss:
        o["ok"] = False
        o["say"] += [miss, has(D, id_)]
        return
    it = []
    for i in range(len(D["classes"])):
        f = cls(D, id_, y, str(i))
        if f and f[0] > 0:
            it.append([i, f[0]])
    if not it:
        o["ok"] = False
        o["say"].append(f"{S} reported no gross premium by class in {y}.")
        return
    t = ssum([v[1] for v in it])
    it.sort(key=lambda v: (-v[1], v[0]))
    nm = lambda k: D["classes"][it[k][0]]
    sh = lambda k: pct(it[k][1] / t)
    o["say"].append(f"In {y} {S}'s largest class was {nm(0)}, with {sh(0)} of its gross premium ({money(it[0][1])}).")
    if len(it) >= 3:
        o["say"].append(f"Next came {nm(1)} ({sh(1)}) and {nm(2)} ({sh(2)}).")
    elif len(it) == 2:
        o["say"].append(f"Next came {nm(1)} ({sh(1)}).")
    o["say"].append(f"It wrote {len(it)} of the {len(D['classes'])} classes.")
    o["nums"] = [[f"c{k + 1}", nm(k), sh(k)] for k in range(min(3, len(it)))] + [["k", "Classes written", str(len(it))]]
    o["chart"] = dict(type="dots", title=f"{S}: share of gross premium by class, {y}")
    o["table"] = dict(head=["Class", "Gross premium", "Share"], rows=[[D["classes"][v[0]], money(v[1]), pct(v[1] / t)] for v in it])


@answer_for("scorecard")
def _scorecard(D, B, s, o):
    id_, y = s["ins"], s["yr"]
    S = sn(D, id_)
    r = D["sc"].get(id_, {}).get(y)
    o["cav"], o["link"], o["src"] = True, [LINK["scorecard"]], SRC["sc"]
    if not r:
        o["ok"] = False
        why = D["ns"].get(id_, {}).get(y)
        o["say"].append(f"{S} was not scored in {y}: {why}." if why else f"{S} is not in the scorecard for {y}.")
        gs = [f"{z} {g[0]}" for z, g in sorted(D["sc"].get(id_, {}).items(), key=lambda kv: int(kv[0]))]
        if gs:
            o["say"].append(f"Its grades in the years it was scored: {', '.join(gs)}.")
        return
    p, fl = r[5:9], (r[9].split(";") if r[9] else [])
    o["say"].append(f"In {y} {S} scored {fix(r[4], 1)} out of 100 and was graded {r[0]}, {ordinal(r[2])} of the {r[3]} insurers scored.")
    av = [i for i in range(4) if p[i] is not None]
    if len(av) > 1:
        hi = lo = av[0]
        for i in av:
            if p[i] > p[hi]:
                hi = i
            if p[i] < p[lo]:
                lo = i
        o["say"].append(f"Its strongest pillar was {PILLARS[hi]} ({fix(p[hi], 1)}), its weakest {PILLARS[lo]} ({fix(p[lo], 1)}).")
    cap = "negative_equity" if "negative_equity" in fl else "below_capital_floor"
    if r[0] != r[1]:
        o["say"].append(f"The score alone would give {r[1]}; {FLAGS[cap]} caps the grade at D.")
    rest = [f for f in fl if r[0] == r[1] or f != cap]
    if rest:
        o["say"].append(("Other watch flags: " if r[0] != r[1] else "Watch flags: ") + "; ".join(FLAGS.get(f, f) for f in rest) + ".")
    o["nums"] = [["grade", "Grade", r[0]], ["rank", "Rank", f"{r[2]} of {r[3]}"], ["score", "Score", fix(r[4], 1)]] + \
                [[f"p{i}", PILLARS[i], "n/a" if v is None else fix(v, 1)] for i, v in enumerate(p)]
    o["chart"] = dict(type="dots", title=f"{S}: scorecard pillars, {y}, out of 100")
    o["table"] = dict(head=["Pillar", "Score"], rows=[[PILLARS[i], "n/a" if v is None else fix(v, 1)] for i, v in enumerate(p)] + [["Total score", fix(r[4], 1)]])


@answer_for("growth")
def _growth(D, B, s, o):
    y = s["yr"]
    p = str(int(y) - 1)
    it, A0, A1 = [], 0, 0
    for k, x in enumerate(D["ins"]):
        a, b = tot(D, x["id"], p), tot(D, x["id"], y)
        if a and a[0] > 0:
            A0 += a[0]
        if b and b[0] > 0:
            A1 += b[0]
        if x["id"] in D["mg"]:
            continue
        pa, pb = pro_forma(D, x["id"], p), pro_forma(D, x["id"], y)
        if a and a[0] > 0 and b and b[0] > 0 and pa >= 5e5:
            it.append([k, pb / pa - 1, cr(b), pb, x["id"]])
    o["cav"], o["link"], o["src"] = True, [LINK["structure"]], SRC["tot"]
    it.sort(key=lambda v: (-v[1], v[0]))
    top = it[:5]
    mg = A1 / A0 - 1 if A0 > 0 else None
    if not top:
        o["ok"] = False
        o["say"].append(f"No insurer had KSh 500m of premium in {p} and premium in {y}.")
        return
    o["say"].append(f"In {y} the fastest growth among insurers with at least KSh 500m of premium in {p} was {sn(D, top[0][4])}'s: "
                    f"{pct(top[0][1], True)}, at a combined ratio of {pct(top[0][2])}.")
    o["say"].append(f"The market's written premium changed by {pct(mg, True)}. Companies that merged are counted together in both years, as on the Market Structure page.")
    k = len([t for t in top if t[2] is not None and t[2] > 1])
    o["say"].append(f"Of these {len(top)}, {k} wrote at a combined ratio above 100%, that is at an underwriting loss.")
    o["nums"] = []
    for i, t in enumerate(top):
        o["nums"] += [[f"g{i + 1}", sn(D, t[4]), pct(t[1], True)], [f"cr{i + 1}", sn(D, t[4]) + ", combined ratio", pct(t[2])]]
    o["nums"].append(["mg", "Market", pct(mg, True)])
    o["chart"] = dict(type="dots", title=f"Growth in written premium, {p} to {y}")
    o["table"] = dict(head=["Insurer", "Growth", "Combined ratio", "Written premium"],
                      rows=[[sn(D, t[4]), pct(t[1], True), pct(t[2]), money(t[3])] for t in top])


@answer_for("backtest")
def _backtest(D, B, s, o):
    R = D["bt"]
    n, nb = len(R), len([b for b in R if b[7]])
    yrs = [int(b[2][:4]) for b in R]
    ev = []
    for b in R:
        if b[1] not in ev:
            ev.append(b[1])
    mon = lambda d: MONTHS[int(d[5:7]) - 1] + " " + d[:4]
    o["say"].append(f"The regulator acted on {n} insurers between {min(yrs)} and {max(yrs)}: {' or '.join(ev)}.")
    o["say"].append(f"{nb} of them were in the bottom fifth of the scorecard in their last scored year before it acted.")
    for b in R:
        if not b[7]:
            o["say"].append(f"{sn(D, b[0])} was {ordinal(b[5])} of {b[6]} in {b[3]}." + (f" It was not scored after that: {b[8]}." if b[8] else ""))
    o["nums"] = [["bottom", "In the bottom fifth", f"{nb} of {n}"]]
    o["chart"] = dict(type="dots", title="Place in the table in the last scored year, top to bottom")
    o["table"] = dict(head=["Insurer", "Regulator acted", "Last scored", "Grade", "Rank", "Bottom fifth"],
                      rows=[[sn(D, b[0]), f"{b[1]}, {mon(b[2])}", str(b[3]), b[4], f"{b[5]} of {b[6]}", "Yes" if b[7] else "No"] for b in R])
    o["cav"], o["link"], o["src"] = True, [LINK["scorecard"]], SRC["sc"]


@answer_for("tri-largest")
def _tri_largest(D, B, s, o):
    T = D["tri"]
    res, ult = [t[3] for t in T], [t[2] for t in T]
    un = [t[3] / t[2] for t in T]
    L, U, Sx, total = argmax(res), argmax(ult), argmax(un), ssum(res)
    o["say"].append(f"{T[L][0]} needs the largest reserve: {usd(res[L])} of the six lines' {usd(total)}.")
    o["say"].append(f"It is also the largest line, with {usd(ult[L])} of ultimate claims, of which {pct(un[L])} is still unpaid." if L == U
                    else f"It is not the largest line by ultimate claims ({T[U][0]} is); {pct(un[L])} of its {usd(ult[L])} ultimate is still unpaid.")
    if Sx != L:
        o["say"].append(f"{T[Sx][0]} has the largest share still unpaid, {pct(un[Sx])}, but its ultimate is "
                        f"{'smaller' if ult[Sx] < ult[L] else 'larger'}: {usd(ult[Sx])}.")
    o["say"].append("A reserve is the ultimate less what has been paid, so it is large where a line is large or slow to pay.")
    o["nums"] = [["line", T[L][0], usd(res[L])], ["total", "Six lines", usd(total)], ["ult", "Its ultimate", usd(ult[L])],
                 ["un", "Its share unpaid", pct(un[L])], ["slow", f"{T[Sx][0]}, share unpaid", pct(un[Sx])]]
    order = sorted(range(len(T)), key=lambda i: (-res[i], i))
    o["chart"] = dict(type="dots", title="Reserve by line, US$bn")
    o["table"] = dict(head=["Line", "Paid to date", "Ultimate", "Reserve", "Share unpaid"],
                      rows=[[T[i][0], usd(T[i][1]), usd(ult[i]), usd(res[i]), pct(un[i])] for i in order])
    o["src"], o["link"] = SRC["tri"], [LINK["tri"], LINK["ifrs"]]


@answer_for("tri-unpaid")
def _tri_unpaid(D, B, s, o):
    t = D["tri"][[slug(x[0]) for x in D["tri"]].index(s["line"])]
    o["say"].append(f"Of {t[0]}'s {usd(t[2])} of ultimate claims, {usd(t[3])} is still unpaid: {pct(t[3] / t[2])}.")
    o["say"].append(f"{usd(t[1])} has been paid to date.")
    o["nums"] = [["ult", "Ultimate", usd(t[2])], ["res", "Still unpaid", usd(t[3])], ["un", "Share unpaid", pct(t[3] / t[2])], ["paid", "Paid to date", usd(t[1])]]
    o["chart"] = dict(type="split", title=f"{t[0]}: paid and unpaid, US$")
    o["table"] = dict(head=["", "Amount"], rows=[["Paid to date", usd(t[1])], ["Still unpaid", usd(t[3])], ["Ultimate", usd(t[2])]])
    o["src"], o["link"] = SRC["tri"], [LINK["tri"]]


@answer_for("tri-sum")
def _tri_sum(D, B, s, o):
    T, i17 = D["tri"], D["i17"]
    res = [t[3] for t in T]
    total, L = ssum(res), argmax(res)
    o["say"].append(f"The six chain ladder reserves add up to {usd(total)}, {pct(res[L] / total)} of it in {T[L][0]}.")
    o["say"].append("That is the undiscounted reserve the IFRS 17 case study starts from." if fix(total / 1e6, 2) == fix(i17[0], 2)
                    else f"The IFRS 17 case study starts from US${fix(i17[0], 2)}bn.")
    o["say"].append(f"Discounting at {fix(i17[2], 1)}% takes US${fix(-i17[1], 2)}bn off it, and a risk adjustment at the 75th percentile adds US${fix(i17[3], 0)}m.")
    o["nums"] = [["total", "Six reserves", usd(total)], ["case", "IFRS 17 case study, undiscounted", f"US${fix(i17[0], 2)}bn"],
                 ["disc", "Discounting", f"US${fix(i17[1], 2)}bn"], ["ra", "Risk adjustment, 75th percentile", f"US${fix(i17[3], 0)}m"]]
    order = sorted(range(len(T)), key=lambda i: (-res[i], i))
    o["chart"] = dict(type="dots", title="Reserve by line, US$bn")
    o["table"] = dict(head=["Line", "Reserve"], rows=[[T[i][0], usd(res[i])] for i in order] + [["Six lines", usd(total)]])
    o["src"], o["link"] = SRC["tri"], [LINK["ifrs"], LINK["tri"]]


def _about(o, item):
    o["say"].append(item["lead"])
    o["points"] = item["points"]


@answer_for("about-done")
def _about_done(D, B, s, o):
    _about(o, B["about"]["about-done"][s["topic"]])


for _q in ("about-tools", "about-checks", "about-open", "about-contact"):
    A[_q] = (lambda q: lambda D, B, s, o: _about(o, B["about"][q]))(_q)


def answer(D, B, q, s0=None):
    if not question(B, q) or q not in A:
        return None
    s = normalize(D, B, q, s0 or {})
    o = dict(q=q, slots=s, title=title(D, B, q, s), ok=True, say=[], nums=[], points=None, chart=None, table=None,
             src="", link=[], cav=False, note="")
    A[q](D, B, s, o)
    if s.get("ins"):
        m = merger_note(D, s["ins"])
        o["note"] = (m + " " if m else "") + "Names in IRA's returns: " + "; ".join(ctx(D).by_id[s["ins"]]["a"]) + "."
    return o
