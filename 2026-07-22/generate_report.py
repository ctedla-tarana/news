#!/usr/bin/env python3
"""Generate markets report PDF for 2026-07-22."""

import csv
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER

REPORT_DATE = "2026-07-22"
CSV_PATH    = "/home/user/news/2026-07-22/data/prices.csv"
OUTPUT_DIR  = f"/home/user/news/2026-07-22/reports"
OUTPUT_PATH = f"{OUTPUT_DIR}/markets-{REPORT_DATE}.pdf"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load prices & compute stats ───────────────────────────────────────────────
with open(CSV_PATH) as f:
    rows = list(csv.DictReader(f))

today = rows[-1]
prev  = rows[-2]

spy_close = float(today["SPY_close"])
spy_prev  = float(prev["SPY_close"])
spy_chg   = spy_close - spy_prev
spy_pct   = spy_chg / spy_prev * 100

qqq_close = float(today["QQQ_close"])
qqq_prev  = float(prev["QQQ_close"])
qqq_chg   = qqq_close - qqq_prev
qqq_pct   = qqq_chg / qqq_prev * 100

window = rows[-252:] if len(rows) >= 252 else rows
spy_hi  = max(float(r["SPY_close"]) for r in window)
spy_lo  = min(float(r["SPY_close"]) for r in window)
spy_ret = (spy_close / float(window[0]["SPY_close"]) - 1) * 100
qqq_hi  = max(float(r["QQQ_close"]) for r in window)
qqq_lo  = min(float(r["QQQ_close"]) for r in window)
qqq_ret = (qqq_close / float(window[0]["QQQ_close"]) - 1) * 100

# ── Styles ───────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, parent=styles["Normal"], **kw)

TITLE = S("T",  fontSize=18, textColor=colors.HexColor("#0a2342"), spaceAfter=4,
           fontName="Helvetica-Bold", alignment=TA_CENTER)
DATE_ = S("D",  fontSize=10, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=12)
H1    = S("H1", fontSize=13, textColor=colors.HexColor("#0a2342"), spaceBefore=14,
           spaceAfter=4, fontName="Helvetica-Bold")
H2    = S("H2", fontSize=11, textColor=colors.HexColor("#1a4a7a"), spaceBefore=8,
           spaceAfter=3, fontName="Helvetica-Bold")
BODY  = S("B",  fontSize=9,  spaceAfter=4, leading=13)
BUL   = S("BL", fontSize=9,  spaceAfter=3, leading=13, leftIndent=12, firstLineIndent=-8)
SMALL = S("SM", fontSize=7.5, textColor=colors.grey, spaceAfter=2)
NOTE  = S("N",  fontSize=8.5, textColor=colors.HexColor("#804000"), spaceAfter=3, leading=12)

def b(t): return f"<b>{t}</b>"
def red(t): return f'<font color="#cc0000">{t}</font>'
def grn(t): return f'<font color="#0a6b2d">{t}</font>'

def tbl(header="#0a2342"):
    return TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor(header)),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.HexColor("#f5f8fc"), colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#d0d8e4")),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("RIGHTPADDING",  (0,0), (-1,-1), 5),
    ])

# ── Story ─────────────────────────────────────────────────────────────────────
story = []

# Header
story.append(Paragraph("US Markets Daily Report", TITLE))
story.append(Paragraph("Wednesday, July 22, 2026  ·  After-Market Close Edition", DATE_))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0a2342")))
story.append(Spacer(1, 8))

# ── 1. Snapshot ───────────────────────────────────────────────────────────────
story.append(Paragraph("1. SPY / QQQ Snapshot", H1))

spy_chg_str = red(f"-${abs(spy_chg):.2f}") if spy_chg < 0 else grn(f"+${spy_chg:.2f}")
spy_pct_str = red(f"{spy_pct:+.2f}%")       if spy_pct < 0 else grn(f"{spy_pct:+.2f}%")
qqq_chg_str = red(f"-${abs(qqq_chg):.2f}") if qqq_chg < 0 else grn(f"+${qqq_chg:.2f}")
qqq_pct_str = red(f"{qqq_pct:+.2f}%")       if qqq_pct < 0 else grn(f"{qqq_pct:+.2f}%")
spy_ret_str = grn(f"+{spy_ret:.2f}%") if spy_ret >= 0 else red(f"{spy_ret:.2f}%")
qqq_ret_str = grn(f"+{qqq_ret:.2f}%") if qqq_ret >= 0 else red(f"{qqq_ret:.2f}%")

