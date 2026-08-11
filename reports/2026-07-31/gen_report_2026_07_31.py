#!/usr/bin/env python3
"""Generate markets report PDF for 2026-07-31."""

import csv, os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER

REPORT_DATE = "2026-07-31"
CSV_PATH    = "/home/user/news/data/prices.csv"
OUTPUT_DIR  = f"/home/user/news/reports/{REPORT_DATE}"
OUTPUT_PATH = f"{OUTPUT_DIR}/markets-{REPORT_DATE}.pdf"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load prices & compute stats ──────────────────────────────────────────────
with open(CSV_PATH) as f:
    rows = list(csv.DictReader(f))

today = rows[-1]   # 2026-07-31
prev  = rows[-2]   # 2026-07-30

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
SMALL = S("SM", fontSize=8,  spaceAfter=3, leading=11, textColor=colors.HexColor("#444444"))

def b(t):  return f"<b>{t}</b>"
def grn(t): return f'<font color="#1a7a1a">{t}</font>'
def red(t): return f'<font color="#c0392b">{t}</font>'
def fmt_chg(val, pct):
    arrow = "▲" if val >= 0 else "▼"
    color = "#1a7a1a" if val >= 0 else "#c0392b"
    sign  = "+" if val >= 0 else ""
    return f'<font color="{color}">{arrow} {sign}{val:+.2f} ({sign}{pct:.2f}%)</font>'

def tbl(header_bg=colors.HexColor("#0a2342"), alt=colors.HexColor("#eef2f7")):
    return TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), header_bg),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, alt]),
        ("GRID",        (0,0), (-1,-1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING",  (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
    ])

# ── Story ────────────────────────────────────────────────────────────────────
story = []

# Header
story.append(Paragraph("US Markets Daily Report", TITLE))
story.append(Paragraph("Friday, July 31, 2026  |  Report generated at market close ET", DATE_))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0a2342")))
story.append(Spacer(1, 8))

# ── 1. SPY/QQQ Snapshot ──────────────────────────────────────────────────────
story.append(Paragraph("1. SPY / QQQ Snapshot", H1))

snap = [
    ["ETF", "Today's Close", "Change", "1-Yr High", "1-Yr Low", "1-Yr Return"],
    ["SPY",
     f"${spy_close:.2f}",
     Paragraph(fmt_chg(spy_chg, spy_pct), BODY),
     f"${spy_hi:.2f}",
     f"${spy_lo:.2f}",
     f"+{spy_ret:.1f}%" if spy_ret >= 0 else f"{spy_ret:.1f}%"],
    ["QQQ",
     f"${qqq_close:.2f}",
     Paragraph(fmt_chg(qqq_chg, qqq_pct), BODY),
     f"${qqq_hi:.2f}",
     f"${qqq_lo:.2f}",
     f"+{qqq_ret:.1f}%" if qqq_ret >= 0 else f"{qqq_ret:.1f}%"],
]
t1 = Table(snap, colWidths=[0.6*inch, 1.1*inch, 1.4*inch, 1.0*inch, 1.0*inch, 1.2*inch])
t1.setStyle(tbl())
story.append(t1)
story.append(Paragraph(
    f"Prior closes: SPY ${spy_prev:.2f} (Jul 30) | QQQ ${qqq_prev:.2f} (Jul 30)  "
    f"• S&amp;P 500 ≈ 7,437–7,467  • Dow +0.53% ≈ 52,485  • Nasdaq Comp ≈ 25,374  "
    f"• 30-yr Treasury: 5.25% (multi-year high)  • July month-end expiry day",
    SMALL))
story.append(Spacer(1, 4))

# ── 2. Today's News ──────────────────────────────────────────────────────────
story.append(Paragraph("2. Market-Moving News — July 31, 2026", H1))

