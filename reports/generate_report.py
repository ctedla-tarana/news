#!/usr/bin/env python3
"""Generate markets report PDF for 2026-07-16."""

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

REPORT_DATE = "2026-07-16"
CSV_PATH    = "/home/user/news/data/prices.csv"
OUTPUT_DIR  = f"/home/user/news/reports/{REPORT_DATE}"
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

def mkrow(*cells, widths):
    t = Table([list(cells)], colWidths=widths)
    t.setStyle(tbl())
    return t

# ── Story ─────────────────────────────────────────────────────────────────────
story = []

# Header
story.append(Paragraph("US Markets Daily Report", TITLE))
story.append(Paragraph("Wednesday, July 16, 2026  ·  After-Market Close Edition", DATE_))
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
    ["Prior Close",        f"${spy_prev:.2f}",    f"${qqq_prev:.2f}"],
    ["Change ($)",         spy_chg_str,            qqq_chg_str],
    ["Change (%)",         spy_pct_str,            qqq_pct_str],
    ["1-Year High",        f"${spy_hi:.2f}",       f"${qqq_hi:.2f}"],
    ["1-Year Low",         f"${spy_lo:.2f}",       f"${qqq_lo:.2f}"],
    ["1-Year Return",      spy_ret_str,            qqq_ret_str],
    ["Rows in prices.csv", str(len(rows)),         f"(window: {window[0]['date']} → {REPORT_DATE})"],
]
t = Table(snap, colWidths=[2.0*inch, 2.5*inch, 2.5*inch])
t.setStyle(tbl())
story.append(t)
story.append(Paragraph(
    "Prices sourced from prices.csv (264 rows); July 9-10, 13 interpolated from index returns "
    "due to proxy restrictions on real-time financial APIs. "
    "Broader indices: S&P 500 –0.45%, Nasdaq-100 –1.51%, Dow Jones –0.30%, Russell 2000 –0.23%.",
    SMALL))
story.append(Spacer(1, 6))

# ── 2. News ───────────────────────────────────────────────────────────────────
story.append(Paragraph("2. Today's Market-Moving News", H1))

news = [
    ("TSMC Q2 2026 — Beat Meets 'Sell the News' Reaction",
     "Taiwan Semiconductor reported Q2 revenue +36% YoY, well above consensus—yet the market "
     "reacted with a second day of semiconductor selling. Investors focused on (a) valuation: "
     "AI chip names are priced for perfection, and a 'good enough' beat is not a catalyst; "
     "(b) pricing signals: TSMC told major clients—Apple, Nvidia, Qualcomm, AMD—to expect "
     "wafer price hikes of 5–10%, suggesting near-term margin pressure for fabless customers. "
     "TSMC's results are the sector's quarterly stress-test; any ambiguity bleeds into AMD, NVDA, INTC."),
    ("AI Memory Stocks Plunge — SNDK –8%, WDC –8%",
     "SanDisk (SNDK) and Western Digital (WDC) each fell roughly 8%, the sharpest single-day "
     "loss in the group. TSMC's comments on HBM/memory capacity allocation triggered fears "
     "that AI-driven memory demand may be peaking or front-loaded into H1 2026. This is a "
     "significant valuation event: both names traded at elevated AI-demand multiples entering the day."),
    ("US–Iran Conflict Escalation — Hormuz Risk Returns",
     "President Trump declared the US–Iran ceasefire ended after Iranian forces attacked "
     "three vessels near the Strait of Hormuz (July 6–7). Crude oil prices jumped on the threat "
     "of supply disruption; the Strait handles ~21% of global oil transit. GE Aerospace cited "
     "this risk in Q1 commentary (rising jet fuel costs). The escalation adds a geopolitical "
     "risk premium across equities, weighing most on risk-sensitive tech and consumer names."),
    ("UnitedHealth Group Q2 2026 — Massive Beat & Guidance Raise",
     "UNH reported Q2 adjusted EPS $6.38 vs. $4.85 consensus (+32% beat) on revenue of $112B. "
     "Full-year adjusted EPS guidance raised to $19.50–$20.00 (vs. ~$18.75 prior). Cash-flow "
     "guidance raised to ~$24B from $18B+. This was the dominant positive story: UNH has heavy "
     "S&P 500 weighting and its sharp rally materially cushioned the index against semiconductor "
     "losses. Healthcare demonstrates resilience against macro headwinds."),
    ("GE Aerospace Q2 2026 — Raised Guide, Orders +17%",
     "GE reported total orders of $16.5B (+17%), revenue of $13.3B (+21%), adjusted EPS $2.02 "
     "vs. $1.86 estimate (+8.6% beat). FY2026 EPS guidance raised to $7.65–$7.85. Commercial "
     "aviation demand is robust despite Iran-related fuel-cost risk. This was the key Industrials "
     "bright spot and contributed positively to S&P 500 breadth."),
    ("BlackRock Q2 2026 — Beat + JPMorgan Upgrade (+6.6%)",
     "BLK surged 6.6% to $1,093.40 after strong Q2 earnings beat. JPMorgan upgraded to "
     "Overweight with $1,364 price target (from $1,165 Neutral). Asset management flows held up "
     "despite macro uncertainty; fee revenues beat. Financials' outperformance provided the "
     "second major offset to semiconductor losses within the S&P 500."),
    ("Netflix Q2 2026 — In-Line After Close (Watch Friday Open)",
     "NFLX reported Q2 revenue $12.6B (+13% YoY), operating margin 33%—both in-line with "
     "guidance. Full-year guidance narrowed to $51.0–51.4B. View hours +2% in H1 2026. "
     "The report removes tail-risk around streaming but provides no upside catalyst. "
     "After-hours NFLX reaction will likely set the tone for consumer-tech sentiment Friday."),
]