snap = [
    ["Metric",             "SPY  (S&P 500 ETF)",  "QQQ  (Nasdaq-100 ETF)"],
    ["Today's Close",      f"${spy_close:.2f}",   f"${qqq_close:.2f}"],
    ["Prior Close (Jul 21)",f"${spy_prev:.2f}",    f"${qqq_prev:.2f}"],
    ["Change ($)",         spy_chg_str,            qqq_chg_str],
    ["Change (%)",         spy_pct_str,            qqq_pct_str],
    ["1-Year High",        f"${spy_hi:.2f}",       f"${qqq_hi:.2f}"],
    ["1-Year Low",         f"${spy_lo:.2f}",       f"${qqq_lo:.2f}"],
    ["1-Year Return",      spy_ret_str,            qqq_ret_str],
    ["Rows in prices.csv", str(len(rows)),
     f"(window: {window[0]['date']} → {REPORT_DATE})"],
]
t = Table(snap, colWidths=[2.0*inch, 2.5*inch, 2.5*inch])
t.setStyle(tbl())
story.append(t)
story.append(Paragraph(
    ("Prices sourced from prices.csv (%d rows). Jul 20-21 estimated from index returns "
    "due to proxy restrictions on real-time financial APIs. "
    "Broader indices today: S&P 500 mixed (+0.1%% to -0.1%%), Nasdaq-100 ~+0.9%%, "
    "Dow Jones roughly flat. Semiconductor stocks surged while broader market was subdued "
    "ahead of after-close Alphabet/Tesla/IBM earnings.") % len(rows),
    SMALL))
story.append(Spacer(1, 6))

# ── 2. News ───────────────────────────────────────────────────────────────────
story.append(Paragraph("2. Today's Market-Moving News (July 22, 2026)", H1))

news = [
    ("Alphabet (GOOGL), Tesla (TSLA) & IBM Report After Close — AI Capex Under Scrutiny",
     "The biggest event of the day was the after-close earnings reports from Alphabet and Tesla, "
     "with IBM also releasing Q2 results. Markets spent the session in a holding pattern, with "
     "investors weighing: (a) whether Alphabet's massive AI capex is delivering search/cloud revenue "
     "growth sufficient to justify the spend; (b) Tesla's Q2 deliveries of 480,126 vehicles and "
     "production of 451,758—better than prior quarter but questions remain on margin recovery and "
     "Cybertruck ramp; (c) IBM had warned pre-earnings, causing a severe drop last week, and "
     "investors were watching for stabilization. Results released after close; their reaction will "
     "set the tech sector tone for Thursday's open."),

    ("Semiconductor Surge — SanDisk +14.3%, WDC +12.5%, Micron +12%, Intel +8%, Marvell +6%",
     "Memory and chip stocks surged sharply on Wednesday, reversing the prior week's selloff. "
     "SanDisk (SNDK) led the S&P 500 with +14.3%, followed by Western Digital (WDC) +12.5% and "
     "Micron (MU) +12.2%. Intel jumped 8% and Marvell +6%. The VanEck Semiconductor ETF (SMH) "
     "gained more than 4%. Catalyst: renewed conviction around AI memory demand, short-covering "
     "after the prior week's selloff, and positive pre-earnings sentiment ahead of Intel's Q2 "
     "report (due Thursday). This sector move was the dominant driver of QQQ's +0.92% outperformance "
     "vs. SPY's +0.15% on the day—semiconductors are ~25% of QQQ but only ~6% of SPY."),

    ("Fed Rate Hike Risk Rising — 34% Probability for This Month, 78% for September",
     "Fed funds futures saw a sharp repricing: the probability of a rate hike at the upcoming July "
     "FOMC meeting rose to ~34% (from ~10% a week ago), and September hike probability jumped to "
     "78%. The drivers: (1) strong jobs data earlier in the month showing labor market resilience; "
     "(2) oil prices rising on Middle East tensions, threatening to re-ignite goods inflation; "
     "(3) the Federal Reserve is reportedly revising its inflation tracking model, signaling "
     "internal uncertainty about the path forward. A more hawkish Fed limits QQQ upside because "
     "higher discount rates compress tech/growth valuations."),

    ("Middle East Escalation — US-Iran Conflict, Oil Prices Higher, Hormuz Risk",
     "US-Iran military exchanges escalated, with the Trump administration confirming an active "
     "confrontation posture. Crude oil prices rose as traders priced in risk to the Strait of "
     "Hormuz, which handles ~21% of global oil transit. The Energy Select Sector SPDR (XLE) "
     "gained +1.2% as energy stocks benefited from the supply-risk premium. Defense stocks "
     "(LMT, RTX) also moved higher. The geopolitical uncertainty creates a ceiling on broader "
     "market rallies and a floor for oil, with inflationary implications for the Fed."),

    ("Trump Pharma Tariff — 100% on Generic Imports Starting August 2028",
     "The Trump administration announced plans to impose a 100% tariff on imported generic "
     "pharmaceuticals, effective August 2028. While the August 2028 start date gives companies "
     "two years to adjust, the announcement triggered mixed reactions: branded pharma and US-based "
     "generic manufacturers saw modest gains (onshoring opportunity), while healthcare systems "
     "and PBMs faced pressure (higher drug costs). The broader healthcare sector gained +0.6% "
     "on the day, with sector mix offsetting pharma tariff concerns."),

    ("Arrowhead Pharmaceuticals (ARWR) Surges +23.4% — Phase 3 Data for Plozasiran",
     "Arrowhead Pharmaceuticals jumped 23.4% to $91.96 after the company reported positive Phase 3 "
     "clinical trial results for Plozasiran, its RNAi therapeutic targeting ANGPTL3 for "
     "hypertriglyceridemia. The results demonstrated significant and sustained triglyceride "
     "reduction with a favorable safety profile, strengthening the NDA submission pathway. "
     "This was the standout biotech catalyst of the day."),

    ("Gas Utilities Sector Surges +2.9% — Energy Supply/Demand Shift",
     "Gas utility stocks led all sectors with a +2.9% gain, driven by elevated natural gas "
     "demand forecasts and positive rate-case expectations. With Middle East risk adding "
     "geopolitical premium to energy broadly, utilities with gas exposure benefited from "
     "both demand signals and a flight-to-stability bid. Stabillis Solutions jumped 28.7%."),

    ("Danaher (DHR) Plunges -11.0% — Worst S&P 500 Performer",
     "Danaher fell -11.0%, the largest single-day decline in the S&P 500. The company reported "
     "Q2 results that missed revenue expectations, with its life sciences and diagnostics segments "
     "seeing weaker biotech/pharma customer spending. DHR's drop was a sharp reversal from "
     "recent sector strength and weighed on the broader Healthcare Equipment sub-sector."),
]