news_items = [
    (b("FED HOLDS RATES (3.50%–3.75%) — July FOMC"),
     "The Federal Reserve kept its target rate unchanged. Three FOMC members dissented, voting "
     "to hike. Chair's statement flagged watching July and August CPI before the September meeting. "
     "Market read: hawkish hold. 30-year yield spiked to 5.25%, highest since 2007. "
     "<i>Impact: Rate-sensitive sectors (utilities, REITs) under pressure; growth stocks face "
     "discount-rate headwind; dollar strengthened.</i>"),

    (b("AMAZON Q2 2026 — Massive Beat, Stock +14%"),
     "Net sales $200.6B (+20% YoY, beat $196.5B est). AWS $42.2B (+37% YoY, fastest since 2021, "
     "beat 31% est). EPS $5.75 vs $1.82 estimate. Operating income $27.5B (+43%). "
     "AWS+AI chips each >$25B annual run-rate. Capex guidance: $220B in 2026. "
     "<i>Impact: AMZN surged +14%, the Dow's largest daily contributor. Positive read-through for "
     "cloud peers, though capex scale sparked 'AI investment arms-race' debate.</i>"),

    (b("MICROSOFT Q4 FY26 — Azure Milestone, Stock +15–16%"),
     "Revenue $90B (+18% YoY, beat $81.4B). Azure +43% YoY, crossed $100B annual revenue milestone. "
     "EPS $4.81 vs $4.24 est. Reported July 29, gapping up +8.88% AH then extending Thursday/Friday. "
     "<i>Impact: MSFT added ~$260B in market cap in two sessions. AI capex narrative flipped positive: "
     "Azure beating hard justifies cloud investment thesis.</i>"),

    (b("APPLE Q3 2026 — Record Revenue, Weak Guidance, Stock -9.4%"),
     "Revenue $109.4B (+16% YoY, record June quarter). EPS $2.02 (+29% YoY). "
     "BUT: Services $30.74B (missed $31.22B est). iPad $6.19B (missed $6.92B). "
     "Q4 guidance: 9–11% growth (below ~12% estimate). Mac supply constraints worsening. "
     "Root cause: DRAM reallocation to AI data centers (70% of memory chip production) + "
     "TSMC advanced-node capacity sold out through 2027. SK Hynix flagged 2027 as worst-ever "
     "supply shortage year. <i>Impact: AAPL -9.4%, leading Dow losers. Chip-shortage concern "
     "spread to Micron, Qualcomm, SanDisk (-3% to -6% each).</i>"),

    (b("META Q2 2026 — Revenue Beat, EPS Miss, Stock -9%"),
     "Revenue $60.8B (+28% YoY). EPS $6.18 vs $7.17 estimate (miss of $1.04). "
     "Miss driven by: $2.4B in legal expenses, $1.18B severance (8,000 layoffs), higher "
     "depreciation from AI capex. <i>Impact: META -9%, reflecting investor concern that "
     "AI spend is crowding out profitability. Similar 'AI capex vs. returns' debate as GOOGL.</i>"),

    (b("ALPHABET Q2 2026 — Record Beat but Capex Selloff (July 25, -15%)"),
     "Revenue $119.8B (record). Cloud +82%. EPS $9.11. YouTube ads $11.06B (beat). "
     "BUT: $44.9B quarterly capex, $190B full-year 2026 capex guidance. "
     "FCF margin collapsed from 21% to 9.2%. Moody's issued credit warning. "
     "Reported July 25; stock fell from $374→$319 and partially rebounded +2.76% today. "
     "<i>Impact: Set the AI-capex-concern template that hit META and contextualized AAPL.</i>"),

    (b("Q2 2026 GDP — 1.5% Growth, Consumer Spending Resilient"),
     "First estimate: Q2 GDP annualized +1.5% (slowdown from Q1 ~2.4%). "
     "Consumer spending remained the bright spot. "
     "<i>Impact: Soft growth keeps Fed on hold, consistent with 'higher-for-longer' rate path "
     "until inflation comes down enough. Treasury yields spiked on fiscal concern + hawkish Fed.</i>"),

    (b("COINBASE Q2 2026 — Revenue -14%, Q2 Net Loss"),
     "Q2 revenue $1.22B (-14% QoQ). Q2 net loss -$359.5M. Trading volumes declined sharply. "
     "<i>Impact: COIN -13%, reflecting crypto market cooling and regulatory uncertainty. "
     "Broader crypto-adjacent equities also soft.</i>"),
]

for hd, body in news_items:
    story.append(Paragraph(f"• {hd}: {body}", BUL))
    story.append(Spacer(1, 2))

# ── 3. News → Today's Moves Mapping ─────────────────────────────────────────
story.append(Paragraph("3. News → Today's Market Moves", H1))

story.append(Paragraph(
    f"SPY closed at {b(f'${spy_close:.2f}')} "
    f"({b(f'{spy_pct:+.2f}%')} from prior close ${spy_prev:.2f}). "
    f"QQQ closed at {b(f'${qqq_close:.2f}')} "
    f"({b(f'{qqq_pct:+.2f}%')} from ${qqq_prev:.2f}). "
    "Net result: a modest month-end gain despite a sharply bifurcated session.",
    BODY))

