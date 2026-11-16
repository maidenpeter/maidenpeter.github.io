"""The questions on /ask/, written once.

tools/build.py writes this bank into the page as JSON; assets/ask/ask.js draws a chip for each question and
computes its answer from assets/ask/data.json; tools/ask_answers.py computes the same answers in Python for
tools/check_ask.py. A question's text holds its slots in braces: {yr}, {y1}, {y2} (years), {ins} (insurer),
{cls} (class), {line} (a reserving line), {topic}.

Each slot names the list it is chosen from:
  years   full years with insurer totals        cyears   full years with class figures
  scyears years the cedant scorecard was run    gyears   years with a full year just before
  ins     insurers                              cls      classes
  line    the six US paid triangles             topic    the topics in ABOUT_TOPICS
kw: words that point a typed question at this one (lower case; a leading space marks a word start).
"""

GROUPS = [
    ("market", "The market"),
    ("insurer", "Any insurer"),
    ("reinsurer", "A reinsurer's view"),
    ("reserving", "Reserving"),
    ("about", "About Marion"),
]

QUESTIONS = [
    dict(id="class-range", g="market", t="Which class lost the most money from {y1} to {y2}, and which made the most?",
         slots=dict(y1="cyears", y2="cyears"),
         kw=["class", "classes", "lost the most", "made the most", "most money", "worst", "best", "lines of business"]),
    dict(id="uw-inv", g="market", t="How did the market's underwriting result compare with its investment income in {yr}?",
         slots=dict(yr="years"), kw=["investment", "operating result", "underwriting result", "investment income"]),
    dict(id="profit-count", g="market", t="How many insurers made an underwriting profit in {yr}?",
         slots=dict(yr="years"), kw=["how many", "profit", "profitable", "made money"]),
    dict(id="concentration", g="market", t="How concentrated was the market in {yr}?",
         slots=dict(yr="years"), kw=["concentrat", "herfindahl", "hhi", "10bn", "biggest insurers", "largest insurers", "top five"]),
    dict(id="motor-lr", g="market", t="What has motor's loss ratio been each year?",
         slots={}, kw=["motor", "loss ratio", "each year", "claims ratio"]),
    dict(id="ins-class-year", g="insurer", t="How did {ins} do on {cls} in {yr}?",
         slots=dict(ins="ins", cls="cls", yr="cyears"), kw=["how did", "do on", "perform", "class", "loss ratio"]),
    dict(id="ins-trend", g="insurer", t="What is {ins}'s trend from {y1} to {y2}?",
         slots=dict(ins="ins", y1="years", y2="years"), kw=["trend", "over time", "history", "from", "combined ratio"]),
    dict(id="ins-rank", g="insurer", t="Where did {ins} rank by premium in {yr}, and how has its share moved?",
         slots=dict(ins="ins", yr="years"), kw=["rank", "share", "position", "how big", "size", "largest"]),
    dict(id="ins-mix", g="insurer", t="Which classes did {ins} write the most of in {yr}?",
         slots=dict(ins="ins", yr="cyears"), kw=["mix", "write the most", "which classes", "business mix", "portfolio"]),
    dict(id="scorecard", g="reinsurer", t="Where did {ins} sit on the Cedant Scorecard in {yr}, and what drives its score?",
         slots=dict(ins="ins", yr="scyears"), kw=["scorecard", "grade", "score", "cedant", "rating", "pillar"]),
    dict(id="growth", g="reinsurer", t="Which insurers grew fastest in {yr}, and at what combined ratio?",
         slots=dict(yr="gyears"), kw=["grew", "growth", "fastest", "growing"]),
    dict(id="backtest", g="reinsurer", t="How did the scorecard rank insurers a year before the regulator acted?",
         slots={}, kw=["back-test", "backtest", "regulator", "statutory", "liquidation", "early warning", "failed"]),
    dict(id="tri-largest", g="reserving", t="Which line needs the largest reserve, and why?",
         slots={}, kw=["largest reserve", "biggest reserve", "most reserve", "which line"]),
    dict(id="tri-unpaid", g="reserving", t="How much of {line}'s ultimate is still unpaid?",
         slots=dict(line="line"), kw=["unpaid", "outstanding", "still to pay", "ultimate"]),
    dict(id="tri-sum", g="reserving", t="How do the six reserves add up, and how does that tie to the IFRS 17 case study?",
         slots={}, kw=["add up", "ifrs 17", "ifrs17", "total reserve", "six reserves", "tie"]),
    dict(id="about-done", g="about", t="Has she done {topic}?",
         slots=dict(topic="topic"), kw=["has she", "experience", "worked on", "done", "ibnr", "pricing", "reinsurance", "health"]),
    dict(id="about-tools", g="about", t="Which tools does she use: R, Python, SQL, Excel?",
         slots={}, kw=["tools", "python", "excel", "sql", " r ", "language", "software", "stack"]),
    dict(id="about-checks", g="about", t="How does she check her numbers?",
         slots={}, kw=["check", "validate", "verify", "trust", "accurate", "quality"]),
    dict(id="about-open", g="about", t="What has she built that I can open now?",
         slots={}, kw=["open", "live", "built", "apps", "demo", "links", "see"]),
    dict(id="about-contact", g="about", t="How do I contact her?",
         slots={}, kw=["contact", "email", "hire", "reach", "linkedin", "talk"]),
]

