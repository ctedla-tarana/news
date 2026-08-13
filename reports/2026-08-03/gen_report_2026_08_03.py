#!/usr/bin/env python3
"""Generate markets-2026-08-03.pdf using ReportLab."""

import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

# ─── Load price data ────────────────────────────────────────────────────────
prices_file = "/home/user/news/data/prices.csv"
rows = []
with open(prices_file, newline="") as f:
    rows = list(csv.DictReader(f))

spy_closes = [float(r["SPY_close"]) for r in rows]
qqq_closes = [float(r["QQQ_close"]) for r in rows]
dates = [r["date"] for r in rows]

spy_today  = spy_closes[-1];  qqq_today  = qqq_closes[-1]
spy_prev   = spy_closes[-2];  qqq_prev   = qqq_closes[-2]
spy_pct    = (spy_today / spy_prev - 1) * 100
qqq_pct    = (qqq_today / qqq_prev - 1) * 100
spy_1y_high = max(spy_closes); spy_1y_low = min(spy_closes)
qqq_1y_high = max(qqq_closes); qqq_1y_low = min(qqq_closes)
spy_1y_ret  = (spy_closes[-1] / spy_closes[0] - 1) * 100
qqq_1y_ret  = (qqq_closes[-1] / qqq_closes[0] - 1) * 100
spy_1y_high_dt = dates[spy_closes.index(spy_1y_high)]
spy_1y_low_dt  = dates[spy_closes.index(spy_1y_low)]
qqq_1y_high_dt = dates[qqq_closes.index(qqq_1y_high)]
qqq_1y_low_dt  = dates[qqq_closes.index(qqq_1y_low)]

# Weekly / Monthly
spy_wk_ret = (spy_closes[-1] / spy_closes[-6] - 1) * 100
qqq_wk_ret = (qqq_closes[-1] / qqq_closes[-6] - 1) * 100
spy_mo_ret = (spy_closes[-1] / spy_closes[-22] - 1) * 100
qqq_mo_ret = (qqq_closes[-1] / qqq_closes[-22] - 1) * 100

# ─── Build PDF ──────────────────────────────────────────────────────────────
out_path = "/home/user/news/reports/2026-08-03/markets-2026-08-03.pdf"
doc = SimpleDocTemplate(
    out_path,
    pagesize=letter,
    leftMargin=0.75*inch, rightMargin=0.75*inch,
    topMargin=0.75*inch, bottomMargin=0.75*inch,
)

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, spaceAfter=4,
                    textColor=colors.HexColor("#1a3a5c"))
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceAfter=3,
                    textColor=colors.HexColor("#2c5f8a"), spaceBefore=10)
H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, spaceAfter=2,
                    textColor=colors.HexColor("#444444"), spaceBefore=6)
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontSize=9.5,
                      spaceAfter=4, leading=14)
NOTE = ParagraphStyle("NOTE", parent=styles["Normal"], fontSize=8,
                      textColor=colors.grey, spaceAfter=3, leading=12)
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=16, bulletIndent=0,
                        spaceAfter=3)

def tbl(data, col_widths=None, header_bg=colors.HexColor("#1a3a5c")):
    t = Table(data, colWidths=col_widths)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fc")]),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    t.setStyle(TableStyle(style))
    return t

story = []

# Header
story.append(Paragraph("US Markets Daily Report — August 3, 2026", H1))
story.append(Paragraph(
    "Generated after market close (ET). Prices are estimated from confirmed "
    "daily index % moves; see footnote. Analysis covers SPY/QQQ dynamics, "
    "news-to-moves mapping, top movers, and next-day scenario trees.",
    NOTE))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2c5f8a"),
                         spaceAfter=8))

# ── 1. SNAPSHOT TABLE ──────────────────────────────────────────────────────
story.append(Paragraph("1 · SPY & QQQ Snapshot", H2))