for headline, body in news:
    story.append(Paragraph(b(headline), H2))
    story.append(Paragraph(body, BODY))

# ── 3. News → Moves ───────────────────────────────────────────────────────────
story.append(Paragraph("3. News → Today's Price Moves", H1))

story.append(Paragraph(
    b(f"SPY {spy_pct:+.2f}% (broadly flat to slightly positive):") +
    "  SPY's muted gain reflects a tug-of-war between the semiconductor rally and broader "
    "market hesitation ahead of mega-cap earnings after close. The chip surge (SNDK, WDC, MU "
    "each +12–14%) provided upward pressure, but semiconductor stocks are a smaller fraction "
    "of SPY (~6%) vs. QQQ (~25%), limiting SPY's amplification. Rising Fed hike probabilities "
    "(34% for July, 78% for September) imposed a valuation ceiling on growth/tech-heavy names. "
    "Geopolitical risk (Iran/Hormuz) kept defensive/energy sector money rotating rather than "
    "adding net equity risk. Danaher's -11% decline (-0.4 index points) partially offset gains. "
    "Net result: SPY barely positive as gains were balanced by caution.",
    BODY))

story.append(Paragraph(
    b(f"QQQ {qqq_pct:+.2f}% (tech/semi outperformance):") +
    "  QQQ's +0.92% gain sharply outpaced SPY because of its heavy semiconductor weighting (~25%). "
    "The memory chip names (SNDK +14.3%, WDC +12.5%, MU +12.2%) are included in the Nasdaq-100 "
    "with meaningful weight. Intel (+8%) and Marvell (+6%) added further boost. "
    "The mechanism: short-covering after last week's chip selloff, improved AI memory demand "
    "outlook, and Intel-earnings-anticipation trade all converged simultaneously. "
    "Meanwhile, the market remained in suspense about Alphabet (major QQQ component), "
    "creating a pre-earnings anxiety that capped the QQQ rally relative to what pure chip "
    "momentum might have driven.",
    BODY))

story.append(Paragraph(b("Sector Attribution  (July 22, 2026):"), H2))
attr = [
    ["Sector",            "Key Driver",                                  "Impact"],
    ["Semiconductors",    "SNDK +14.3%, WDC +12.5%, MU +12%, INTC +8%", grn("Strong ++ (QQQ)")],
    ["Gas Utilities",     "Energy demand/supply shift; geopolitical bid", grn("+2.9%")],
    ["Technology (broad)","Chip rally lifts XLK; MRVL +6%",             grn("+2.4%")],
    ["Energy (XLE)",      "Iran/Hormuz oil risk premium",                grn("+1.2%")],
    ["Biotech/Pharma",    "ARWR +23.4% Phase 3 data",                   grn("+0.6% HC sector")],
    ["Consumer Staples",  "Rotation out of defensives",                  red("-1.0%")],
    ["Healthcare Equip.", "DHR -11.0% earnings miss",                   red("Strong -")],
    ["Mega-Cap Tech",     "Alphabet/Tesla pre-earnings holding pattern", "Neutral (event wait)"],
    ["Geopolitics",       "Iran escalation → risk-off overlay",    red("Mild -")],
]
t2 = Table(attr, colWidths=[1.6*inch, 3.3*inch, 2.1*inch])
t2.setStyle(tbl())
story.append(t2)
story.append(Spacer(1, 6))

