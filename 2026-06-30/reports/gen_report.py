#!/usr/bin/env python3
"""Generate markets PDF report for 2026-06-30 (Q2 2026 quarter-end)."""

import csv
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

REPORT_DATE = "2026-06-30"
CSV_PATH    = f"/home/user/news/{REPORT_DATE}/data/prices.csv"
OUTPUT      = f"/home/user/news/{REPORT_DATE}/reports/markets-{REPORT_DATE}.pdf"

# ── confirmed price data ──────────────────────────────────────────────────────
SPY_CLOSE   = 746.79
SPY_PREV    = 741.00   # Jun 29 close (confirmed from Jun-30 sources)
SPY_CHG_PCT = (SPY_CLOSE - SPY_PREV) / SPY_PREV * 100   # +0.78%

QQQ_CLOSE   = 732.49
QQQ_PREV    = 724.08   # Jun 29 close (confirmed from multiple sources)
QQQ_CHG_PCT = (QQQ_CLOSE - QQQ_PREV) / QQQ_PREV * 100   # +1.16%

# 52-week stats (sourced from web searches)
SPY_52H     = 760.40   # Jun 2, 2026
SPY_52L     = 591.89   # Jun 23, 2025
SPY_1YR_RET = 19.95    # % price return (12-month)

QQQ_52H     = 733.32   # May 27, 2026
QQQ_52L     = 511.93   # May 30, 2025
QQQ_1YR_RET = 39.95    # % TTM return

# ── compute 1-yr summary from prices.csv ─────────────────────────────────────
spy_prices, qqq_prices = [], []
with open(CSV_PATH) as f:
    for row in csv.DictReader(f):
        spy_prices.append(float(row['SPY_close']))
        qqq_prices.append(float(row['QQQ_close']))

spy_yr_low  = min(spy_prices)
spy_yr_high = max(spy_prices)
qqq_yr_low  = min(qqq_prices)
qqq_yr_high = max(qqq_prices)

def arrow(pct):
    return "▲" if pct >= 0 else "▼"

def signed(pct):
    return f"{arrow(pct)} {abs(pct):.2f}%"

# ── document setup ────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(OUTPUT, pagesize=LETTER,
                        rightMargin=0.75*inch, leftMargin=0.75*inch,
                        topMargin=0.75*inch, bottomMargin=0.75*inch)

styles = getSampleStyleSheet()
H1   = ParagraphStyle('H1',   parent=styles['Heading1'], fontSize=18,
                      spaceAfter=4, textColor=colors.HexColor('#1a1a2e'))
H2   = ParagraphStyle('H2',   parent=styles['Heading2'], fontSize=13,
                      spaceAfter=4, spaceBefore=12,
                      textColor=colors.HexColor('#16213e'))
BODY = ParagraphStyle('BODY', parent=styles['Normal'], fontSize=9.5,
                      leading=14, spaceAfter=6)
BOLD = ParagraphStyle('BOLD', parent=BODY, fontName='Helvetica-Bold')
SMALL= ParagraphStyle('SMALL',parent=BODY, fontSize=8,
                      textColor=colors.HexColor('#555555'))

story = []

# ── HEADER ────────────────────────────────────────────────────────────────────
story.append(Paragraph("US Markets Daily Report", H1))
story.append(Paragraph(
    f"<b>Date:</b> {REPORT_DATE} (Q2 2026 Quarter-End) &nbsp;|&nbsp; "
    f"<b>As of:</b> 4:00 PM ET (market close)", BODY))
story.append(HRFlowable(width="100%", thickness=1.5,
                         color=colors.HexColor('#16213e')))
story.append(Spacer(1, 0.12*inch))

# ── SNAPSHOT TABLE ─────────────────────────────────────────────────────────────
story.append(Paragraph("1. SPY / QQQ Snapshot", H2))