snap_data = [
    ["Metric", "SPY (S&P 500 ETF)", "QQQ (Nasdaq-100 ETF)"],
    ["Today's Close*",  f"${spy_today:.2f}", f"${qqq_today:.2f}"],
    ["Today's Chg",
     f"{spy_pct:+.2f}%",
     f"{qqq_pct:+.2f}%"],
    ["Prev Close (7/31)", f"${spy_prev:.2f}", f"${qqq_prev:.2f}"],
    ["1-Yr High",
     f"${spy_1y_high:.2f}  ({spy_1y_high_dt})",
     f"${qqq_1y_high:.2f}  ({qqq_1y_high_dt})"],
    ["1-Yr Low",
     f"${spy_1y_low:.2f}  ({spy_1y_low_dt})",
     f"${qqq_1y_low:.2f}  ({qqq_1y_low_dt})"],
    ["1-Yr Return", f"{spy_1y_ret:+.1f}%", f"{qqq_1y_ret:+.1f}%"],
    ["1-Wk Return",  f"{spy_wk_ret:+.2f}%", f"{qqq_wk_ret:+.2f}%"],
    ["1-Mo Return",  f"{spy_mo_ret:+.2f}%", f"{qqq_mo_ret:+.2f}%"],
    ["WTI Crude Oil", "$79.62 (-5.97%)", "— Iran deal tailwind"],
    ["Brent Crude",   "$82.92 (-5.69%)", "— geopolitical risk premium unwind"],
    ["Dow Jones",     "53,131 (+1.23%)", "Record close"],
]
story.append(tbl(snap_data, col_widths=[1.8*inch, 2.5*inch, 2.5*inch]))
story.append(Paragraph(
    "* SPY/QQQ closes are estimated: SPY = prior close × 1.015 (S&P +1.50%); "
    "QQQ = prior close × 1.011 (Nasdaq-100 +~1.1%, as chip weakness offset "
    "mega-cap tech surge). Dow, oil figures from confirmed sources.",
    NOTE))

# ── 2. TODAY'S NEWS → MOVES ─────────────────────────────────────────────────
story.append(Paragraph("2 · Today's News → Market Moves", H2))

story.append(Paragraph(
    "<b>S&P 500 +1.50%  |  Nasdaq-100 +~1.1%  |  Dow +1.23% (record close)</b>",
    BODY))
story.append(Spacer(1, 4))

news_items = [
    (
        "Iran Diplomacy / Oil Collapse  (Primary driver; +0.8–1.0 ppt to S&P)",
        "President Trump called off a planned military strike on Iran, "
        "re-opening Strait of Hormuz negotiations. WTI fell 5.97% to $79.62; "
        "Brent fell 5.69% to $82.92. Lower energy costs reduce input inflation "
        "across the economy, push rate-cut expectations slightly higher, and "
        "relieve geopolitical risk premium. Energy sector sold off (short-term "
        "revenue hit) but broad market surged as consumer/industrial margins "
        "improved. The oil drop alone likely contributed 80–100 bps to SPY."
    ),
    (
        "Amazon AWS Earnings Blowout — $3 Trillion Milestone  (+0.4–0.5 ppt)",
        "Amazon reported Q2 revenues of $200.61B (est. $196.47B) and AWS "
        "revenue of $42.2B (est. $40.54B, +~30% YoY). AMZN stock surged "
        "+5.2% to $285.79, briefly crossing a $3 trillion market cap for the "
        "first time. AWS strength validated AI-cloud capex cycle and boosted "
        "the entire hyperscaler complex. Amazon is ~7% of QQQ."
    ),
    (
        "Meta Platforms Ad Revenue Surge  (+0.3–0.4 ppt to QQQ)",
        "Meta recovered from its May selloff, rising +7% to $593.15 after "
        "Q2 advertising revenue climbed 27% to $59B. Strong ad spend signals "
        "healthy consumer and brand budgets. Meta is ~5% of QQQ; its 7% gain "
        "contributed roughly 35 bps directly to QQQ returns."
    ),
    (
        "Microsoft & Alphabet AI Spending Confidence  (+0.2–0.3 ppt)",
        "MSFT +5% to $488.16 and GOOGL +5% to $374.40 continued momentum "
        "from prior week's earnings. Alphabet raised FY2026 capex guidance to "
        "$195–205B; Google Cloud grew 82% in Q2 to $24.8B. Hyperscaler capex "
        "acceleration signals AI buildout remains intact, lifting cloud "
        "software and data center supply chains."
    ),
    (
        "ISM Manufacturing PMI 55.6 — 4-Year High  (+0.1 ppt)",
        "July ISM Manufacturing PMI printed 55.6 (vs 53.3 prior), the "
        "highest since May 2022, with New Orders at 56.7 and Production "
        "at 58.5. This 21st consecutive month of expansion confirms the "
        "US industrial re-shoring trend is intact. Cyclical sectors "
        "(industrials, materials) added modestly to SPY gains."
    ),
    (
        "Philadelphia Semiconductor Index (SOX) -1.9%  (Drag on QQQ)",
        "Micron (MU) and Broadcom (AVGO) led chip stocks lower amid "
        "continued DRAM/NAND pricing pressure and margin concerns on "
        "AI-GPU ramps. The SOX decline offset mega-cap strength in QQQ, "
        "explaining why QQQ (+~1.1%) lagged the Nasdaq Composite (+2.1%). "
        "Semiconductor stocks remain a -0.4 ppt headwind on QQQ today."
    ),
]