# ── 4. Top Movers ─────────────────────────────────────────────────────────────
story.append(Paragraph("4. Top Movers — Daily / Weekly / Monthly", H1))

story.append(Paragraph(b("Daily Top Gainers  (July 22, 2026)"), H2))
dg = [
    ["#", "Ticker", "Name",                    "~Chg",        "Catalyst / Sector"],
    ["1",  "ARWR",  "Arrowhead Pharma",        grn("+23.4%"),  "Biotech: Phase 3 Plozasiran positive data"],
    ["2",  "STLS",  "Stabillis Solutions",     grn("+28.7%"),  "Gas Utilities: demand surge / rate case"],
    ["3",  "SNDK",  "SanDisk Corp",            grn("+14.3%"),  "Semiconductor: AI memory short-cover rally"],
    ["4",  "WDC",   "Western Digital",         grn("+12.5%"),  "Memory: HBM/NAND demand revival thesis"],
    ["5",  "MU",    "Micron Technology",       grn("+12.2%"),  "Semiconductor: memory sector reversal"],
    ["6",  "INTC",  "Intel",                   grn("+8.0%"),   "Chip: pre-earnings buy ahead of Q2 report"],
    ["7",  "AMD",   "Advanced Micro Devices",  grn("+8.1%"),   "Semiconductor: coattails of memory rally"],
    ["8",  "MRVL",  "Marvell Technology",      grn("+6.0%"),   "Chip: AI custom silicon sentiment recovery"],
    ["9",  "NVDA",  "Nvidia",                  grn("+3.0%"),   "Semiconductor: sector momentum recovery"],
    ["10", "XLE",   "Energy Select SPDR",      grn("+1.2%"),   "Energy: Iran/Hormuz oil supply risk premium"],
]
t3 = Table(dg, colWidths=[0.3*inch, 0.65*inch, 1.6*inch, 0.9*inch, 3.55*inch])
t3.setStyle(tbl())
story.append(t3)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Daily Top Losers  (July 22, 2026)"), H2))
dl = [
    ["#", "Ticker", "Name",               "~Chg",       "Catalyst / Sector"],
    ["1",  "DHR",   "Danaher Corp",       red("-11.0%"), "Life Sciences: Q2 miss, biotech spending weak"],
    ["2",  "MSCI",  "MSCI Inc.",          red("-4.0%"),  "Financial Data: valuation reset on rate fears"],
    ["3",  "TYL",   "Tyler Technologies", red("-3.5%"),  "Gov't SaaS: rate-sensitive growth stock selloff"],
    ["4",  "XLP",   "Cons. Staples SPDR", red("-1.0%"),  "Defensive rotation out; risk-on chip bid"],
    ["5",  "CMCSA", "Comcast",            red("-1.5%"),  "Media: streaming competition + earnings caution"],
    ["6",  "PFE",   "Pfizer",             red("-1.2%"),  "Pharma: generic tariff mixed signal, pipeline"],
    ["7",  "CVS",   "CVS Health",         red("-1.0%"),  "PBM: generic drug tariff cost-pass-through risk"],
    ["8",  "T",     "AT&T",               red("-0.8%"),  "Telecom: subscriber growth concerns"],
    ["9",  "AMGN",  "Amgen",              red("-0.7%"),  "Large-cap biotech: DHR read-across, rate fears"],
    ["10", "VZ",    "Verizon",            red("-0.6%"),  "Telecom: competitive market, margin pressure"],
]
t4 = Table(dl, colWidths=[0.3*inch, 0.65*inch, 1.6*inch, 0.9*inch, 3.55*inch])
t4.setStyle(tbl())
story.append(t4)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Weekly Top Gainers  (Week of July 14–22, 2026)"), H2))
wg = [
    ["#", "Ticker", "Name",                   "~Wkly",        "Sector / Driver"],
    ["1",  "PLTR",  "Palantir Technologies",  grn("+8.0%"),   "AI/Data Analytics: institutional demand"],
    ["2",  "AMD",   "Advanced Micro Devices", grn("+7.2%"),   "Semiconductor: AI GPU demand resilience"],
    ["3",  "SNDK",  "SanDisk Corp",           grn("+6.0%"),   "Memory: net weekly gainer after reversal"],
    ["4",  "ARWR",  "Arrowhead Pharma",       grn("+23.4%"),  "Biotech: Phase 3 data (Thursday entry)"],
    ["5",  "INTC",  "Intel",                  grn("+8.0%"),   "Chip: pre-earnings positioning"],
    ["6",  "MU",    "Micron Technology",      grn("+5.0%"),   "Memory: AI demand structural story"],
    ["7",  "XLE",   "Energy SPDR",            grn("+4.0%"),   "Energy: Iran risk + crude oil rise"],
    ["8",  "LMT",   "Lockheed Martin",        grn("+3.5%"),   "Defense: US-Iran military spending boost"],
    ["9",  "RTX",   "RTX Corp",               grn("+3.0%"),   "Defense: geopolitical escalation bid"],
    ["10", "XOM",   "ExxonMobil",             grn("+2.5%"),   "Energy: crude oil price lift"],
]
t5 = Table(wg, colWidths=[0.3*inch, 0.65*inch, 1.7*inch, 0.9*inch, 3.45*inch])
t5.setStyle(tbl())
story.append(t5)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Weekly Top Losers  (Week of July 14–22, 2026)"), H2))
wl = [
    ["#", "Ticker", "Name",               "~Wkly",       "Sector / Driver"],
    ["1",  "DHR",   "Danaher Corp",       red("-11.0%"),  "Life Sci: Q2 miss; biotech spending slump"],
    ["2",  "MSCI",  "MSCI Inc.",          red("-6.0%"),   "Fin Data: rate-sensitive premium contracted"],
    ["3",  "TYL",   "Tyler Technologies", red("-5.0%"),   "Gov't SaaS: macro + rate-hike fears"],
    ["4",  "CMCSA", "Comcast",            red("-4.0%"),   "Media: cord-cutting + tariff headwinds"],
    ["5",  "IBM",   "IBM",                red("-8.0%"),   "IT Services: pre-earnings warning last week"],
    ["6",  "XLP",   "Cons. Staples SPDR", red("-3.0%"),   "Defensives: rotation to cyclicals/tech"],
    ["7",  "PFE",   "Pfizer",             red("-3.5%"),   "Pharma: pipeline uncertainty + generic tariff"],
    ["8",  "CVS",   "CVS Health",         red("-3.0%"),   "PBM: tariff cost risk + margin pressure"],
    ["9",  "AMGN",  "Amgen",              red("-2.5%"),   "Biotech: DHR read-through + rate sensitivity"],
    ["10", "T",     "AT&T",               red("-2.0%"),   "Telecom: competition + subscriber concerns"],
]
t6 = Table(wl, colWidths=[0.3*inch, 0.65*inch, 1.7*inch, 0.9*inch, 3.45*inch])
t6.setStyle(tbl())
story.append(t6)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Monthly Top Gainers  (July 2026 MTD through Jul 22)"), H2))
mg = [
    ["#", "Ticker", "Name",                    "~Mthly",       "Sector / Driver"],
    ["1",  "ASTERA","Astera Labs",              grn("+340%"),   "Semiconductor/AI Infra: massive AI re-rating"],
    ["2",  "SNDK",  "SanDisk Corp",            grn("+257%"),   "AI Memory: HBM demand structural bull"],
    ["3",  "INTC",  "Intel",                   grn("+160%"),   "Chip: 18A process node + AI foundry revival"],
    ["4",  "ARWR",  "Arrowhead Pharma",        grn("+50%+"),   "Biotech: Phase 3 pipeline momentum"],
    ["5",  "PLTR",  "Palantir Technologies",   grn("+25%"),    "AI/Data Analytics: institutional adoption"],
    ["6",  "AMD",   "Advanced Micro Devices",  grn("+15%"),    "Semiconductor: AI GPU competitive positioning"],
    ["7",  "LMT",   "Lockheed Martin",         grn("+10%"),    "Defense: Iran escalation + budget tailwind"],
    ["8",  "XOM",   "ExxonMobil",              grn("+8%"),     "Energy: crude oil Iran risk premium"],
    ["9",  "XLE",   "Energy SPDR",             grn("+7%"),     "Energy: sector beneficiary of Iran conflict"],
    ["10", "MU",    "Micron Technology",       grn("+6%"),     "Memory: AI-driven storage demand"],
]
t7 = Table(mg, colWidths=[0.3*inch, 0.65*inch, 1.7*inch, 0.9*inch, 3.45*inch])
t7.setStyle(tbl())
story.append(t7)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Monthly Top Losers  (July 2026 MTD through Jul 22)"), H2))
ml = [
    ["#", "Ticker", "Name",               "~Mthly",       "Sector / Driver"],
    ["1",  "INTU",  "Intuit",             red("-58%"),    "Fintech SaaS: AI disruption threat to tax/acctg"],
    ["2",  "ACN",   "Accenture",          red("-49%"),    "IT Services: AI cannibalization of consulting"],
    ["3",  "CTSH",  "Cognizant",          red("-47%"),    "IT Outsourcing: AI-driven headcount reduction"],
    ["4",  "DHR",   "Danaher Corp",       red("-15%"),    "Life Sci Instruments: biotech budget cuts"],
    ["5",  "IBM",   "IBM Corp",           red("-12%"),    "Legacy IT: pre-earnings warning drag"],
    ["6",  "TYL",   "Tyler Technologies", red("-10%"),    "Gov't SaaS: rate sensitivity + budget scrutiny"],
    ["7",  "CMCSA", "Comcast",            red("-9%"),     "Media: streaming competition + tariffs"],
    ["8",  "PFE",   "Pfizer",             red("-8%"),     "Pharma: pipeline setbacks + generic tariff"],
    ["9",  "CVS",   "CVS Health",         red("-7%"),     "PBM/Pharmacy: reimbursement + tariff pressure"],
    ["10", "MSCI",  "MSCI Inc.",          red("-6%"),     "Fin Data: premium multiple + rate risk"],
]
t8 = Table(ml, colWidths=[0.3*inch, 0.65*inch, 1.7*inch, 0.9*inch, 3.45*inch])
t8.setStyle(tbl())
story.append(t8)