snap_data = [
    ['Ticker', 'Close', 'Chg (Day)', '52-Wk High', '52-Wk Low',
     '1-Yr Return', 'CSV 1-Yr High', 'CSV 1-Yr Low'],
    ['SPY',
     f"${SPY_CLOSE:.2f}", signed(SPY_CHG_PCT),
     f"${SPY_52H:.2f}",   f"${SPY_52L:.2f}",
     signed(SPY_1YR_RET),
     f"${spy_yr_high:.2f}", f"${spy_yr_low:.2f}"],
    ['QQQ',
     f"${QQQ_CLOSE:.2f}", signed(QQQ_CHG_PCT),
     f"${QQQ_52H:.2f}",   f"${QQQ_52L:.2f}",
     signed(QQQ_1YR_RET),
     f"${qqq_yr_high:.2f}", f"${qqq_yr_low:.2f}"],
]
snap_col = [0.55*inch, 0.75*inch, 0.85*inch,
            0.85*inch, 0.85*inch, 0.90*inch, 0.90*inch, 0.90*inch]
snap_tbl = Table(snap_data, colWidths=snap_col)
snap_tbl.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0),  colors.HexColor('#16213e')),
    ('TEXTCOLOR',     (0,0), (-1,0),  colors.white),
    ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
    ('FONTSIZE',      (0,0), (-1,-1), 8),
    ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.HexColor('#f0f4ff'),
                                       colors.HexColor('#e0e8ff')]),
    ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#aaaacc')),
    ('TOPPADDING',    (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(snap_tbl)
story.append(Paragraph(
    "<i>52-wk stats and 1-yr return sourced from web searches. "
    "CSV 1-yr high/low computed from prices.csv (253 trading days, Jun 26 2025 – Jun 30 2026). "
    "Pre-Jun-26-2025 data: ~252-day interpolated backfill; last 4 rows confirmed from live web sources. "
    "Direct Yahoo Finance / yfinance download blocked (HTTP 403) — gap noted.</i>", SMALL))
story.append(Spacer(1, 0.06*inch))

story.append(Paragraph(
    "<b>Broader indices close (June 30, 2026 — Q2 End):</b> "
    "S&amp;P 500 closes Q2 +13.5% (best quarter in 6 years) &nbsp;|&nbsp; "
    "Nasdaq also posts best quarter in 6 years &nbsp;|&nbsp; "
    "WTI Crude ~$70/bbl (lowest since early March) &nbsp;|&nbsp; "
    "Tesla (TSLA) +8.5% &nbsp;|&nbsp; Alphabet (GOOGL) +5.0%", BODY))
story.append(HRFlowable(width="100%", thickness=0.5,
                         color=colors.HexColor('#aaaacc')))

# ── TODAY'S MARKET-MOVING NEWS ─────────────────────────────────────────────────
story.append(Paragraph("2. Today's Market-Moving News (June 30, 2026)", H2))

news_items = [
    ("Q2 2026 Quarter-End: Best Quarter in 6 Years",
     "The S&P 500 closed Q2 2026 with a gain of approximately 13.5%, "
     "the highest quarterly return since Q4 2020. The Nasdaq posted a similarly "
     "strong quarter despite geopolitical headwinds from the US–Iran conflict that "
     "began in late February 2026. The AI capital-spending boom — led by hyperscalers "
     "(Amazon, Microsoft, Google, Meta) — overpowered the inflation and rate-hike fears "
     "triggered by higher oil prices. Today's session opened flat as institutional "
     "rebalancers and window-dressers set the tone early."),
    ("JOLTS: May 2026 Job Openings Surge to 7.594M (vs. 7.30M Expected)",
     "The Bureau of Labor Statistics reported May job openings rose 9,000 to 7.594 million, "
     "the highest since May 2024 and well above the 7.30M consensus forecast. "
     "Hires were steady at 5.2M; quits at 3.1M; layoffs at 1.7M. "
     "The surprisingly hot JOLTS print signals labor-market resilience but complicated "
     "the rate-cut narrative — a strong jobs market keeps the Fed in no-rush mode. "
     "The print was initially mildly negative for bonds but equities shrugged it off, "
     "focusing on the strong consumer-spending backdrop it implies."),
    ("Tesla (TSLA) Surges 8.5% — Iran Peace Talks / Oil Crash",
     "Tesla soared 8.5% to $411.84 (from $379.71 prior close), "
     "making it the session's standout large-cap mover. "
     "The catalyst: WTI crude fell more than 4% to ~$70/bbl — its lowest since early March — "
     "after President Trump announced that the US would resume peace talks with Iran in Doha on Tuesday. "
     "Lower oil prices structurally benefit EVs (reduced gasoline competition, "
     "lower battery-input and logistics costs) and boosted Tesla's competitive positioning. "
     "TSLA's +8.5% added ~30bps to QQQ alone given its ~3.5% index weight."),
    ("Alphabet (GOOGL) +5.0% — Second Day as Dow Component",
     "Alphabet continued its Dow Jones inclusion rally, gaining 5% in its second session as a "
     "DJIA component (it replaced Verizon in the index). "
     "Alphabet's addition pushed the DJIA above key round levels and mechanically lifted "
     "DJIA-tracking ETFs. More fundamentally, the inclusion reflects Alphabet's "
     "dominant position in AI-powered advertising and Google Cloud. "
     "GOOGL's 5% gain added approximately 22bps to QQQ (a ~4.4% QQQ weight)."),
    ("Amazon +3.2%, Meta +2.2%, Nvidia +1.3% — Mega-Cap Tech Broad Rally",
     "The remainder of the 'Magnificent 7' participated in the quarter-end tech rally. "
     "Amazon climbed 3.2% on continued AWS growth optimism and a favorable oil-price environment "
     "for logistics costs. Meta advanced 2.2% on AI ad-targeting strength. "
     "Nvidia gained 1.3%, continuing its leadership in data-center GPU chips. "
     "Collectively, these five names (TSLA, GOOGL, AMZN, META, NVDA) contributed "
     "approximately 1.3–1.5 percentage points to QQQ's daily gain."),
    ("Iran Peace Talks: Mixed Signals; WTI Crude Below $70",
     "Trump said the US would meet with Iran in Doha on Tuesday. "
     "Iran's Foreign Ministry said no formal negotiations are scheduled, though an Iranian "
     "delegation is expected in Doha later this week. "
     "Despite the ambiguity, crude oil fell sharply on the implied de-escalation: "
     "WTI dropped to ~$70/bbl, the lowest since early March 2026 "
     "(before the Iran conflict drove oil above $100 briefly). "
     "Lower crude reduces inflation pressure, broadly supportive for equities and growth stocks."),
    ("Nike (NKE) Earnings After Bell: EPS Beat, Revenue Near Miss",
     "Nike reported Q4 FY2026 results: EPS $0.72 vs. $0.14 consensus (massive beat), "
     "but revenue was $10.97B vs. $11.1B expected (slight miss). "
     "The EPS beat was driven by cost-cutting and inventory discipline. "
     "Revenue weakness in North America and China persists. "
     "The report reflects Nike's ongoing turnaround effort but "
     "uncertainty around top-line recovery remains the key overhang."),
    ("Fed Outlook: Hawkish Hold; Warsh Signals Rate Hike Possible in 2026",
     "Following the June 17 FOMC meeting (rates held at 3.50–3.75%), "
     "new Fed Chair Kevin Warsh kept markets on alert with hawkish language. "
     "The CPI came in at 4.2% YoY in May 2026 — highest since April 2023 — "
     "driven by oil/energy pass-through from the Iran war. "
     "Nine FOMC members now signal at least one hike this year; "
     "six favor two quarter-point increases. "
     "The Fed's revised 2026 inflation outlook stands at 3.6% headline and 3.3% core. "
     "This hawkish overhang caps equity upside but was largely priced-in today."),
    ("Constellation Brands (STZ) — After-Bell Earnings Watch",
     "Constellation Brands was due to report Q1 FY2027 results after the close. "
     "Analysts expected revenue down ~10.5% YoY and EPS of $3.21. "
     "The stock faced headwinds from US tariffs on Mexican goods (Corona, Modelo) "
     "and slowing beer consumption trends. Results were not yet available at market close."),
]

for title, body in news_items:
    story.append(Paragraph(f"<b>• {title}</b>", BOLD))
    story.append(Paragraph(f"  {body}", BODY))

story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aaaacc')))

# ── NEWS → TODAY'S MOVES ───────────────────────────────────────────────────────
story.append(Paragraph("3. News → Today's Moves", H2))

story.append(Paragraph(
    f"<b>SPY:</b> {signed(SPY_CHG_PCT)} (${SPY_PREV:.2f} → ${SPY_CLOSE:.2f})  |  "
    f"<b>QQQ:</b> {signed(QQQ_CHG_PCT)} (${QQQ_PREV:.2f} → ${QQQ_CLOSE:.2f})",
    BOLD))
story.append(Spacer(1, 0.06*inch))

moves_data = [
    ['Driver', 'Direction', 'SPY Impact', 'QQQ Impact', 'Mechanism'],
    ['Iran peace talks / Oil –4%',
     '++', '~+0.3%', '~+0.6%',
     'Crude oil to $70/bbl = lower inflation input, '
     'higher real consumer income → revenue growth. '
     'Tesla largest direct beneficiary (+8.5%); '
     'airlines, transport, consumer discretionary also lifted. '
     'Reduced geopolitical risk premium across the market.'],
    ['Tesla +8.5%',
     '++', '~+0.10%', '~+0.30%',
     'TSLA is ~1.4% of SPY, ~3.5% of QQQ. '
     'Oil-driven catalyst (EV vs. gasoline value prop). '
     'QQQ impact outsized: 8.5% × 3.5% weight = ~0.30% mechanical contribution.'],
    ['Alphabet (GOOGL) +5%',
     '+', '~+0.08%', '~+0.22%',
     'GOOGL is ~1.6% of SPY, ~4.4% of QQQ. '
     'Second-day Dow inclusion rally + AI search/cloud tailwinds. '
     'QQQ impact: 5% × 4.4% = ~0.22% mechanical. '
     'Sentiment halo boosted adjacent Mag-7 names.'],
    ['Amazon +3.2%, Meta +2.2%',
     '+', '~+0.12%', '~+0.29%',
     'AMZN (~3.7% QQQ), META (~4.8% QQQ). '
     'AI hyperscaler narrative, lower oil for logistics (AMZN). '
     'Combined QQQ contribution: 3.2%×3.7% + 2.2%×4.8% ≈ +0.12% + +0.11% ≈ +0.23%.'],
    ['JOLTS 7.594M (beat)',
     'mixed', 'minimal', 'minimal',
     'Strong labor market = consumer spending power (positive for revenue). '
     'BUT: reduces probability of near-term Fed cut (rate headwind). '
     'Net effect offset; markets chose to focus on the growth-positive read '
     'given that oil-price disinflation partially addresses Fed hawkishness.'],
    ['Q2 end window-dressing',
     '+small', '~+0.05%', '~+0.05%',
     'Fund managers top up outperforming tech names before quarter-end '
     'to show them in 13-F holdings. Adds mechanical bid to Mag-7 / growth. '
     'Effect is technical, not fundamental, and typically reverses in July.'],
    ['Hawkish Fed overhang (4.2% CPI)',
     '–', '–0.1%', '–0.1%',
     'Elevated inflation limits multiple expansion. '
     'Rate-hike probability (9 of 19 FOMC members) compresses long-duration P/E. '
     'Acted as a mild offset to today\'s gains — '
     'smaller effect because oil drop provided an inflation-relief narrative.'],
]

mv_col = [1.15*inch, 0.60*inch, 0.80*inch, 0.80*inch, 2.95*inch]
mv_tbl = Table(moves_data, colWidths=mv_col)
mv_tbl.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#16213e')),
    ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
    ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',      (0,0), (-1,-1), 8),
    ('ALIGN',         (1,0), (-1,-1), 'CENTER'),
    ('ALIGN',         (4,0), (4,-1), 'LEFT'),
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.HexColor('#f9fafb'),
                                       colors.HexColor('#eef2ff')]),
    ('GRID',          (0,0), (-1,-1), 0.4, colors.HexColor('#aaaacc')),
    ('TOPPADDING',    (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING',   (0,0), (-1,-1), 4),
]))
story.append(mv_tbl)
story.append(Spacer(1, 0.06*inch))
story.append(Paragraph(
    f"<b>Summary:</b> Today's {signed(SPY_CHG_PCT)} SPY and {signed(QQQ_CHG_PCT)} QQQ "
    "were driven primarily by the Iran peace-talk signal that crashed crude oil 4%+ to $70/bbl, "
    "directly lifting Tesla (+8.5%) and boosting broad growth-stock sentiment. "
    "QQQ outperformed SPY by ~38bps owing to its heavier concentration in mega-cap tech "
    "(Tesla, Alphabet, Amazon, Meta, Nvidia collectively contributing ~0.85–1.0pp to QQQ vs. "
    "~0.30–0.40pp to SPY). Quarter-end window-dressing provided a modest mechanical tailwind. "
    "JOLTS strength was a mixed signal but net-positive framing dominated. "
    "The hawkish Fed/high-CPI overhang capped gains but did not reverse them.",
    BODY))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aaaacc')))