for title, detail in news_items:
    story.append(Paragraph(f"<b>{title}</b>", BULLET))
    story.append(Paragraph(detail, BULLET))
    story.append(Spacer(1, 2))

# ── 3. TOP MOVERS ───────────────────────────────────────────────────────────
story.append(Paragraph("3 · Top 10 Daily / Weekly / Monthly Movers", H2))

story.append(Paragraph("3a · Daily Top 10 Gainers (August 3, 2026)", H3))
daily_gain = [
    ["Ticker","Company","~Daily Chg","Sector","Driver"],
    ["META","Meta Platforms","+7.0%","Comm. Services","Ad revenue +27% Q2"],
    ["AMZN","Amazon.com","+5.2%","Cons. Discretionary","AWS blowout, $3T cap"],
    ["MSFT","Microsoft","+5.0%","Technology","Azure AI capex signal"],
    ["GOOGL","Alphabet","+5.0%","Comm. Services","GCloud +82%, capex raise"],
    ["DXCM","DexCom","+10.9%","Health Care","Q2 beat + FDA AI approval"],
    ["MPWR","Monolithic Power","+~8%","Technology","Power mgmt earnings beat"],
    ["ORCL","Oracle","+~4%","Technology","RPO $638B, Cloud Infra +93%"],
    ["HYFM","Hydrofarm Hldgs","+241%","Consumer Staples","Asset sale windfall"],
    ["EZRA","EZRA Medical","+75%","Health Care","$11M asset sale deal"],
    ["Airlines / Travel","Multiple carriers","+3-4%","Industrials","Oil -6%, fuel cost relief"],
]
story.append(tbl(daily_gain, col_widths=[0.8*inch, 1.6*inch, 0.8*inch, 1.4*inch, 2.2*inch]))