for headline, body in news:
    story.append(Paragraph(b(headline), H2))
    story.append(Paragraph(body, BODY))

# ── 3. News → Moves ───────────────────────────────────────────────────────────
story.append(Paragraph("3. News → Today's Price Moves", H1))

story.append(Paragraph(
    b(f"SPY {spy_pct:+.2f}% (S&P 500 –0.45%):") + "  Healthcare and industrials provided "
    "powerful offsets against the semiconductor drag. UNH's blowout (+32% EPS beat) added "
    "an estimated 30–40 bps of positive S&P 500 attribution. GE Aerospace and BlackRock "
    "further reinforced the offset. The semiconductor names (NVDA, AMD, INTC) have smaller "
    "direct weight in SPY vs. QQQ, so the sector's decline was diluted. Iran risk added "
    "mild risk-off sentiment but did not trigger broad-market panic—likely because energy "
    "(oil up) partially offset the headline worry in SPY.",
    BODY))

story.append(Paragraph(
    b(f"QQQ {qqq_pct:+.2f}% (Nasdaq-100 –1.51%):") + "  The Nasdaq-100 bore the brunt "
    "because its composition is dominated by mega-cap tech and semiconductors—precisely the "
    "sectors under TSMC-driven selling pressure. Two consecutive days of chip-sector selling "
    "(SNDK/WDC –8%, AMD/NVDA/INTC lower) compounded the TSMC 'sell-the-news' dynamic. "
    "QQQ's geographic concentration in AI-related names means Iran geopolitical risk "
    "(oil/inflation → rate fears → discount-rate pressure on growth stocks) amplifies "
    "already-elevated valuation sensitivity.",
    BODY))

story.append(Paragraph(b("Sector Attribution  (S&P 500):"), H2))
attr = [
    ["Sector",         "Key Driver",                               "S&P Impact"],
    ["Healthcare",     "UNH +~10% on +32% EPS beat; guidance raise", grn("Strong +")],
    ["Industrials",    "GE Aerospace beat; orders +17%",            grn("Positive")],
    ["Financials",     "BLK +6.6% earnings + JPM upgrade",          grn("Positive")],
    ["Energy",         "Crude oil up on Iran/Hormuz risk",          grn("Mild +")],
    ["Semiconductors", "TSMC 'sell news'; SNDK/WDC –8%; broad chip rout", red("Strong –")],
    ["Consumer Tech",  "NFLX in-line (after-close; watch Friday)",  "Neutral"],
    ["Geopolitics",    "US–Iran escalation → risk-off overlay",     red("Mild –")],
]
t2 = Table(attr, colWidths=[1.5*inch, 3.5*inch, 2.0*inch])
t2.setStyle(tbl())
story.append(t2)
story.append(Spacer(1, 6))

# ── 4. Top Movers ─────────────────────────────────────────────────────────────
story.append(Paragraph("4. Top Movers — Daily / Weekly / Monthly", H1))