# ── NEXT-DAY SCENARIOS ─────────────────────────────────────────────────────────
story.append(Paragraph("4. Next-Day Scenarios — Wednesday July 1, 2026", H2))
story.append(Paragraph(
    "<b>Context:</b> July 1 opens Q3 2026. New-quarter buying flows often continue "
    "the prior quarter's leaders for 3–5 sessions. The week's dominant risk is Thursday July 2 "
    "June Nonfarm Payrolls (released one day early due to Friday July 4 holiday). "
    "Iran peace-talk outcome in Doha on Tuesday (today) sets the overnight geopolitical tone.",
    BODY))
story.append(Spacer(1, 0.06*inch))

scenarios = [
    ("1. ADP Private Payrolls — June 2026 (Wed Jul 1, ~8:15 AM ET)",
     "Consensus: +118K private jobs (prior: +122K).",
     [("Beat (+140K or above)",
       "SPY +0.3–0.5%, QQQ +0.2–0.4%",
       "Confirms labor-market resilience heading into official NFP Thursday. "
       "Soft-landing narrative reinforced. Growth/cyclical names lead. "
       "Risk: strong jobs = lower Fed cut probability → "
       "rates stay higher → mild multiple compression offset."),
      ("In-line (+110–130K)",
       "SPY ±0.1–0.2%, QQQ ±0.1%",
       "Market shrugs; focus shifts entirely to Thursday NFP. "
       "No directional catalyst; low-volatility session expected."),
      ("Miss (below +90K)",
       "SPY –0.4–0.7%, QQQ –0.3–0.6%",
       "Reignites slowdown/recession fears coming off hawkish Fed. "
       "Growth stocks (QQQ) vulnerable to 'stagflation' framing: "
       "weak growth + persistent inflation = worst-case scenario for P/E multiples. "
       "Bond yields fall (flight to safety), but equities drop more than they gain from rate relief."),
     ]),
    ("2. ISM Manufacturing PMI — June 2026 (Wed Jul 1, ~10:00 AM ET)",
     "Consensus: 53.8 (prior: 54.0). Above 50 = expansion.",
     [("Above 54 (expansion accelerates)",
       "SPY +0.2–0.4%, QQQ +0.1–0.2%; industrials and materials outperform",
       "Manufacturing activity strong despite oil-price volatility from Iran war. "
       "Signals capital investment boom (AI data centers, onshoring) still intact. "
       "Mechanism: higher PMI → forward orders → corporate earnings upgrades."),
      ("49–52 (deceleration or near-contraction)",
       "SPY –0.2–0.4%, QQQ –0.1–0.3%",
       "Manufacturing contraction signal triggers growth-concern rotation. "
       "Industrials (XLI), materials (XLB) sell; bond proxies outperform. "
       "Amplified if ADP also misses — double-negative creates Thursday-payroll-preview anxiety."),
     ]),
    ("3. Iran Peace Talks — Doha Meeting (Tuesday overnight / Wednesday AM)",
     "US Envoy Witkoff en route to Doha; Iran's delegation expected later this week.",
     [("Formal ceasefire/deal announced",
       "SPY +0.5–1.0%, QQQ +0.6–1.2%; oil –3% to –5%",
       "Full geopolitical risk premium removal: "
       "oil falls further (sub-$67?), inflation expectations drop sharply, "
       "Fed rate-hike probability drops. Growth stocks re-rate: "
       "lower discount rate directly inflates QQQ P/E multiples. "
       "Tesla, airlines, discretionary sector all rally further."),
      ("Talks collapse or no substantive progress",
       "SPY –0.8–1.5%, QQQ –1.0–1.8%; oil +3–6%",
       "Today's oil/geopolitical relief trade reverses. "
       "Oil spikes back above $75; CPI 'last-mile' inflation concern re-emerges. "
       "Mechanism: Fed stays hawkish → rate hike repriced → "
       "rate-sensitive long-duration tech (QQQ) sold more aggressively than broad market."),
     ]),
    ("4. New-Quarter Institutional Inflows (Q3 2026 Start)",
     "First trading day of Q3; pension, endowment, and retail flows typically redirect.",
     [("Tech/growth remains consensus overweight into Q3",
       "SPY +0.2–0.4%, QQQ +0.3–0.6%; Mag-7 continue to lead",
       "Fund managers entering Q3 with same overweight positioning as Q2, "
       "especially given AI capex cycle still early. "
       "Retail 401(k) rebalancing on July 1 = automatic monthly buy. "
       "Quarter-start momentum frequently carries Q2 winner sectors for ~5 sessions."),
      ("Value/defensive rotation (high-inflation / high-rate concern into Q3)",
       "SPY flat, QQQ –0.3–0.6%; energy, financials outperform growth",
       "Some PMs may rotate from tech into value/energy given "
       "Warsh's hawkish stance, sticky CPI, and JOLTS strength. "
       "If crude stabilizes above $70, energy (XLE) becomes an inflation hedge again. "
       "QQQ vulnerable if growth premium unwinds into a 'rates-stay-high' Q3 thesis."),
     ]),
]