story.append(Spacer(1, 6))
story.append(Paragraph("Daily Top 10 Losers (August 3, 2026)", H3))
daily_loss = [
    ["Ticker","Company","~Daily Chg","Sector","Driver"],
    ["MU","Micron Technology","-2.5%","Tech / Semis","DRAM/NAND pricing pressure"],
    ["AVGO","Broadcom","-2.0%","Tech / Semis","SOX selloff, margin concerns"],
    ["NVDA","NVIDIA","-1.8%","Tech / Semis","Chip sector rotation"],
    ["AMD","Advanced Micro Dev.","-1.5%","Tech / Semis","Pre-earnings caution"],
    ["XOM","ExxonMobil","-3.8%","Energy","Oil -6% on Iran deal"],
    ["CVX","Chevron","-3.5%","Energy","Oil -6% revenue impact"],
    ["COP","ConocoPhillips","-3.2%","Energy","Oil price collapse"],
    ["COIN","Coinbase","-3.1%","Financials","Risk rotation, crypto down"],
    ["CTVA","Corteva","-2.8%","Materials","Agri chemical sector drag"],
    ["GDDY","GoDaddy","-2.1%","Tech / Services","Sector rotation out of mid-cap"],
]
story.append(tbl(daily_loss, col_widths=[0.8*inch, 1.6*inch, 0.8*inch, 1.4*inch, 2.2*inch]))

story.append(Spacer(1, 6))
story.append(Paragraph("3b · Weekly Top 10 Gainers (July 28 – August 3, 2026)", H3))
weekly_gain = [
    ["Ticker","Company","~Weekly Chg","Sector","Driver"],
    ["META","Meta Platforms","+~12%","Comm. Services","Earnings recovery from May miss"],
    ["AMZN","Amazon.com","+~9%","Cons. Discretionary","AWS Q2 blowout"],
    ["MSFT","Microsoft","+~7%","Technology","Azure AI capex beat"],
    ["GOOGL","Alphabet","+~7%","Comm. Services","GCloud hyper-growth"],
    ["DXCM","DexCom","+~12%","Health Care","Q2 beat + FDA win"],
    ["MPWR","Monolithic Power","+~10%","Technology","Power semis earnings"],
    ["AAPL","Apple","+~4%","Technology","Earnings outlook stable"],
    ["Airlines / Travel","AAL/DAL/UAL","+5-8%","Industrials","Oil price relief"],
    ["GOOG","Alphabet C","+~7%","Comm. Services","Google Cloud strength"],
    ["CRM","Salesforce","+~5%","Technology","SaaS enterprise demand"],
]
story.append(tbl(weekly_gain, col_widths=[0.8*inch, 1.6*inch, 0.85*inch, 1.4*inch, 2.15*inch]))

story.append(Spacer(1, 4))
story.append(Paragraph("Weekly Top 10 Losers (July 28 – August 3, 2026)", H3))
weekly_loss = [
    ["Ticker","Company","~Weekly Chg","Sector","Driver"],
    ["XOM","ExxonMobil","-5%","Energy","Oil -6% on Iran talks"],
    ["CVX","Chevron","-5%","Energy","Oil -6% revenue impact"],
    ["MU","Micron","-4%","Tech / Semis","Memory pricing pressure"],
    ["AVGO","Broadcom","-4%","Tech / Semis","Chip sector rotation"],
    ["NVDA","NVIDIA","-3%","Tech / Semis","Post-run consolidation"],
    ["COIN","Coinbase","-5%","Financials","Crypto soft week"],
    ["COP","ConocoPhillips","-4.5%","Energy","Iran/oil impact"],
    ["SLB","Schlumberger","-4%","Energy","Oil services follow"],
    ["OXY","Occidental Petro","-5%","Energy","Oil price sensitive"],
    ["HAL","Halliburton","-4.5%","Energy","Oil services follow"],
]
story.append(tbl(weekly_loss, col_widths=[0.8*inch, 1.6*inch, 0.85*inch, 1.4*inch, 2.15*inch]))

story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Weekly Sector Trend:</b> Big Tech / AI Hyperscalers surged on "
    "earnings beats while Energy fell across the board as oil collapsed "
    "on Iran diplomacy. Semiconductor names (Micron, Broadcom, NVIDIA) "
    "were notable laggards within Tech.",
    BODY))