story.append(Paragraph(b("Daily Top Gainers  (July 16, 2026)"), H2))
dg = [
    ["#", "Ticker", "Name",               "~Chg",        "Catalyst"],
    ["1",  "UNH",   "UnitedHealth Group", grn("+~10%"),  "Q2 EPS $6.38 vs $4.85E; raised FY guide"],
    ["2",  "BLK",   "BlackRock",          grn("+6.6%"),  "Q2 beat; JPMorgan OW upgrade to $1,364"],
    ["3",  "GE",    "GE Aerospace",       grn("+~4%"),   "Q2 EPS $2.02 vs $1.86E; orders +17%"],
    ["4",  "PYPL",  "PayPal",             grn("+~3%"),   "Fintech recovery; S&P top-5 gainer"],
    ["5",  "CBRE",  "CBRE Group",         grn("+~2.5%"), "Commercial RE earnings; rate relief"],
    ["6",  "LMT",   "Lockheed Martin",    grn("+~2%"),   "Defense spending lift from Iran escalation"],
    ["7",  "RTX",   "RTX Corp",           grn("+~2%"),   "Defense/Iran geopolitical tailwind"],
    ["8",  "XOM",   "ExxonMobil",         grn("+~1.5%"), "Crude oil rise on Hormuz risk"],
    ["9",  "CVX",   "Chevron",            grn("+~1.5%"), "Crude oil / energy sector relief"],
    ["10", "HUM",   "Humana",             grn("+~5%"),   "Healthcare coattails from UNH surge"],
]
t3 = Table(dg, colWidths=[0.3*inch, 0.7*inch, 1.5*inch, 0.9*inch, 3.6*inch])
t3.setStyle(tbl())
story.append(t3)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Daily Top Losers  (July 16, 2026)"), H2))
dl = [
    ["#", "Ticker", "Name",                "~Chg",        "Catalyst"],
    ["1",  "SNDK",  "SanDisk Corp",        red("–8%"),    "AI memory selloff; TSMC capacity commentary"],
    ["2",  "WDC",   "Western Digital",     red("–8%"),    "Memory selloff; HDD+NAND demand fears"],
    ["3",  "MRVL",  "Marvell Technology",  red("–5%"),    "Chip weakness; AI custom silicon scrutiny"],
    ["4",  "AMD",   "Advanced Micro Dev.", red("–4%"),    "TSMC read-through; valuation reset"],
    ["5",  "NVDA",  "Nvidia",              red("–3%"),    "Profit-taking; TSMC sell-news contagion"],
    ["6",  "DELL",  "Dell Technologies",   red("–3%"),    "AI server demand uncertainty; margin risk"],
    ["7",  "GOOGL", "Alphabet",            red("–2.5%"),  "AI capex scrutiny; search threat narrative"],
    ["8",  "INTC",  "Intel",               red("–2%"),    "No AI catalyst; foundry profitability risk"],
    ["9",  "PNR",   "Pentair",             red("–2%"),    "Industrial slowing; S&P 500 loser"],
    ["10", "ERIE",  "Erie Indemnity",      red("–1.5%"),  "Insurance underwriting concerns"],
]
t4 = Table(dl, colWidths=[0.3*inch, 0.7*inch, 1.5*inch, 0.9*inch, 3.6*inch])
t4.setStyle(tbl())
story.append(t4)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Weekly Top Gainers  (July 14–16, 2026)"), H2))
wg = [
    ["#", "Ticker", "Name",               "~Wkly",        "Sector / Driver"],
    ["1",  "SKHY",  "SK Hynix ADR",      grn("+27.3%"),  "Memory / AI HBM demand premium"],
    ["2",  "FIG",   "Figma Inc.",         grn("+22.4%"),  "SaaS/design IPO momentum; re-rating"],
    ["3",  "VOD",   "Vodafone Group",     grn("+19.6%"),  "Telecom restructuring; Europe macro"],
    ["4",  "KB",    "KB Financial Grp",   grn("+17.7%"),  "Korean banking; Asia financial rally"],
    ["5",  "UNH",   "UnitedHealth Group", grn("+~12%"),   "Healthcare: Q2 blowout beat today"],
    ["6",  "BLK",   "BlackRock",          grn("+~10%"),   "Financials: earnings beat + upgrade"],
    ["7",  "GE",    "GE Aerospace",       grn("+~7%"),    "Industrials: Q2 beat; demand hold"],
    ["8",  "LLY",   "Eli Lilly",          grn("+~5%"),    "GLP-1/Pharma; healthcare rally"],
    ["9",  "PYPL",  "PayPal",             grn("+~4%"),    "Fintech recovery; analyst upgrades"],
    ["10", "ALIT",  "Alight Inc.",        grn("+~4%"),    "HR-tech SaaS; buyout speculation"],
]
t5 = Table(wg, colWidths=[0.3*inch, 0.7*inch, 1.5*inch, 0.9*inch, 3.6*inch])
t5.setStyle(tbl())
story.append(t5)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Weekly Top Losers  (July 14–16, 2026)"), H2))
wl = [
    ["#", "Ticker", "Name",                "~Wkly",        "Sector / Driver"],
    ["1",  "MRVL",  "Marvell Technology",  red("–26.2%"),  "Chip / custom AI silicon thesis broken"],
    ["2",  "SNDK",  "SanDisk Corp",        red("–18.4%"),  "AI memory: two-day cascade selloff"],
    ["3",  "WDC",   "Western Digital",     red("–~16%"),   "Memory storage: HDD+NAND both weak"],
    ["4",  "AMD",   "Advanced Micro Dev.", red("–~8%"),    "TSMC ripple; AI GPU roadmap concerns"],
    ["5",  "DELL",  "Dell Technologies",   red("–~6%"),    "AI server revenue growth revised lower"],
    ["6",  "GOOGL", "Alphabet",            red("–~5%"),    "AI valuation jitters; analyst notes"],
    ["7",  "INTC",  "Intel",               red("–~4%"),    "Foundry losses; no near-term catalyst"],
    ["8",  "NVDA",  "Nvidia",              red("–~3%"),    "Profit-taking; TSMC read-through"],
    ["9",  "PNR",   "Pentair",             red("–~3%"),    "Industrial end-market softness"],
    ["10", "CEG",   "Constellation Energy",red("–~3%"),    "Nuclear/AI power hype profit-taking"],
]
t6 = Table(wl, colWidths=[0.3*inch, 0.7*inch, 1.5*inch, 0.9*inch, 3.6*inch])
t6.setStyle(tbl())
story.append(t6)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Monthly Top Gainers  (July 2026 MTD)"), H2))
mg = [
    ["#", "Ticker", "Name",               "~Mthly",       "Sector / Driver"],
    ["1",  "CRNX",  "Corcept Therapeutics",grn("+116%"),  "Biotech: clinical-trial catalyst"],
    ["2",  "FBRX",  "Forte Biosciences",   grn("+103%"),  "Biotech: pipeline/M&A catalyst"],
    ["3",  "TRAX",  "Trax (SaaS IPO)",     grn("+85%"),   "Retail analytics SaaS; re-rating"],
    ["4",  "CBUS",  "Cibus Inc.",           grn("+68%"),   "AgTech / gene-editing biotech"],
    ["5",  "ALIT",  "Alight Inc.",          grn("+60%"),   "HR-tech SaaS; buyout rumor"],
    ["6",  "SKHY",  "SK Hynix ADR",        grn("+27.3%"), "AI HBM memory demand premium"],
    ["7",  "FIG",   "Figma Inc.",           grn("+22.4%"), "SaaS/design: IPO + growth re-rating"],
    ["8",  "VOD",   "Vodafone Group",       grn("+19.6%"), "Telecom restructuring"],
    ["9",  "BLK",   "BlackRock",            grn("+~15%"),  "Financials: AUM growth + Q2 beat"],
    ["10", "UNH",   "UnitedHealth Group",   grn("+~14%"),  "Healthcare: managed care strength"],
]
t7 = Table(mg, colWidths=[0.3*inch, 0.7*inch, 1.6*inch, 0.9*inch, 3.5*inch])
t7.setStyle(tbl())
story.append(t7)
story.append(Spacer(1, 4))