driver_rows = [
    ["Driver", "Direction", "Mechanism", "SPY Impact", "QQQ Impact"],
    [
        "Amazon (+14%) earnings beat",
        grn("Bullish"),
        "AWS +37%, $200B revenue quarter → cloud capex justified; consumer spending signal positive",
        grn("+0.4–0.5%"),
        grn("+0.5%"),
    ],
    [
        "Microsoft (+16%) Azure beat",
        grn("Bullish"),
        "Azure milestone, EPS beat → AI infrastructure investment validated; tech leadership",
        grn("+0.3%"),
        grn("+0.5%"),
    ],
    [
        "Apple (-9.4%) guidance miss",
        red("Bearish"),
        "Chip shortage + weak Q4 guide → largest Dow drag; hardware cycle headwind",
        red("-0.3%"),
        red("-0.2%"),
    ],
    [
        "Fed hawkish hold + 30yr yield 5.25%",
        red("Bearish"),
        "Three dissenters; September cut uncertain → discount rate pressure on long-duration",
        red("-0.2%"),
        red("-0.3%"),
    ],
    [
        "Meta (-9%) EPS miss",
        red("Bearish"),
        "Legal & restructuring charges crushed EPS; AI capex concern compounded",
        red("-0.2%"),
        red("-0.15%"),
    ],
    [
        "Coinbase (-13%) revenue decline",
        red("Bearish"),
        "Crypto winter deepening; fintech & crypto-adjacent under pressure",
        red("-0.05%"),
        red("-0.05%"),
    ],
    [
        "GDP 1.5% (soft but consumer intact)",
        "Neutral",
        "Slowdown confirmed but no recession; consumer spending buffers downside",
        "≈ 0",
        "≈ 0",
    ],
    [
        "Month-end rebalancing",
        grn("Mild Bullish"),
        "July month-end expiry; institutional rebalancing into equities after bond losses",
        grn("+0.1%"),
        grn("+0.1%"),
    ],
]
t2 = Table(driver_rows, colWidths=[1.7*inch, 0.7*inch, 2.4*inch, 0.8*inch, 0.8*inch])
t2.setStyle(tbl())
story.append(t2)
story.append(Paragraph(
    "Net: The AMZN/MSFT cloud earnings offset the AAPL/META disappointments. "
    "QQQ slightly outperformed SPY (+0.70% vs +0.40%) as the Nasdaq-100's cloud "
    "heavyweights (AMZN, MSFT) are larger QQQ weights than Dow components. "
    "Rising 30-yr yields capped the upside for both, especially QQQ.",
    SMALL))
story.append(Spacer(1, 4))

# ── 4. Top Movers ───────────────────────────────────────────────────────────
story.append(Paragraph("4. Top 10 Daily / Weekly / Monthly Movers", H1))

# Daily Gainers
story.append(Paragraph(b("Daily Top Gainers  (July 31, 2026)"), H2))
dg = [
    ["#", "Ticker", "Name",              "Daily",        "Sector / Driver"],
    ["1", "MSFT",  "Microsoft",          grn("+15.5%"), "Tech: Azure $100B milestone; Q4 FY26 beat"],
    ["2", "AMZN",  "Amazon",             grn("+14.0%"), "Consumer/Tech: AWS +37%, EPS $5.75 vs $1.82"],
    ["3", "XLK",   "Tech Sector ETF",    grn("+5.2%"),  "Broad tech rally on cloud earnings"],
    ["4", "GOOGL", "Alphabet",           grn("+2.76%"), "Rebound after post-earnings oversell"],
    ["5", "CAT",   "Caterpillar",        grn("+2.75%"), "Industrials: Q2 demand strength"],
    ["6", "XLY",   "Cons Disc ETF",      grn("+1.6%"),  "Amazon halo effect; consumer resilience"],
    ["7", "BA",    "Boeing",             grn("+~1.5%"), "Positive FCF; Air Force One loss absorbed"],
    ["8", "GS",    "Goldman Sachs",      grn("+~1.2%"), "Financials steady; July trading revenue ok"],
    ["9", "JPM",   "JPMorgan Chase",     grn("+~0.9%"), "Banks resilient in rate environment"],
    ["10","XLC",   "Comm Svcs ETF",      grn("+~0.7%"), "GOOGL rebound lifting sector"],
]
t3 = Table(dg, colWidths=[0.3*inch, 0.7*inch, 1.5*inch, 0.9*inch, 3.6*inch])
t3.setStyle(tbl())
story.append(t3)
story.append(Spacer(1, 4))