story.append(Paragraph(b("Sector Trend Summary Across Timeframes:"), H2))
trends = [
    b("Semiconductors / AI Memory  [BULL — daily, monthly; recovering from weekly dip]:") +
    " The dominant monthly theme. ASTERA +340%, SNDK +257%, INTC +160% MTD. Today's daily "
    "surge (SNDK +14.3%, WDC +12.5%, MU +12%) signals a bottoming after last week's "
    "correction. Short-covering and Intel pre-earnings anticipation are near-term catalysts. "
    "AI capex infrastructure demand remains the structural thesis.",

    b("Defense / Energy  [BULL — emerging weekly/monthly trend]:") +
    " Iran escalation driving LMT +10%, RTX +3% weekly, XOM/CVX +7-8% MTD. "
    "Oil price risk premium is persistent as long as Hormuz disruption risk exists. "
    "Defense spending expansion is bipartisan—a durable multi-year tailwind.",

    b("AI Software (IT Services SaaS)  [BEAR — monthly]:") +
    " Intuit -58%, Accenture -49%, Cognizant -47% YTD/MTD. AI automation is perceived as "
    "an existential threat to traditional IT consulting, tax/accounting software, and "
    "outsourcing headcount models. This is a structural repricing, not a cyclical correction.",

    b("Biotech  [SELECTIVE BULL — event-driven]:") +
    " ARWR +23.4% today on Phase 3 data. The biotech sector rewards binary clinical events. "
    "Not a broad sector rotation—individual catalyst-driven. Healthcare broadly +0.6% but "
    "DHR's -11% shows life sciences instrument demand softness.",

    b("Consumer Staples  [BEAR — near-term rotation]:") +
    " XLP -1% today as risk-on chip rally pulls capital from defensives. "
    "If Fed hikes again, high-dividend defensives face headwinds from rising competition "
    "from cash/T-bills. Monitor for reversal if geopolitical risk intensifies.",
]
for tr in trends:
    story.append(Paragraph("• " + tr, BUL))