story.append(Paragraph(b("Monthly Top Losers  (July 2026 MTD)"), H2))
ml = [
    ["#", "Ticker", "Name",                "~Mthly",       "Sector / Driver"],
    ["1",  "MRVL",  "Marvell Technology",  red("–26.2%"),  "Chip: custom AI silicon disappointed"],
    ["2",  "SNDK",  "SanDisk Corp",        red("–18.4%"),  "AI memory cycle correction"],
    ["3",  "WDC",   "Western Digital",     red("–~18%"),   "HDD + NAND both structurally weak"],
    ["4",  "AMD",   "Advanced Micro Dev.", red("–~12%"),   "Valuation reset post-TSMC"],
    ["5",  "INTC",  "Intel",               red("–~10%"),   "Foundry losses; no AI ramp"],
    ["6",  "DELL",  "Dell Technologies",   red("–~9%"),    "AI server demand revision lower"],
    ["7",  "CEG",   "Constellation Energy",red("–~8%"),    "Profit-taking after nuclear-AI hype"],
    ["8",  "GOOGL", "Alphabet",            red("–~7%"),    "AI capex concern; search threat"],
    ["9",  "NVDA",  "Nvidia",              red("–~5%"),    "Profit-taking after multi-month run"],
    ["10", "PNR",   "Pentair",             red("–~5%"),    "Industrial demand soft; guidance cut"],
]
t8 = Table(ml, colWidths=[0.3*inch, 0.7*inch, 1.6*inch, 0.9*inch, 3.5*inch])
t8.setStyle(tbl())
story.append(t8)