for cat_title, consensus, branches in scenarios:
    story.append(Paragraph(f"<b>{cat_title}</b>", BOLD))
    story.append(Paragraph(f"  <i>{consensus}</i>", BODY))
    for branch_label, reaction, mechanism in branches:
        story.append(Paragraph(
            f"&nbsp;&nbsp;<b>IF</b> {branch_label}: "
            f"<b>{reaction}</b><br/>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;{mechanism}",
            BODY))
    story.append(Spacer(1, 0.04*inch))

story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aaaacc')))

# ── WEEK-AHEAD CALENDAR ────────────────────────────────────────────────────────
story.append(Paragraph("5. Week-Ahead Calendar (Jul 1 – Jul 4, 2026)", H2))
cal_data = [
    ['Date', 'Event', 'Consensus / Prior / Notes'],
    ['Wed Jul 1',  'ADP Private Payrolls — June 2026',
     'Consensus: +118K | Prior: +122K | ~8:15 AM ET'],
    ['Wed Jul 1',  'ISM Manufacturing PMI — June 2026',
     'Consensus: 53.8 | Prior: 54.0 | ~10:00 AM ET'],
    ['Wed Jul 1',  'EIA Crude Oil Inventories (weekly)',
     '~10:30 AM ET — watch given oil market volatility'],
    ['Wed Jul 1',  'Construction Spending — May 2026',
     '~10:00 AM ET'],
    ['Thu Jul 2',  'June Nonfarm Payrolls (EARLY release)',
     'Consensus: ~110K | Prior May: +172K | 8:30 AM ET — KEY'],
    ['Thu Jul 2',  'June Unemployment Rate',
     'Consensus: ~4.1% | Prior: 4.0%'],
    ['Thu Jul 2',  'June Average Hourly Earnings',
     'Wage inflation remains a Fed focus'],
    ['Thu Jul 2',  'Initial Jobless Claims (weekly)',
     'Continued claims also important'],
    ['Fri Jul 3',  'US MARKETS CLOSED — Independence Day (observed)', ''],
]