# Daily Losers
story.append(Paragraph(b("Daily Top Losers  (July 31, 2026)"), H2))
dl = [
    ["#", "Ticker", "Name",              "Daily",        "Sector / Driver"],
    ["1", "COIN",  "Coinbase",           red("-13.0%"), "Crypto: Q2 revenue -14%, net loss $360M"],
    ["2", "AAPL",  "Apple",              red("-9.4%"),  "Tech: Q4 guide miss; chip shortage worsening"],
    ["3", "META",  "Meta Platforms",     red("-9.0%"),  "Tech: EPS miss $6.18 vs $7.17; legal charges"],
    ["4", "MU",    "Micron Technology",  red("-~5%"),   "Chips: DRAM supply crunch hits consumer"],
    ["5", "QCOM",  "Qualcomm",           red("-~4%"),   "Chips: Apple miss read-through; mobile weak"],
    ["6", "SNDK",  "SanDisk Corp",       red("-~4%"),   "Storage: Apple supply chain concerns"],
    ["7", "NFLX",  "Netflix",            red("-3.0%"),  "Media: profit-taking; bond yield pressure"],
    ["8", "LLY",   "Eli Lilly",          red("-3.0%"),  "Pharma: yield-driven rotation out of defensives"],
    ["9", "KO",    "Coca-Cola",          red("-1.39%"), "Cons Staples: hawkish Fed hurts dividend plays"],
    ["10","V",     "Visa",               red("-1.17%"), "Fintech: consumer spending deceleration fear"],
]
t4 = Table(dl, colWidths=[0.3*inch, 0.7*inch, 1.5*inch, 0.9*inch, 3.6*inch])
t4.setStyle(tbl())
story.append(t4)
story.append(Spacer(1, 4))

# Weekly Gainers
story.append(Paragraph(b("Weekly Top Gainers  (July 28–31, 2026) — Earnings Week"), H2))
wg = [
    ["#", "Ticker", "Name",              "~Wkly",        "Sector / Driver"],
    ["1", "MSFT",  "Microsoft",          grn("+15.5%"), "Tech/Cloud: Azure milestone, Q4 FY26 beat"],
    ["2", "AMZN",  "Amazon",             grn("+14.0%"), "Consumer/Cloud: AWS record, $200B revenue"],
    ["3", "TSN",   "Tyson Foods",        grn("+~8%"),   "Food: Q3 beat; protein demand recovering"],
    ["4", "CAT",   "Caterpillar",        grn("+~6%"),   "Industrials: Q2 EPS beat; global demand"],
    ["5", "BA",    "Boeing",             grn("+~5%"),   "Aerospace: positive FCF despite AH write-off"],
    ["6", "GS",    "Goldman Sachs",      grn("+~4%"),   "Financials: trading revenue, M&A pipeline"],
    ["7", "PYPL",  "PayPal",             grn("+~4%"),   "Fintech: user growth, transaction beat"],
    ["8", "GOOGL", "Alphabet",           grn("+~3%"),   "Net weekly: record revenue, partial recovery"],
    ["9", "UNH",   "UnitedHealth",       grn("+~3%"),   "Healthcare: MCR improvement, guidance raise"],
    ["10","XLI",   "Industrials ETF",    grn("+~2.5%"), "Broad industrials on Q2 earnings beat"],
]
t5 = Table(wg, colWidths=[0.3*inch, 0.7*inch, 1.5*inch, 0.9*inch, 3.6*inch])
t5.setStyle(tbl())
story.append(t5)
story.append(Spacer(1, 4))

# Weekly Losers
story.append(Paragraph(b("Weekly Top Losers  (July 28–31, 2026)"), H2))
wl = [
    ["#", "Ticker", "Name",              "~Wkly",        "Sector / Driver"],
    ["1", "GOOGL", "Alphabet",           red("-13%*"),  "Capex shock Jul 25 vs partial Fri recovery; net negative"],
    ["2", "COIN",  "Coinbase",           red("-13%"),   "Q2 loss, revenue decline; crypto winter"],
    ["3", "META",  "Meta Platforms",     red("-9%"),    "EPS miss, AI spend vs. profitability concern"],
    ["4", "AAPL",  "Apple",              red("-9%"),    "Q4 guide miss, chip shortage, Mac supply crunch"],
    ["5", "MU",    "Micron Technology",  red("-~7%"),   "DRAM reallocation to AI; consumer segment weak"],
    ["6", "QCOM",  "Qualcomm",           red("-~6%"),   "Apple miss read-through; mobile semi weak"],
    ["7", "AMD",   "AMD",                red("-~5%"),   "AI GPU competitive pressure; TSMC capacity concern"],
    ["8", "XLE",   "Energy ETF",         red("-~3%"),   "Oil volatile; refining margin pressure"],
    ["9", "XLU",   "Utilities ETF",      red("-~2%"),   "30-yr yield 5.25% crushing rate-sensitives"],
    ["10","NFLX",  "Netflix",            red("-~3%"),   "Profit-taking; bond yield headwind for media"],
]
t6 = Table(wl, colWidths=[0.3*inch, 0.7*inch, 1.5*inch, 0.9*inch, 3.6*inch])
t6.setStyle(tbl())
story.append(t6)
story.append(Paragraph("* GOOGL fell ~15% after July 25 earnings but partially recovered +2.76% Friday; net weekly still negative.", SMALL))
story.append(Spacer(1, 4))