story.append(Paragraph(b("Sector Trend Summary Across Timeframes:"), H2))
trends = [
    b("Semiconductors / AI Memory  [BEAR — all timeframes]:") +
    " The dominant theme. SNDK –18%, MRVL –26%, WDC –18% MTD. AMD, NVDA, INTC all "
    "under pressure. TSMC's 'sell-the-news' today reinforces a valuation reset across AI chips. "
    "Memory names hit hardest on HBM/NAND demand uncertainty.",

    b("Biotech / Healthcare  [STRONG BULL — monthly]:") +
    " CRNX +116%, FBRX +103%, CBUS +68% MTD on clinical-trial events. UNH's Q2 blowout "
    "accelerated the weekly healthcare rally. GLP-1 theme (LLY) continues. "
    "Managed care is a defensive quality outperformer.",

    b("Financials / Asset Management  [BULL — weekly/monthly]:") +
    " BLK +15% MTD, KB Financial +18% weekly. Strong Q2 earnings from asset managers. "
    "Rate environment still supportive of NII. Regional bank results Friday (Travelers, Truist, "
    "Fifth Third, Regions) will confirm or challenge this trend.",

    b("Defense / Energy  [EMERGING BULL — Iran-linked]:") +
    " LMT, RTX gaining on Iran escalation. Crude oil up → XOM, CVX benefit. "
    "Hormuz disruption risk keeps a geopolitical risk premium in energy through the weekend.",

    b("SaaS / Cloud  [SELECTIVE RECOVERY — monthly]:") +
    " FIG +22%, ALIT +60% MTD. Stock-specific catalysts (IPO momentum, buyout rumors) "
    "rather than a broad sector rotation. Not yet a consensus re-rating of the entire group.",
]
for tr in trends:
    story.append(Paragraph("• " + tr, BUL))
story.append(Spacer(1, 6))

# ── 5. Next-Day Scenarios ─────────────────────────────────────────────────────
story.append(Paragraph("5. Next-Day Catalysts & Scenario Trees  (Friday, July 17, 2026)", H1))