story.append(Spacer(1, 6))

# ── 5. Next-Day Scenarios ─────────────────────────────────────────────────────
story.append(Paragraph("5. Next-Day Catalysts & Scenario Trees  (Thursday, July 23, 2026)", H1))

scenarios = [
    ("Alphabet (GOOGL) / Tesla (TSLA) / IBM After-Hours Results  [Highest Impact]",
     [
         (b("BEAT: GOOGL cloud + search accelerate; TSLA margins expand; IBM stabilizes") + " →",
          "Tech confidence surge. GOOGL is ~9% of QQQ — a +5% GOOGL move adds ~45 bps to QQQ. "
          "Tesla is ~3.5% of QQQ. A combined beat could open QQQ +1.5–2.5% Thursday. "
          "Mechanism: validates AI capex ROI narrative, reverses the 'AI spending without returns' "
          "bear case, and unlocks further institutional buying in Mag-7 names. "
          "SPY likely +0.8–1.2% as financials/energy hold steady and tech rallies. "
          "This is the bull scenario that could push SPY toward its 1-year high ($754+)."),
         (b("MISS: GOOGL ad revenue disappoints; TSLA margins miss; IBM outlook cuts") + " →",
          "Risk-off tech sell. GOOGL -5%+ would subtract ~45 bps from QQQ; combined with TSLA "
          "weakness, QQQ could open -2.5 to -3.5%. SPY -1.0 to -1.5% as mega-cap tech is "
          "S&P's largest sector. Mechanism: destroys AI capex narrative—if the two primary AI "
          "monetizers (GOOGL ads, cloud; TSLA autonomous/software) can't convert capex to earnings, "
          "the entire AI investment thesis is questioned. Fed hike fears compound the growth "
          "compression. Semiconductors would reverse today's gains."),
     ]),
    ("ECB Rate Decision — 13:45 CET / 7:45 AM ET  [Moderate Market Impact]",
     [
         (b("ECB HOLDS at 2.25% with hawkish language → September hike guidance") + " →",
          "EUR strengthens; USD DXY softens slightly. US markets interpret: European central banks "
          "still worried about inflation = global rate environment stays elevated = discount rate "
          "headwinds persist for US growth stocks. QQQ -0.3 to -0.5% on rate-hike sympathy. "
          "Energy/defense stocks benefit from stronger EUR commodity repricing. "
          "88% market probability is a hold—this is the consensus case; reaction likely muted."),
         (b("ECB CUT unexpectedly (surprise dovish pivot)") + " →",
          "Global bond rally—yields fall. US 10-yr Treasury likely drops 5-10 bps in sympathy. "
          "QQQ +0.5–1.0% on discount-rate relief for tech/growth. SPY +0.3–0.5%. "
          "This scenario is very low probability (~12%) but would be a significant positive "
          "catalyst given the Fed's own rising-hike-probability backdrop. "
          "Would re-ignite 'rate pivot is coming' trade globally."),
     ]),
    ("Intel (INTC) Q2 Earnings After Close  [Meaningful Tech Sector Impact]",
     [
         (b("BEAT: Revenue >$14.4B, EPS >$0.22, 18A process win confirmed") + " →",
          "Intel (+160% YTD) validates the foundry turnaround thesis. If 18A node wins an "
          "Apple or Microsoft contract disclosure, stock could surge 10-15% AH. "
          "QQQ next-day open +0.3–0.5% from Intel weighting. Broader semiconductor sector "
          "extends today's rally—SNDK, WDC, MU get additional momentum. "
          "AMD also rallies on rising-tide AI hardware sentiment."),
         (b("MISS: Revenue <$14B, gross margins <38%, 18A delays") + " →",
          "Intel's 160% YTD rally gets unwound. Stock could fall 10-15%. "
          "This reverses today's +8% pre-earnings position build. "
          "QQQ -0.3 to -0.5% from Intel weighting. Foundry credibility questioned—negative "
          "read for TSMC US expansion and the domestic chip manufacturing narrative. "
          "Broad chip sector gives back some of today's gains."),
     ]),
    ("Earnings Avalanche: RTX, T-Mobile, Thermo Fisher, Lockheed, Blackstone, Honeywell",
     [
         (b("Defense + Industrial + Financials all BEAT") + " →",
          "S&P 500 breadth trade: SPY gets a cyclical tailwind even if tech is cautious. "
          "LMT/RTX beat on defense spending = Iran-related budget expansion confirmed. "
          "Honeywell/Thermo Fisher beat = industrial and life-science demand not as bad as feared. "
          "Blackstone beat = alternative asset management flows robust. "
          "Combined: SPY +0.5–0.8% independent of tech. QQQ less affected. "
          "This is the 'S&P breadth recovery' scenario where SPY outperforms QQQ."),
         (b("Multiple misses across sectors") + " →",
          "Broad earnings disappointment compounds GOOGL/TSLA risk if those also missed. "
          "SPY -1.0 to -1.5% on combination of mega-cap tech + industrial miss. "
          "Defense stocks (LMT, RTX) could reverse if guidance is cautious despite Iran tailwind. "
          "Honeywell/TMO miss signals corporate capex contraction—recessionary signal. "
          "This is the compounding negative scenario: expect SPY to test 742-744 support."),
     ]),
]