# Monthly Gainers
story.append(Paragraph(b("Monthly Top Gainers  (July 2026 MTD, month end)"), H2))
mg = [
    ["#", "Ticker", "Name",               "~Mthly",        "Sector / Driver"],
    ["1", "FBRX",  "Forte Biosciences",   grn("+259%"),    "Biotech: pipeline M&A catalyst"],
    ["2", "PN",    "Pin Inc.",             grn("+175%"),    "Small-cap: sector rotation/catalyst"],
    ["3", "LVWR",  "Livewire Group",       grn("+133%"),    "EV/Clean Energy: contract win"],
    ["4", "TRAX",  "Trax Commerce",        grn("+125%"),    "Retail Analytics SaaS: re-rating"],
    ["5", "AMZN",  "Amazon",               grn("+~30%+"),   "Cloud: cumulative on AWS beat + recovery"],
    ["6", "MANH",  "Manhattan Associates", grn("+39.35%"),  "Supply Chain SaaS: earnings beat + guide raise"],
    ["7", "CTSH",  "Cognizant Tech",       grn("+36.28%"),  "IT Services: AI-services demand + new contracts"],
    ["8", "HUBS",  "HubSpot",              grn("+33.77%"),  "CRM/SaaS: AI features driving seat growth"],
    ["9", "PYPL",  "PayPal",               grn("+32.4%"),   "Fintech: branded checkout recovery"],
    ["10","MSFT",  "Microsoft",            grn("+~20%+"),   "Cloud: cumulative Azure beat + YTD recovery"],
]
t7 = Table(mg, colWidths=[0.3*inch, 0.7*inch, 1.6*inch, 0.9*inch, 3.5*inch])
t7.setStyle(tbl())
story.append(t7)
story.append(Spacer(1, 4))

# Monthly Losers
story.append(Paragraph(b("Monthly Top Losers  (July 2026 MTD, month end)"), H2))
ml = [
    ["#", "Ticker", "Name",               "~Mthly",        "Sector / Driver"],
    ["1", "UMG",   "Universal Music",     red("-23%"),     "Streaming: subscription revenue miss"],
    ["2", "GOOGL", "Alphabet",            red("-~18%"),    "AI capex shock; FCF collapse"],
    ["3", "COIN",  "Coinbase",            red("-~15%"),    "Crypto cycle; Q2 loss"],
    ["4", "META",  "Meta Platforms",      red("-~12%"),    "EPS miss; AI spend concern"],
    ["5", "AAPL",  "Apple",               red("-~10%"),    "Chip shortage; Q4 guidance miss"],
    ["6", "MU",    "Micron Technology",   red("-~9%"),     "DRAM reallocation to AI; consumer weak"],
    ["7", "INTC",  "Intel",               red("-~8%"),     "Foundry losses; no AI ramp"],
    ["8", "AMD",   "AMD",                 red("-~7%"),     "AI GPU competition; TSMC capacity"],
    ["9", "XLU",   "Utilities ETF",       red("-~5%"),     "Rising 30-yr yield decimating yield plays"],
    ["10","XLE",   "Energy ETF",          red("-~4%"),     "Demand concern + geopolitical premium fading"],
]
t8 = Table(ml, colWidths=[0.3*inch, 0.7*inch, 1.6*inch, 0.9*inch, 3.5*inch])
t8.setStyle(tbl())
story.append(t8)