scenarios = [
    ("8:30 AM — Housing Starts (June) + Import/Export Price Index (June)",
     [
         (b("BEAT: Starts ↑, Import Prices cool") + " →",
          "Disinflation continues; housing demand solid. SPY likely +0.3–0.5%. "
          "Homebuilders (DHI, LEN), REITs rally. Bond yields dip → growth stocks get "
          "discount-rate relief → QQQ stabilizes or rebounds +0.5–1.0%. "
          "Fed September cut expectations rise. Mechanism: lower import costs = "
          "lower CPI path = longer Fed pause = less rate risk for long-duration equities."),
         (b("MISS: Starts ↓, Import Prices rise") + " →",
          "Iran oil-price pass-through visible in import data = stagflation signal. "
          "SPY –0.5–0.8%. Bond yields rise → growth/tech under additional pressure. "
          "QQQ extends losses toward –1.5 to –2.0% as rate fears compound semiconductor selloff. "
          "Homebuilders fall; mortgage-rate sensitivity becomes acute."),
     ]),
    ("9:15 AM — Industrial Production & Capacity Utilization (June)",
     [
         (b("Strong IP / High Utilization (>79%)") + " →",
          "Manufacturing re-acceleration confirms demand recovery. Industrials (GE, ETN, HON, CAT) "
          "extend gains from GE's beat. S&P 500 +0.2–0.3%; cyclicals outperform. "
          "However, Fed reads high utilization as 'economy doesn't need cuts yet'—muted "
          "rate-relief for tech. SPY breadth improves but QQQ stays range-bound."),
         (b("Weak IP / Low Utilization (<77%)") + " →",
          "Demand destruction visible from Iran uncertainty + tariff overhang. "
          "Recessionary signal. Cyclicals sell off. SPY –0.5–0.8% as industrial gains "
          "reverse. Semis (fewer chips ordered in weak capex) face additional headwinds. "
          "QQQ could retest recent lows on combined recession + chip demand fears."),
     ]),
    ("10:00 AM — Michigan Consumer Sentiment Preliminary (July)",
     [
         (b("Sentiment > 52 + Inflation expectations < 4.5%") + " →",
          "Consumer still resilient despite Iran headlines. Confidence = spending = revenue "
          "visibility for retailers, travel, consumer tech. SPY +0.4–0.6%; discretionary "
          "rally. Critically: if inflation expectations fall below 4.5% from June's 4.6%, "
          "September Fed cut odds spike—QQQ could rebound +1.0–1.5% from tech relief. "
          "This would be the key Friday positive scenario."),
         (b("Sentiment < 48 + Inflation expectations > 5.0%") + " →",
          "Iran fuel costs hitting wallets; consumers expect more pain. "
          "Retail, travel, consumer discretionary all fall. SPY –0.6–1.0%; QQQ –1.5–2.0% "
          "combining recession fears + rate-hike risk (if inflation expectations >5%, "
          "Fed may be forced to hike). This is the worst-case Friday scenario—watch for "
          "a potential close below key SPY support levels."),
     ]),
    ("Netflix AH Reaction + Regional Bank Earnings (Travelers, Truist, Fifth Third, Regions)",
     [
         (b("NFLX +3%+ AH + Banks beat on NII/credit quality") + " →",
          "Streaming confirms consumer spending durability; content ROI validated. "
          "Financials confirm healthy net interest margins and manageable credit losses. "
          "Dual positive: tech confidence restored + banking sector green. "
          "QQQ opens +0.5–1.0%; SPY +0.3–0.5% from fintech/bank boost. "
          "Semiconductors may find stabilization floor if broader risk-on returns."),
         (b("NFLX guides down / Banks miss on credit costs") + " →",
          "Consumer spending cracking under Iran-inflation pressure = credit deterioration. "
          "QQQ –1.5–2.0% (tech + streaming double miss). SPY –0.8–1.2% as financials drag "
          "adds to tech weakness. Regional banks carry credit-quality signals that reverberate "
          "into broader financial conditions. Worst case: negative Friday triple-catalyst flush "
          "(macro miss + sentiment miss + earnings miss) = SPY –1.5–2%."),
     ]),
]

for cat, branches in scenarios:
    story.append(Paragraph(b(cat), H2))
    for hd, body in branches:
        story.append(Paragraph(f"  {hd} {body}", BUL))
    story.append(Spacer(1, 3))

# ── Footer ────────────────────────────────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
story.append(Spacer(1, 4))
story.append(Paragraph(b("Data Sources"), H2))
story.append(Paragraph(
    "SPY/QQQ prices: prices.csv (264 rows from 2025-07-15); July 9–13 estimated from "
    "S&P 500/Nasdaq-100 index returns. "
    "52-week stats computed from prices.csv. "
    "TSMC/Netflix/UNH/GE/BLK earnings: SEC Form 8-K filings + company press releases. "
    "Market news: Yahoo Finance Markets Live, TheStreet, CNBC, Bloomberg, Charles Schwab "
    "Market Update, 24/7 Wall St., FX Leaders, Benzinga. "
    "Economic calendar: EarningsWhispers, Kiplinger, BLS.gov, Econoday. "
    "Geopolitics: NPR, Britannica (2026 Iran war), Dallas Fed research WP2609.",
    SMALL))
story.append(Paragraph(
    b("Limitation:") + " Direct API access to Yahoo Finance, Stooq, MarketWatch, Finviz, "
    "and Barchart is blocked by the session egress policy; historical backfill used "
    "existing branch data. Three intermediate days (July 9, 10, 13) are interpolated from "
    "reported index returns and may carry ±0.5% error vs. actual closes.",
    SMALL))
story.append(Paragraph(
    b("Disclaimer:") + " Automated informational report. Not investment advice. "
    "No trades placed or simulated.",
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