story.append(Spacer(1, 6))
story.append(Paragraph("3c · Monthly Top 10 Gainers (July 2026)", H3))
monthly_gain = [
    ["Ticker","Company","~Monthly Chg","Sector","Driver"],
    ["AAPL","Apple","+15.2%","Technology","Supply chain re-rating, India mfg"],
    ["META","Meta Platforms","+~14%","Comm. Services","Ad revenue beat recovers May losses"],
    ["AMZN","Amazon.com","+~18%","Cons. Discretionary","AWS AI cloud acceleration"],
    ["MSFT","Microsoft","+~12%","Technology","Azure growth momentum"],
    ["GOOGL","Alphabet","+~11%","Comm. Services","Google Cloud re-rating"],
    ["ORCL","Oracle","+~10%","Technology","Cloud infra RPO surge"],
    ["LLY","Eli Lilly","+~8%","Health Care","GLP-1 demand expansion"],
    ["UNH","UnitedHealth","+~7%","Health Care","Medicare Advantage recovery"],
    ["CAT","Caterpillar","+~7%","Industrials","ISM manufacturing boost"],
    ["DE","Deere & Co","+~6%","Industrials","Equipment demand, re-shoring"],
]
story.append(tbl(monthly_gain, col_widths=[0.8*inch, 1.6*inch, 0.85*inch, 1.4*inch, 2.15*inch]))

story.append(Spacer(1, 4))
story.append(Paragraph("Monthly Top 10 Losers (July 2026)", H3))
monthly_loss = [
    ["Ticker","Company","~Monthly Chg","Sector","Driver"],
    ["XOM","ExxonMobil","-8%","Energy","Oil -$25+/bbl since June ATH"],
    ["CVX","Chevron","-7%","Energy","Oil income risk"],
    ["MU","Micron","-12%","Tech / Semis","Commodity DRAM pricing crash"],
    ["AVGO","Broadcom","-8%","Tech / Semis","AI-spending concern overhang"],
    ["NVDA","NVIDIA","-6%","Tech / Semis","Post-ATH consolidation, Iran risk"],
    ["COP","ConocoPhillips","-9%","Energy","Direct oil price exposure"],
    ["SLB","Schlumberger","-7%","Energy","Oil services demand concern"],
    ["COIN","Coinbase","-10%","Financials","Crypto winter fears; rate uncertainty"],
    ["INTC","Intel","-15%","Technology","Market share losses to AMD/ARM"],
    ["OXY","Occidental Petro","-9%","Energy","High oil price beta, reversed"],
]
story.append(tbl(monthly_loss, col_widths=[0.8*inch, 1.6*inch, 0.85*inch, 1.4*inch, 2.15*inch]))

story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Monthly Sector Trends:</b><br/>"
    "<b>Gaining sectors:</b> Big Tech & AI Hyperscalers (MSFT, AMZN, META, GOOGL), "
    "Healthcare/GLP-1 (LLY), Industrials (CAT, DE) driven by ISM expansion and "
    "re-shoring narrative.<br/>"
    "<b>Losing sectors:</b> Energy across the board as oil prices retreated from June "
    "ATH highs on Iran diplomacy; Semiconductors (MU, AVGO, INTC) under pressure "
    "from memory oversupply and market-share shifts; Crypto-adjacent (COIN).",
    BODY))

# ── 4. NEXT-DAY SCENARIOS ───────────────────────────────────────────────────
story.append(Paragraph("4 · Next-Day Scenarios — Tuesday, August 4, 2026", H2))
story.append(Paragraph(
    "<b>Calendar:</b> AMD Q2 earnings (after close), Palantir Q2 earnings (before/at open), "
    "Disney / Shopify / McDonald's / Pfizer earnings during the day. "
    "<b>ISM Services PMI</b> is Wednesday Aug 5; "
    "<b>Nonfarm Payrolls</b> is Friday Aug 7. Iran talks continue off-market.",
    BODY))
story.append(Spacer(1, 4))