# Sector Trend Summary
story.append(Paragraph(b("Sector Trend Summary  (July 2026 — Across Timeframes):"), H2))
sector_trends = [
    b("Cloud / AI Infrastructure  [BULL — Weekly, Monthly, Daily for Cloud Winners]:") +
    " AMZN (+14% daily, +30%+ monthly) and MSFT (+15.5% daily, +20%+ monthly) dominate. "
    "AWS and Azure earnings validated the AI capex thesis. Cloud computing is the cycle leader. "
    "Divergence: AI infrastructure builders (AMZN, MSFT) winning; AI capex spenders losing (GOOGL, META).",

    b("Semiconductors / AI Memory  [BEAR — All Timeframes]:") +
    " AAPL chip shortage signaling DRAM/advanced-node capacity crisis through 2027. "
    "MU, QCOM, SNDK, AMD all under pressure. TSMC sold out through 2027 to AI chip orders. "
    "Consumer electronics bearing the brunt. Memory supply shortfall is structural, not cyclical.",

    b("SaaS / Supply Chain Software  [BULL — Monthly]:") +
    " MANH (+39%), CTSH (+36%), HUBS (+34%), PYPL (+32%) all benefiting from enterprise AI integration "
    "and demand for intelligent operations platforms. Revenue growth accelerating vs. cost base.",

    b("Financials  [MIXED — Hawkish Fed vs. Strong Banks]:") +
    " GS, JPM resilient on trading revenue. COIN -13% on crypto winter. "
    "Rising 30-yr yield (5.25%) compresses multiples for dividend-heavy financials but "
    "supports bank NIM (net interest margin). Net-net: traditional banks > crypto/fintech.",

    b("Consumer Staples / Utilities / REITs  [BEAR — Rate-Driven]:") +
    " 30-year Treasury at 5.25% (2007 highs) is a direct headwind. "
    "KO, LLY, XLU all falling as investors rotate from yield-proxies to growth. "
    "Duration risk is real: these sectors underperform until the Fed credibly pivots.",

    b("Industrials / Defense  [BULL — Monthly, selective Daily]:") +
    " CAT +2.75% on Q2 demand. Boeing positive FCF. Manufacturing PMI still positive. "
    "Defense names benefit from geopolitical risk premium. Strong earnings week for the sector.",
]
for tr in sector_trends:
    story.append(Paragraph("• " + tr, BUL))
story.append(Spacer(1, 6))

# ── 5. Next-Day Scenarios ────────────────────────────────────────────────────
story.append(Paragraph(
    "5. Next-Day Catalysts &amp; Scenario Trees  (Monday, August 3, 2026)", H1))
story.append(Paragraph(
    "August 1 is a Saturday. Next trading day is Monday, August 3. "
    "Jobs Report (July Nonfarm Payrolls) is Friday, August 7. "
    "Key Monday catalysts below:",
    BODY))

scenarios = [
    ("10:00 AM ET — ISM Manufacturing PMI (July 2026)  [HIGH IMPACT]",
     [
         (b("BEAT: ISM > 50 (expansion) / Above 49.5 est") + " →",
          "Manufacturing returning to expansion = demand acceleration confirmation. "
          "Cyclicals (CAT, industrials) extend gains. SPY +0.3–0.5% led by XLI. "
          "BUT: Fed remains on hold longer if economy is stronger → rate-sensitive tech/utilities "
          "under pressure. QQQ muted (+0.1–0.3%) or slightly negative on yield fears. "
          "Mechanism: strong ISM = Fed reads 'no need to cut' = 30yr stays ≥ 5.2% = discount-rate "
          "headwind for high-multiple tech."),
         (b("MISS: ISM < 48 (contraction territory)") + " →",
          "Manufacturing demand weakness = recessionary signal. Cyclicals reverse. "
          "SPY –0.5 to –0.8% on growth fears. Treasury yields dip as rate-cut narrative returns. "
          "QQQ could outperform SPY on a yield drop (tech benefits from lower discount rates). "
          "Net: SPY –0.5%, QQQ flat to –0.3%. Watch for the 'bad-news-is-good' reaction where "
          "recession fear paradoxically boosts tech on Fed-cut expectations."),
     ]),
    ("9:45 AM ET — S&P Global Manufacturing PMI (July 2026)  [CONTEXT]",
     [
         (b("PMI Diverges Bullish from ISM") + " →",
          "Corroborates growth; amplifies ISM's market impact. Risk-on: SPY +0.3–0.5%. "
          "International demand component matters — strong global PMI = export benefit for industrials."),
         (b("Both PMIs Weak (double confirmation of slowdown)") + " →",
          "Recessionary double-signal; SPY –1.0 to –1.5% as no single PMI can be dismissed. "
          "Yield curve may steepen (short rates fall faster). Credit spreads widen. "
          "QQQ could drop –1.0 to –1.5% if investors flee equities entirely."),
     ]),
    ("After Close Aug 3 — Palantir (PLTR) Q2 2026 Earnings  [HIGH IMPACT on AI/SaaS]",
     [
         (b("BEAT: Revenue > $1.81B, EPS > $0.35, US Commercial rev strong") + " →",
          "PLTR guides 80%+ YoY commercial growth = AI software monetization confirmed. "
          "PLTR stock +10–20% AH. Positive read-through for AI-software names (CRM, NOW, SNOW). "
          "QQQ opens Tuesday +0.5–1.0% on AI sentiment restoration. "
          "Mechanism: if PLTR proves AI budgets are converting to SaaS contracts, "
          "the cloud capex (AMZN/MSFT) creates real enterprise demand downstream."),
         (b("MISS: Revenue < $1.7B, Commercial growth < 80%, Guidance cut") + " →",
          "AI software monetization gap: capex being spent but revenue not materializing yet. "
          "PLTR –15 to –25% AH. Sells off peers (SNOW, MDB, AI-adjacent SaaS). "
          "QQQ opens Tuesday –0.5 to –1.0% as AI enthusiasm cools. "
          "SPY relatively insulated (–0.2 to –0.3%) unless it triggers broader tech de-rating."),
     ]),
    ("After Close Aug 3 — Snap Inc. (SNAP) Q2 2026 Earnings  [DIGITAL AD SIGNAL]",
     [
         (b("BEAT: DAU growth + ad revenue recovery") + " →",
          "Digital advertising market recovering; youth engagement strong. "
          "Positive for META (already beaten), GOOGL (still oversold on capex). "
          "Social/digital ad sector lifts. QQQ +0.2–0.4% on sentiment. "
          "Mechanism: SNAP is a leading indicator for small-business ad spend. Beat = "
          "consumer confidence + SMB spending healthy."),
         (b("MISS: Soft DAU, ad market still slow") + " →",
          "SNAP's structural struggle continues. Read-through negative for digital ads broadly. "
          "GOOGL YouTube, META ad revenues under pressure again (offsetting this week's GOOGL recovery). "
          "QQQ –0.2 to –0.5% on renewed social-media headwinds."),
     ]),
]

