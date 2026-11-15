"""Charts for maidenpeter.github.io, written as plain HTML and CSS.

No JavaScript and no images: each chart reflows on a phone, follows the ink and paper themes
through the tokens in assets/site.css, and prints. Styles are in assets/viz.css.

Colour does one job per chart. Teal (--gain) and oxblood (--loss) carry polarity: profit or
loss, fine or in trouble. A dimmed grey (--vz-ctx) carries context behind the marks the story
is about. A neutral (--vz-neu) carries a single series with no polarity. Gold is for
annotation only, never a data series (it fails the lightness band on ink).

Every chart has a title, a one-line summary for screen readers (role="img"), a table of its
numbers behind "Show the numbers", and a source line. Each mark also has a title attribute,
so hovering shows its value; nothing depends on hover.
"""
from html import escape
from math import floor, log10


def esc(s):
    return escape(str(s), quote=True)


def nice_ticks(lo, hi, n=4):
    """Round tick values covering lo..hi, always including zero when the range spans it."""
    span = (hi - lo) or abs(hi) or 1
    raw = span / n
    mag = 10 ** floor(log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    start = floor(lo / step) * step
    ticks, t = [], start
    while t < hi + step * 0.999:
        ticks.append(round(t, 10))
        t += step
    return ticks


def figure(title, plot, sub="", key="", table="", note="", cls=""):
    """A chart panel: title, subtitle, the plot, its key, its numbers and its source."""
    return (f'<figure class="panel vz{(" " + cls) if cls else ""}"><h3>{title}</h3>'
            + (f'<p class="vz-sub">{sub}</p>' if sub else "") + plot + key + table
            + (f'<figcaption class="vz-note">{note}</figcaption>' if note else "") + "</figure>")


def key(items):
    """Legend: (mark class, text). Always shown for two or more series."""
    return '<ul class="vz-key">' + "".join(f'<li><i class="{c}"></i>{t}</li>' for c, t in items) + "</ul>"


def table(head, rows, summary="Show the numbers"):
    """The table view behind every chart. head: column titles; rows: lists of cell text."""
    th = "".join(f'<th scope="col">{h}</th>' for h in head)
    tr = "".join("<tr>" + "".join((f'<th scope="row">{c}</th>' if i == 0 else f"<td>{c}</td>") for i, c in enumerate(r)) + "</tr>"
                 for r in rows)
    return (f'<details class="vz-tab"><summary>{summary}</summary><div class="vz-scroll">'
            f'<table class="data"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div></details>')


def columns(cats, series, label, fmt, tick_fmt=None, ticks=None, height=220, marks=None):
    """Vertical columns on one shared zero baseline; values may be negative (a diverging column chart).

    cats: category labels along the bottom. series: (mark class, series name, values), values aligned
    with cats, None for no bar. A mark class of "sign" colours each bar by its sign (teal up, oxblood
    down); a list of classes sets one per bar (to pick out the bar the story is about).
    marks: {(series index, category index): text} printed at the bar's tip, used sparingly."""
    vals = [v for _, _, vs in series for v in vs if v is not None]
    lo, hi = min(0, min(vals)), max(0, max(vals))
    ticks = list(ticks or nice_ticks(lo, hi))
    lo, hi = min(lo, ticks[0]), max(hi, ticks[-1])
    # leave room for a tip label near either end of the scale, so it never meets the axis text
    step = ticks[1] - ticks[0] if len(ticks) > 1 else (hi - lo) or 1
    for si, ci in (marks or {}):
        v = series[si][2][ci]
        if v is not None and v < 0 and (v - lo) / (hi - lo) < 0.12:
            ticks.insert(0, ticks[0] - step)
            lo = ticks[0]
        if v is not None and v > 0 and (hi - v) / (hi - lo) < 0.12:
            ticks.append(ticks[-1] + step)
            hi = ticks[-1]
    span = hi - lo
    tick_fmt = tick_fmt or fmt

    def y(v):
        return (hi - v) / span * 100

    grid = "".join(f'<span class="vz-tick{" z" if t == 0 else ""}" style="top:{y(t):.2f}%"><b>{tick_fmt(t)}</b></span>' for t in ticks)
    groups = []
    for ci, c in enumerate(cats):
        lanes = []
        for si, (cls, name, vs) in enumerate(series):
            v = vs[ci]
            if v is None:
                lanes.append('<span class="vz-lane"></span>')
                continue
            up = v >= 0
            top, h = (y(v), y(0) - y(v)) if up else (y(0), y(v) - y(0))
            mc = cls[ci] if isinstance(cls, list) else ("pos" if up else "neg") if cls == "sign" else cls
            lab = (marks or {}).get((si, ci))
            lanes.append(f'<span class="vz-lane"><i class="vz-col {mc} {"up" if up else "dn"}" style="top:{top:.2f}%;height:{max(h, 0.6):.2f}%" '
                         f'title="{esc(f"{name}, {c}: {fmt(v)}")}">' + (f"<em>{lab}</em>" if lab else "") + "</i></span>")
        groups.append(f'<span class="vz-g">{"".join(lanes)}</span>')
    # a four-digit year shortens to '16 on a phone, so nine years fit side by side
    xl = "".join(f'<span><b class="f">{esc(c)}</b><b class="s">{esc(chr(39) + c[2:] if len(c) == 4 and c.isdigit() else c)}</b></span>' for c in cats)
    return (f'<div class="vz-colchart" style="--h:{height}px"><div class="vz-plot" role="img" aria-label="{esc(label)}">{grid}'
            f'<div class="vz-gs">{"".join(groups)}</div></div><div class="vz-x" aria-hidden="true">{xl}</div></div>')


def dotrows(rows, lo, hi, ticks, tick_fmt, label, band=None, rule=None):
    """One row per entity, dots on a shared horizontal axis.

    rows: (name, note, [(value, mark class, hover text, label or "")]). band: (from, to, text), a shaded
    reference range drawn in every row. rule: (value, text), a reference line such as a threshold."""
    def x(v):
        return (v - lo) / (hi - lo) * 100

    under = "".join(f'<span class="vz-vt" style="left:{x(t):.2f}%"></span>' for t in ticks)
    if band:
        under += f'<span class="vz-band" style="left:{x(band[0]):.2f}%;width:{x(band[1]) - x(band[0]):.2f}%"></span>'
    if rule:
        under += f'<span class="vz-rule" style="left:{x(rule[0]):.2f}%"></span>'
    out = []
    for name, note, dots in rows:
        pos = ' class="r"' if len(dots) == 1 else ""   # a lone dot carries its label to the right
        ds = "".join(f'<i class="vz-dot {c}" style="left:{x(v):.2f}%" title="{esc(tip)}">' + (f"<b{pos}>{lab}</b>" if lab else "") + "</i>"
                     for v, c, tip, lab in dots)
        out.append(f'<div class="vz-row"><span class="vz-name">{name}' + (f"<small>{note}</small>" if note else "")
                   + f'</span><span class="vz-track">{under}{ds}</span></div>')
    axis = "".join(f'<span class="{"o" if i % 2 else ""}" style="left:{x(t):.2f}%">{tick_fmt(t)}</span>' for i, t in enumerate(ticks))
    tops = ""
    if band:
        tops += f'<span class="vz-bandlab" style="left:{x((band[0] + band[1]) / 2):.2f}%">{band[2]}</span>'
    if rule:
        tops += f'<span class="vz-rulelab" style="left:{x(rule[0]):.2f}%">{rule[1]}</span>'
    return (f'<div class="vz-dots" role="img" aria-label="{esc(label)}"><div class="vz-row vz-top" aria-hidden="true"><span></span><span class="vz-track">{tops}</span></div>'
            + "".join(out) + f'<div class="vz-row vz-axis" aria-hidden="true"><span></span><span class="vz-track">{axis}</span></div></div>')


def scatter(points, xr, yr, xticks, yticks, xfmt, yfmt, xlab, ylab, label, xref=None, yref=None, quads=(), height=380):
    """Dots on two axes. points: (x, y, mark class, hover text, label, where) where 'where' places the
    label: r, l, t, b, tr, tl, br, bl; a trailing '*' keeps the label on small screens too.
    xref, yref: (value, text) reference lines. quads: (corner, text) with corner tl, tr, bl, br."""
    def px(v):
        return (v - xr[0]) / (xr[1] - xr[0]) * 100

    def py(v):
        return (v - yr[0]) / (yr[1] - yr[0]) * 100

    g = "".join(f'<span class="vz-gx" style="left:{px(t):.2f}%"><b class="{"o" if i % 2 else ""}">{xfmt(t)}</b></span>' for i, t in enumerate(xticks))
    g += "".join(f'<span class="vz-gy" style="bottom:{py(t):.2f}%"><b>{yfmt(t)}</b></span>' for t in yticks)
    if xref:
        g += f'<span class="vz-refx" style="left:{px(xref[0]):.2f}%"><b>{xref[1]}</b></span>'
    if yref:
        g += f'<span class="vz-refy" style="bottom:{py(yref[0]):.2f}%"><b>{yref[1]}</b></span>'
    g += "".join(f'<span class="vz-quad {c}">{t}</span>' for c, t in quads)
    dots = []
    for x, y, c, tip, lab, where in points:
        keep = where.endswith("*")
        where = where.rstrip("*")
        dots.append(f'<i class="vz-pt {c}" style="left:{px(x):.2f}%;bottom:{py(y):.2f}%" title="{esc(tip)}">'
                    + (f'<b class="{where}{" keep" if keep else ""}">{lab}</b>' if lab else "") + "</i>")
    return (f'<div class="vz-sc"><p class="vz-ylab" aria-hidden="true">{ylab}</p>'
            f'<div class="vz-plot" style="--h:{height}px" role="img" aria-label="{esc(label)}">{g}{"".join(dots)}</div>'
            f'<p class="vz-xlab" aria-hidden="true">{xlab}</p></div>')


def grades(rows, cols, label):
    """A table of grades by year, one row per insurer. rows: (name, note, {col: (cell class, text, hover)}).
    Cell classes: g-A to g-E for grades, nr for no full-year return, act for the regulator stepping in.
    A row with name None draws a divider labelled by note."""
    th = "".join(f'<th scope="col"><span class="f">{c}</span><span class="s">{chr(39) + c[2:] if len(c) == 4 and c.isdigit() else c}</span></th>' for c in cols)
    body = []
    for name, note, cells in rows:
        if name is None:
            body.append(f'<tr class="vz-div"><th scope="rowgroup" colspan="{len(cols) + 1}">{note}</th></tr>')
            continue
        tds = []
        for c in cols:
            cl, text, tip = cells.get(c, ("", "", ""))
            tds.append(f'<td class="{cl}"' + (f' title="{esc(tip)}"' if tip else "") + f">{text}</td>")
        body.append(f'<tr><th scope="row">{name}' + (f"<small>{note}</small>" if note else "") + "</th>" + "".join(tds) + "</tr>")
    return (f'<div class="vz-scroll"><table class="vz-grades"><caption class="vz-sr">{esc(label)}</caption>'
            f'<thead><tr><th scope="col"><span class="vz-sr">Insurer</span></th>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')


def split(parts, label, total=None):
    """One whole split into parts (the tall segmented bar). parts: (mark class, name, value, text printed
    inside or ""). Widths are proportional; the legend names the parts in order."""
    total = total or sum(v for _, _, v, _ in parts)

    def fits(v, t):   # print a label inside only when the part is wide enough for it; the legend carries every value
        return t and v / total * 100 >= 2.4 * len(t) + 4

    seg = "".join(f'<span class="vz-seg {c}" style="flex:{v / total * 100:.3f} 1 0" title="{esc(f"{n}: {t or v}")}">'
                  + (f"<b>{t}</b>" if fits(v, t) else "") + "</span>" for c, n, v, t in parts)
    return f'<div class="vz-split" role="img" aria-label="{esc(label)}">{seg}</div>'


def timeline(groups, years, label):
    """Items on a shared row of years, one row per item, drawn to the year.

    groups: (group name, [(title, note, first year, last year, mark)]). mark "bar" spans first to last year;
    "dot" marks a single year (a qualification); "ring" marks a single year as an annotation (a placing).
    The note carries the exact dates, so the drawing never claims more precision than the source has."""
    cols = len(years)
    head = "".join(f"<span>{y}</span>" for y in years)
    rows = []
    for name, items in groups:
        rows.append(f'<div class="vz-tl-group">{name}</div>')
        for title, note, a, b, mark in items:
            i, j = years.index(a) + 1, years.index(b) + 2
            m = (f'<i class="vz-tl-bar" style="grid-column:{i} / {j}" title="{esc(f"{title}: {note}")}"></i>' if mark == "bar" else
                 f'<i class="vz-tl-pt {mark}" style="grid-column:{i} / {i + 1}" title="{esc(f"{title}: {note}")}"></i>')
            rows.append(f'<div class="vz-tl-row"><span class="vz-tl-name">{title}<small>{note}</small></span>'
                        f'<span class="vz-tl-track" style="--n:{cols}">{m}</span></div>')
    return (f'<div class="vz-tl" role="img" aria-label="{esc(label)}">'
            f'<div class="vz-tl-row vz-tl-head" aria-hidden="true"><span></span><span class="vz-tl-track" style="--n:{cols}">{head}</span></div>'
            + "".join(rows) + "</div>")