scenarios = [
    (
        "Catalyst 1 · AMD Q2 Earnings (After Close Tonight — Market Impact Tomorrow)",
        [
            ("BEAT: Revenue >$11.2B + strong Instinct/Helios guidance",
             "AMD +8–12% pre-market; SOX rebounds 1–2%; NVDA/AVGO sympathy up 2–3%; "
             "QQQ +0.6–0.8%; SPY +0.3–0.4%. Mechanism: validates AI GPU demand "
             "is not just NVIDIA and signals broad semis recovery. Watch Helios "
             "ramp guidance — margin pressure near-term but topline growth validates "
             "AI-infra cycle."),
            ("MISS: Revenue <$11.0B or weak guidance on Helios margins",
             "AMD -8–15%; SOX -2–3%; ripple to NVDA/AVGO -2%; QQQ -0.5–0.8%; "
             "SPY -0.3%. Mechanism: semiconductor cycle concern deepens, "
             "AI capex narrative questioned. Would offset today's tech gains."),
        ]
    ),
    (
        "Catalyst 2 · Palantir Q2 Earnings (Expected Tues Pre-Market)",
        [
            ("BEAT: Rev >$1.81B + raised guidance, EPS >$0.35",
             "PLTR +5–8%; AI defense software peers up 2–3%; "
             "SPY negligible (PLTR is ~0.25% of S&P). However, Palantir's "
             "US Government AI contracts are a read-through for federal AI "
             "spending — bullish signal for broader enterprise AI."),
            ("MISS or valuation concern (~P/S 61x already stretched)",
             "PLTR -10–15% (Motley Fool bearish preview materialized); "
             "AI software de-rating risk across sector; negligible direct "
             "SPY/QQQ impact but sentiment drag on high-multiple growth names."),
        ]
    ),
    (
        "Catalyst 3 · Iran / Strait of Hormuz Overnight Developments",
        [
            ("Talks progress; ceasefire framework announced",
             "WTI falls below $75; S&P futures +0.5–0.8% before open; "
             "Airlines/Transportation, consumer discretionary surge. Inflation "
             "expectations fall → 10-yr yields dip → rate-sensitive sectors "
             "(REIT, utilities) catch a bid. SPY +0.4–0.6% on open."),
            ("Talks break down; Iran threatens Hormuz closure",
             "WTI spikes toward $90; Energy +3%; Broad market -1.0–1.5% open; "
             "QQQ -1.2% (tech most rate-sensitive to higher-for-longer on oil "
             "inflation). Airlines -4%; Consumer staples defensive bid."),
        ]
    ),
    (
        "Catalyst 4 · ISM Services PMI (Wednesday Preview — Sets Tuesday Tone)",
        [
            ("ISM Services >54 (expansion, matches manufacturing strength)",
             "Soft-landing narrative reinforced; SPY continues rally +0.3%; "
             "Bonds sell off modestly; USD strengthens. Financials/cyclicals "
             "outperform."),
            ("ISM Services <51 (near stall or contraction)",
             "Recession concern re-emerges; defensive rotation into "
             "utilities/healthcare; SPY -0.5–1.0%; yield curve steepens; "
             "small-caps (IWM) hit hardest."),
        ]
    ),
]

for cat_title, branches in scenarios:
    story.append(Paragraph(f"<b>{cat_title}</b>", H3))
    for condition, outcome in branches:
        story.append(Paragraph(f"  ▸ <b>IF</b> {condition}:", BULLET))
        story.append(Paragraph(f"    <b>THEN</b> {outcome}", BULLET))
        story.append(Spacer(1, 2))

# ── 5. POSSIBLE PURCHASE SUMMARY ─────────────────────────────────────────────
story.append(Paragraph("5 · Possible Trade Summary (End-of-Day / Next-Day Open)", H2))
story.append(Paragraph(
    "This section is for informational and analytical purposes only. "
    "No trades are placed or simulated. All views are based on publicly "
    "available data, news, and fundamental factors.",
    NOTE))
story.append(Spacer(1, 4))