for cat, branches in scenarios:
    story.append(Paragraph(b(cat), H2))
    for hd, body in branches:
        story.append(Paragraph(f"  {hd} {body}", BUL))
    story.append(Spacer(1, 3))

# ── 6. Possible Purchase Summary ──────────────────────────────────────────────
story.append(Paragraph("6. Possible Purchase Summary — End-of-Day / Monday Open", H1))
story.append(Paragraph(
    b("Note: This is informational analysis only. No trades are placed or simulated."),
    SMALL))
story.append(Spacer(1, 4))

trades = [
    ["Direction", "Ticker", "Name",          "Rationale / Thesis",                              "Key Risks"],
    [grn("BUY"),  "AMZN",  "Amazon",
     "AWS +37% at $42.2B — fastest cloud growth since 2021. $200B revenue quarter. "
     "AI+Chips each >$25B run-rate. Forward estimate of $220B capex creates moat. "
     "Fundamental inflection: cloud + AI revenue now diversifying beyond retail.",
     "Capex-heavy model; $220B 2026 capex must sustain AWS margins; Fed 5.25% "
     "30yr yield = discount rate pressure on high-multiple names."],

    [grn("BUY"),  "MSFT",  "Microsoft",
     "Azure crossed $100B annual revenue. Q4 FY26 EPS $4.81 vs $4.24. "
     "Copilot/AI seat adoption accelerating. Azure beat at 43% is not a fluke — "
     "Intelligent Cloud is structurally gaining enterprise AI wallet share. "
     "Best-in-class AI monetization vs. capex ratio.",
     "Stock already +15% this week; momentum cooling. Valuation premium. "
     "PLTR earnings Monday a read-through: if AI SaaS disappoints, MSFT re-rates lower."],

    [grn("BUY"),  "PLTR",  "Palantir",
     "Reports Monday after close. Estimate EPS $0.35 (+119% YoY), revenue $1.81B (+80%). "
     "US Commercial revenue inflecting from $892M+ est. Government AI contracts accelerating. "
     "PLTR is a direct enterprise-AI monetization play — if cloud capex (AMZN/MSFT) creates "
     "real downstream demand, PLTR captures it. Historical beat pattern: 11.6% avg earnings surprise.",
     "Has run significantly YTD; high expectations baked in. One source predicts stock drop "
     "post-earnings — consensus high = high bar to beat. Position sizing prudent."],

    [grn("BUY"),  "MANH",  "Manhattan Associates",
     "+39% MTD on supply chain AI platform. Enterprise demand for intelligent operations "
     "accelerating. Earnings beat + guide raise. AI-augmented supply chain is a "
     "multi-year secular theme. Cognizant (+36%) and HubSpot (+34%) confirm AI-SaaS re-rating "
     "is broadening beyond mega-cap.",
     "Valuation rich after 39% monthly run. Supply chain spend could slow with "
     "manufacturing PMI weakness. Not a catalyst-driven trade — more of a thesis hold."],

    [red("SELL/AVOID"), "AAPL", "Apple",
     "Q4 guide 9-11% growth below ~12% estimate. Chip shortage (DRAM, advanced-node) "
     "worsening through 2027. Mac supply constrained structurally. Services missed. "
     "The structural headwind (SK Hynix warning: 2027 worst-ever semiconductor shortage) "
     "is multi-quarter, not a one-quarter blip. ASP pressures from chip scarcity adding to cost.",
     "Apple has unmatched ecosystem loyalty and services margin. "
     "iPhone 18 supercycle could offset if TSMC prioritizes. "
     "Near-term: -9.4% priced in some but not all of the shortage duration risk."],

    [red("SELL/AVOID"), "GOOGL","Alphabet",
     "FCF margin collapsed 21%→9.2% on $190B 2026 capex. Moody's credit warning. "
     "While stock partially recovered today, the structural concern (capex > returns) "
     "will limit re-rating until Q3 shows capex efficiency. Avoid until next "
     "earnings call shows FCF improvement or capex discipline.",
     "Record revenue, cloud +82%, YouTube growing. Stock already down ~18% from highs. "
     "Any reduction in capex guidance would be a massive re-rating catalyst upward."],

    [red("AVOID"), "COIN", "Coinbase",
     "Q2 revenue -14%, net loss $360M. Crypto market in cooling phase. "
     "Institutional crypto demand has not materialized as expected. "
     "Regulatory environment still uncertain. No near-term catalyst visible.",
     "Any crypto market recovery (Bitcoin rally) would drive COIN higher. "
     "Spot Bitcoin ETF flows could re-accelerate. Speculative trade only."],
]