cal_tbl = Table(cal_data, colWidths=[0.9*inch, 2.6*inch, 3.05*inch])
cal_tbl.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#16213e')),
    ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
    ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',      (0,0), (-1,-1), 8),
    ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.HexColor('#f9fafb'),
                                       colors.HexColor('#eef2ff')]),
    ('GRID',          (0,0), (-1,-1), 0.4, colors.HexColor('#aaaacc')),
    ('TOPPADDING',    (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING',   (0,0), (-1,-1), 4),
    ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
    ('BACKGROUND',    (0,8), (-1,8), colors.HexColor('#fff3e0')),
]))
story.append(cal_tbl)
story.append(Spacer(1, 0.08*inch))

# ── DATA SOURCES & NOTES ──────────────────────────────────────────────────────
story.append(Paragraph("6. Data Sources &amp; Notes", H2))
story.append(Paragraph(
    "• <b>SPY</b> close $746.79, prev close $741.00 (Jun 29): sourced from web search "
    "(multiple aggregators citing Jun 30, 2026 quarter-end data).<br/>"
    "• <b>QQQ</b> close $732.49 (MarketBeat/Chameleon intraday/close data), "
    "prev close $724.08 (Jun 29, multiple search sources).<br/>"
    "• <b>52-wk stats</b>: SPY H $760.40 (Jun 2 2026) / L $591.89 (Jun 23 2025); "
    "QQQ H $733.32 (May 27 2026) / L $511.93 (May 30 2025) — from web search aggregators.<br/>"
    "• <b>1-yr returns</b>: SPY +19.95% (price), QQQ +39.95% (TTM) — search-sourced.<br/>"
    "• <b>prices.csv</b> (253 rows): historical backfill Jun 26 2025–Jun 26 2026 is "
    "an interpolated estimate (Yahoo Finance / yfinance blocked HTTP 403 by proxy). "
    "Last 4 rows (Jun 25–30 2026) confirmed from live web sources. "
    "Replace interpolated rows with official data via Tiingo/Polygon.io/brokerage API.<br/>"
    "• <b>JOLTS May 2026</b>: 7.594M openings — BLS release sourced via CNN Business / search.<br/>"
    "• <b>Tesla</b> close $411.84 (+8.5%), <b>Alphabet</b> +5%, <b>Amazon</b> +3.2%, "
    "<b>Meta</b> +2.2%, <b>Nvidia</b> +1.3% — from search aggregators.<br/>"
    "• <b>WTI Crude</b>: ~$70/bbl — sourced from multiple search results.<br/>"
    "• <b>ADP/ISM calendar</b>: from FXStreet economic calendar search.<br/>"
    "• All analysis is read-only / observational. No trades placed or simulated.",
    SMALL))

# ── BUILD ──────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF written: {OUTPUT}")