ABOUT_TOPICS = [
    ("ibnr", "IBNR reserving", ["ibnr", "reserving", "reserve"]),
    ("ifrs17", "IFRS 17", ["ifrs 17", "ifrs17", "ifrs"]),
    ("pricing", "pricing", ["pricing", "price", "rate"]),
    ("reinsurance", "reinsurance analysis", ["reinsurance", "reinsurer", "cedant"]),
    ("health", "health insurance", ["health", "medical"]),
]

# Words a typed question may use for a class or a reserving line, beyond their own names (lower case).
CLASS_WORDS = {
    "Motor Private": ["private motor", "private car", "motor private"],
    "Motor Commercial": ["commercial motor", "motor commercial", "psv", "matatu"],
    "Medical": ["medical", "health"],
    "Workmen's Compensation": ["workmen", "wiba", "work injury", "workers' compensation", "workers compensation"],
    "Fire Industrial": ["fire industrial", "industrial fire"],
    "Fire Domestic": ["fire domestic", "domestic fire", "home"],
    "Personal Accident": ["personal accident"],
    "Miscellaneous": ["miscellaneous", "misc"],
}
LINE_WORDS = {
    "Private motor": ["private motor", "private passenger"],
    "Commercial motor": ["commercial motor", "commercial auto"],
    "Workers' compensation": ["workers", "workmen", "work injury"],
    "Medical malpractice": ["malpractice", "medical"],
    "General liability": ["general liability"],
    "Product liability": ["product liability", "products"],
}

# Shown under every answer that names an insurer.
CAVEAT = "From the insurer's unaudited returns to the IRA. A screening view, not a credit opinion."

# The definitions the answers use, as the analysis repos write them: (term, definition, repo, file).
DEFINITIONS = [
    ("Full year", "The fourth-quarter return, year to date. 2017 is left out because IRA has no Q4 2017 workbook online.",
     "ira-kenya-data", "README.md"),
    ("Market", "Insurers only, micro insurers included, as IRA counts the market. Reinsurers are left out.",
     "ira-kenya-insurance", "src/profitability/build.py"),
    ("Written premium", "Gross direct premium plus inward reinsurance.", "ira-kenya-data", "README.md"),
    ("Net earned premium", "Net premium written plus reserves brought forward less reserves carried forward.",
     "ira-kenya-data", "docs/data_dictionary.md"),
    ("Incurred claims", "Net incurred claims.", "ira-kenya-data", "docs/data_dictionary.md"),
    ("Underwriting result", "Net earned premium less claims, commissions and expenses.", "ira-kenya-data", "docs/data_dictionary.md"),
    ("Investment income", "Investment income allocated to general business.", "ira-kenya-data", "docs/data_dictionary.md"),
    ("Loss ratio", "Incurred claims over net earned premium, where earned premium is positive.",
     "ira-kenya-insurance", "src/profitability/build.py"),
    ("Combined ratio", "Claims, commissions and management expenses over net earned premium.",
     "ira-kenya-data", "explorer/template.html"),
    ("Market share", "Written premium over the total of every insurer with positive written premium.",
     "ira-kenya-insurance", "src/structure/build.py"),
    ("Class", "The 13 classes of the Loss Map; Motor Commercial PSV is counted in Motor Commercial.",
     "ira-kenya-insurance", "src/profitability/build.py"),
    ("Grade", "Score bands: A 70 and above, B 55 to 70, C 40 to 55, D 25 to 40, E below 25. Negative equity, or equity under "
     "IRA's minimum capital, caps the grade at D.", "ira-kenya-reinsurance", "src/scorecard/score.py"),
    ("Bottom fifth", "A rank below 80% of the insurers scored that year.", "ira-kenya-reinsurance", "src/scorecard/backtest.py"),
    ("Reserve", "A volume-weighted chain ladder on the paid triangle: the projected ultimate less what has been paid.",
     "maidenpeter.github.io", "tools/build.py"),
]


def bank(about):
    """The JSON the page carries: groups, questions, topics, words, the caveat and the About answers."""
    return dict(groups=GROUPS, questions=QUESTIONS, topics=[[k, t, w] for k, t, w in ABOUT_TOPICS],
                classWords=CLASS_WORDS, lineWords=LINE_WORDS, caveat=CAVEAT, about=about)