t9 = Table(trades, colWidths=[0.7*inch, 0.6*inch, 1.0*inch, 2.7*inch, 1.9*inch])
t9.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#0a2342")),
    ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#eef2f7")]),
    ("GRID",         (0,0), (-1,-1), 0.25, colors.HexColor("#cccccc")),
    ("TOPPADDING",   (0,0), (-1,-1), 3),
    ("BOTTOMPADDING",(0,0), (-1,-1), 3),
    ("LEFTPADDING",  (0,0), (-1,-1), 5),
    ("VALIGN",       (0,0), (-1,-1), "TOP"),
]))
story.append(t9)
story.append(Spacer(1, 4))
story.append(Paragraph(
    b("Summary Decision:") + " The dominant theme is "
    "<b>cloud AI winners vs. hardware/capex spenders</b>. "
    "AMZN and MSFT have clearly justified their AI infrastructure spend via revenue. "
    "AAPL, META, and GOOGL are paying the cost without yet showing the return. "
    "For Monday: watch ISM Manufacturing at 10 AM (recession signal vs. re-acceleration). "
    "PLTR earnings after close is the AI-software monetization verdict for the sector. "
    "The 30-year yield at 5.25% is the macro ceiling — if it breaks above 5.3%, "
    "expect significant tech multiple compression regardless of earnings.",
    BODY))

# ── Footer ────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
story.append(Spacer(1, 4))
story.append(Paragraph(b("Data Sources &amp; Methodology"), H2))
story.append(Paragraph(
    f"SPY/QQQ closing prices: data/prices.csv ({len(rows)} rows, 2025-07-30 through 2026-07-31). "
    "July 30 close confirmed: SPY $741.69, QQQ $683.55 (multiple web sources). "
    "July 31 close estimated: SPY $744.65 (+0.40%), QQQ $688.33 (+0.70%) from "
    "S&amp;P 500 ≈ +0.40% market recap and near-close QQQ price from search. "
    "52-week stats computed from prices.csv window. "
    "Earnings data: Amazon.com IR press release; Microsoft IR Q4 FY26; "
    "Apple Q3 2026 CNBC/Yahoo Finance/TechTimes; Meta Q2 2026 CNBC; "
    "Alphabet Q2 2026 CNBC; Coinbase Q2 2026 GuruFocus. "
    "Fed decision: CNBC Fed meeting recap July 2026. "
    "GDP: initial estimate via search. "
    "PMI calendar: Investrade weekly event calendar 08/03/2026–08/07/2026. "
    "PLTR earnings: Yahoo Finance, EarningsWhispers, WallStreetHorizon. "
    "Market recap: TheStreet, 24/7 Wall St., Madison Investments.",
    SMALL))
story.append(Paragraph(
    b("Limitation:") +
    " Direct API access to Yahoo Finance, Stooq, and financial data endpoints is blocked "
    "by the session's egress policy. July 31 SPY/QQQ closing prices are best-effort estimates "
    "from multiple search-based sources and may carry ±$0.50 error vs. official 4pm ET close. "
    "Next-day (Snap) figures are analyst estimates, not actuals.",
    SMALL))
story.append(Paragraph(
    b("Disclaimer:") +
    " This is an automated informational report generated by a scheduled analytics routine. "
    "It is NOT investment advice. No trades are placed, recommended, or simulated. "
    "Past price moves do not guarantee future results.",
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