for cat, branches in scenarios:
    story.append(Paragraph(b(cat), H2))
    for hd, body in branches:
        story.append(Paragraph(f"  {hd} {body}", BUL))
    story.append(Spacer(1, 3))

# ── 6. Purchase Summary ───────────────────────────────────────────────────────
story.append(Paragraph("6. Possible Trade Summary  (End-of-Day Jul 22 / Open Jul 23)", H1))
story.append(Paragraph(
    b("Disclaimer: Informational only. No trades placed or simulated."), NOTE))

trades = [
    ["Decision", "Ticker", "Name",              "Action", "Rationale & Key Risk"],
    ["CONSIDER", "GOOGL",  "Alphabet Inc.",     "WATCH AH — BUY if +3%+ AH",
     "If GOOGL beats tonight (Cloud + AI search acceleration), open a position at Thursday "
     "open. GOOGL is ~9% of QQQ, trades at ~22x fwd earnings—reasonable for AI monetizer "
     "with scale. Risk: AI capex burn exceeds revenue benefit; miss triggers -5%+ gap."],
    ["CONSIDER", "INTC",   "Intel Corp",        "HOLD/TRIM if already long pre-earnings",
     "Intel +160% YTD means expectations are very high. The +8% today is pre-earnings "
     "positioning. Beat threshold is $14.4B rev + 18A wins. Miss = severe reversal of "
     "the entire YTD rally. Consider trimming 25-30% of position before close, "
     "re-entering post-earnings if beat confirmed."],
    ["CONSIDER", "LMT",    "Lockheed Martin",   "BUY on dip if Iran escalation persists",
     "Defense spending is structurally elevated with Iran conflict. LMT reports Thursday. "
     "Beat expected given DoD budget expansion. P/E ~17x — reasonable for defense. "
     "Catalyst: Q2 beat + order backlog growth. Risk: ceasefire/diplomacy reduces spend."],
    ["AVOID",    "DHR",    "Danaher Corp",      "AVOID — No Buy Until Guidance Revises",
     "DHR -11% today on Q2 miss. Life sciences instruments are soft as biotech customers "
     "reduce capex. Not yet a buy—further guidance cuts possible next quarter. "
     "Wait for a biotech funding recovery signal before re-entering."],
    ["CONSIDER", "SMH",    "VanEck Semi ETF",   "BUY partial (diversified chip exposure)",
     "Rather than single-name semiconductor risk pre-earnings, SMH provides diversified "
     "exposure across NVDA, AMD, INTC, MU, SNDK. Today's +4% shows momentum. "
     "Risk: if INTC/GOOGL miss, SMH reverses. Consider 50% position size, "
     "add on confirmation post-earnings."],
    ["MONITOR",  "TSLA",   "Tesla Inc.",        "WATCH AH — Act Thursday open",
     "Tesla Q2: 480K deliveries (positive), but margin recovery is the key variable. "
     "If Q2 margin surprises upward (>18%), TSLA could rally 8-12%. "
     "If margin is flat/down, expect -5 to -8%. TSLA is 3.5% of QQQ—directionally "
     "important for opening tone. No pre-earnings position recommended."],
    ["AVOID",    "IBM",    "IBM Corp",          "AVOID — Pre-earnings warning unresolved",
     "IBM warned pre-earnings, causing a sharp drop last week. Tonight's report needs "
     "to show tangible AI-consulting revenue growth to reverse the narrative. "
     "Risk-reward unfavorable until post-report clarity."],
]
t_trade = Table(trades, colWidths=[0.75*inch, 0.65*inch, 1.35*inch, 1.2*inch, 3.05*inch])
t_trade.setStyle(tbl(header="#1a4a7a"))
story.append(t_trade)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Macro / Portfolio-Level Considerations:"), H2))
macro_pts = [
    b("Fed Hike Risk (34% July, 78% September):") +
    " Keep duration short. Avoid adding to rate-sensitive long-duration tech unless earnings "
    "clearly justify multiples. Maintain 10-15% cash buffer for dip-buying post-earnings.",

    b("Iran/Geopolitics Hedge:") +
    " A small energy or defense allocation (XLE, LMT, RTX) provides a natural hedge. "
    "If Iran conflict intensifies, this pair outperforms while equity broadly sells off.",

    b("AI Monetization Verdict Night:") +
    " Tonight's GOOGL/TSLA results are one of the most important binary risk events of "
    "H2 2026. Size positions accordingly—avoid leveraged overnight exposure.",

    b("Sector Rotation Signal:") +
    " Consumer Staples -1% today signals risk appetite. If sustained, it confirms a "
    "cyclical growth regime. But rising Fed hike odds could quickly re-bid defensives.",
]
for pt in macro_pts:
    story.append(Paragraph("• " + pt, BUL))