trade_data = [
    ["Action","Ticker","Rationale","Risk / Watch"],
    ["BUY (conviction: HIGH)","AMZN",
     "AWS AI-cloud growth $42.2B beat. $3T milestone signals institutional "
     "re-rating. AWS sold out through 2027; GenAI inference demand structural.",
     "Valuation stretch; needs continued cloud margin expansion"],
    ["BUY (conviction: HIGH)","META",
     "+7% day; ad revenue +27%. AI-driven Advantage+ ad targeting = "
     "durable moat. Still below June ATH; recovery not complete.",
     "Regulatory risk (EU); mid-cycle ad spend sensitivity"],
    ["BUY (conviction: MEDIUM-HIGH)","MSFT",
     "Azure growth + Copilot enterprise adoption. +5% today continues "
     "multi-week trend. AI capex $195B+ guidance (GOOGL) validates hyperscaler cycle.",
     "US DOJ AI antitrust scrutiny; Azure growth deceleration risk"],
    ["BUY (conviction: MEDIUM)","DXJ/Airlines ETF",
     "Oil -6% = direct margin windfall for airlines/transport. If Iran "
     "talks hold, fuel cost tailwind persists. Delta/UAL/AAL undervalued.",
     "Iran talks collapse = immediate reversal; demand sensitivity"],
    ["BUY (conditional — wait for AMD print)","AMD",
     "If AMD beats tonight: semis recovery, strong AI GPU demand "
     "thesis. AMD at significant discount to NVDA on AI GPU market share.",
     "Beat required; Helios margin risk; INTC competitive pressure"],
    ["BUY (conviction: MEDIUM)","DXCM",
     "Q2 beat +13% YoY, FDA AI-enabled CGM approval, raised guidance. "
     "GLP-1 population driving CGM market expansion.",
     "Competition from Abbott (FreeStyle Libre); insurance coverage"],
    ["AVOID / UNDERWEIGHT","MU/AVGO",
     "DRAM/NAND commodity pricing pressure. Memory oversupply cycle "
     "not yet cleared despite HBM strength. SOX -1.9% today. "
     "Broadcom AI-chip concerns persist.",
     "Wait for commodity memory pricing inflection signal"],
    ["AVOID","Energy (XOM/CVX/COP)",
     "Oil -6% today; Iran deal if sustained = structural oil headwind. "
     "Energy was the month's worst sector. Avoid until Iran resolution clear.",
     "If Iran talks fail = violent reversal; use as hedge only"],
    ["BUY (long-term conviction)","QQQ / Mega-cap index",
     "AI capex supercycle intact (Amazon, Microsoft, Alphabet all raising). "
     "ISM Manufacturing at 4-yr high. Iran diplomacy reduces tail risk. "
     "QQQ -2.96% this month = buy-the-dip opportunity vs. S&P.",
     "Chip sector drag; potential Iran reversal; NFP surprise Friday"],
]
story.append(tbl(trade_data,
                  col_widths=[1.3*inch, 0.9*inch, 3.0*inch, 1.65*inch]))

story.append(Spacer(1, 8))
story.append(Paragraph(
    "<b>Key macro backdrop for tomorrow:</b> NFP jobs report Friday (expected "
    "~175K jobs). If jobs come in hot (+200K+), Fed expectations shift hawkish → "
    "SPY/QQQ give back 0.5–1.0%. If jobs miss (<150K), recession fear vs. "
    "rate-cut hope dynamic. AMD earnings are the single biggest near-term "
    "catalyst for QQQ direction Tuesday. Iran remains a binary overnight tail risk.",
    BODY))

story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Sources: Bloomberg, The Street, Yahoo Finance, 24/7 Wall St., CNBC, "
    "Benzinga, ISM World, Investing.com, Fortune, TipRanks, Schaeffersresearch.com | "
    "Data as of August 3, 2026 market close ET. SPY/QQQ estimated from confirmed "
    "index % moves; exact ETF closing prices may differ slightly.",
    NOTE))

doc.build(story)
print(f"PDF generated: {out_path}")