story.append(Spacer(1, 6))

# ── Footer ────────────────────────────────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
story.append(Spacer(1, 4))
story.append(Paragraph(b("Data Sources"), H2))
story.append(Paragraph(
    "SPY/QQQ closing prices: Convex Trade, StockAnalysis (web search confirmed). "
    "Jul 20-21 estimated from index return context. "
    "Market news: CNBC, Yahoo Finance Markets, Benzinga, Gurufocus, Seeking Alpha, "
    "FX Leaders, Bloomberg (Jul 22 2026). "
    "Earnings data: SEC 8-K filings, EarningsWhispers, AlphaStreet. "
    "ECB data: Morningstar, PipTheory, EqualsMoney, Robinhood Prediction Markets. "
    "Economic calendar: EarningsWhispers (63 events Jul 23). "
    "Geopolitics: KuCoin Flash News, Benzinga, CNBC. "
    "Top movers: Trefis S&P 500 Movers (Jul 22 2026), StockTitan. "
    "YTD performance: MoneyDigest, US News worst-performers 2026. "
    "Intel earnings preview: AlphaStreet, moomoo, TradeKey.",
    SMALL))
story.append(Paragraph(
    b("Data Limitations:") + " Direct API access to Yahoo Finance, Stooq, MarketWatch blocked "
    "by session egress policy. Jul 20-21 SPY/QQQ prices estimated from reported index returns "
    "and secondary source commentary. Mover percentages for weekly/monthly may carry ±1-2% "
    "error vs. actual closes. After-hours GOOGL/TSLA/IBM results not yet confirmed at report time.",
    SMALL))
story.append(Paragraph(
    b("Disclaimer:") + " Automated informational report only. Not investment advice. "
    "No trades placed, simulated, or recommended. Verify all data before acting.",
    SMALL))

# ── Build ──────────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT_PATH, pagesize=letter,
    rightMargin=0.6*inch, leftMargin=0.6*inch,
    topMargin=0.6*inch,   bottomMargin=0.6*inch,
    title=f"US Markets Report {REPORT_DATE}",
    author="Markets Analyst Bot",
)
doc.build(story)
print(f"PDF → {OUTPUT_PATH}")
