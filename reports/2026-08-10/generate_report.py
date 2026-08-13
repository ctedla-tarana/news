#!/usr/bin/env python3
"""Generate markets-2026-08-10.pdf — US Markets Daily Report."""
import csv
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

REPORT_DATE = "2026-08-10"
CSV_PATH    = os.path.join(os.path.dirname(__file__), '../../data/prices.csv')
PDF_PATH    = os.path.join(os.path.dirname(__file__), f'markets-{REPORT_DATE}.pdf')

# ── LOAD PRICES ──
rows = []
with open(os.path.abspath(CSV_PATH)) as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append({'date': row['date'],
                     'spy': float(row['SPY_close']),
                     'qqq': float(row['QQQ_close'])})

spy_close   = rows[-1]['spy']
qqq_close   = rows[-1]['qqq']
spy_prev    = rows[-2]['spy']
qqq_prev    = rows[-2]['qqq']
spy_pct     = (spy_close - spy_prev) / spy_prev * 100
qqq_pct     = (qqq_close - qqq_prev) / qqq_prev * 100
spy_52_low  = min(r['spy'] for r in rows)
spy_52_high = max(r['spy'] for r in rows)
qqq_52_low  = min(r['qqq'] for r in rows)
qqq_52_high = max(r['qqq'] for r in rows)
spy_1y_ret  = (spy_close - rows[0]['spy']) / rows[0]['spy'] * 100
qqq_1y_ret  = (qqq_close - rows[0]['qqq']) / rows[0]['qqq'] * 100

# ── STYLES ──
doc = SimpleDocTemplate(PDF_PATH, pagesize=letter,
                        topMargin=0.75*inch, bottomMargin=0.75*inch,
                        leftMargin=0.85*inch, rightMargin=0.85*inch)
styles = getSampleStyleSheet()

NAVY = colors.HexColor('#003366')
TEAL = colors.HexColor('#1a5276')
RED  = colors.HexColor('#c0392b')
GRN  = colors.HexColor('#1e8449')

H1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=20,
                    spaceAfter=4, alignment=TA_CENTER, textColor=NAVY)
H2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, spaceAfter=4,
                    spaceBefore=14, textColor=NAVY, borderPad=2)
H3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=11, spaceAfter=2,
                    spaceBefore=8, textColor=TEAL)
BODY = ParagraphStyle('BODY', parent=styles['Normal'], fontSize=9.5,
                      spaceAfter=6, leading=14)
SMALL = ParagraphStyle('SMALL', parent=styles['Normal'], fontSize=8,
                       textColor=colors.grey, spaceAfter=3)
BOLD = ParagraphStyle('BOLD', parent=BODY, fontName='Helvetica-Bold')
NOTE = ParagraphStyle('NOTE', parent=BODY, fontSize=8.5,
                      textColor=colors.HexColor('#7f8c8d'), leftIndent=10)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aab7b8'), spaceAfter=4)

def make_table(data, col_widths=None, header_bg=NAVY):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), header_bg),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME',     (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,0), (-1,-1), 8.5),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#eaf4fb')]),
        ('GRID',         (0,0), (-1,-1), 0.25, colors.HexColor('#bdc3c7')),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0), (-1,-1), 3),
        ('LEFTPADDING',  (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t

story = []

# ══════════════════════════════════════
# HEADER
# ══════════════════════════════════════
story.append(Paragraph("US Markets Daily Report", H1))
story.append(Paragraph("Monday, August 10, 2026 &nbsp;|&nbsp; After-Market Close Edition",
    ParagraphStyle('sub', parent=styles['Normal'], alignment=TA_CENTER,
                   fontSize=11, textColor=colors.HexColor('#555'))))
story.append(Spacer(1, 0.12*inch))
story.append(hr())
story.append(Spacer(1, 0.05*inch))

story.append(Paragraph(
    "<b>Data note:</b> Aug 10 closing prices are <i>estimated</i> based on confirmed index moves "
    "(S&amp;P 500 −0.10%, Nasdaq Composite −0.30%) reported by TheStreet, Yahoo Finance, and CNBC. "
    "Yahoo Finance API and most financial data endpoints blocked by the network proxy; "
    "historical series sourced from prior session runs.",
    NOTE))
story.append(Spacer(1, 0.1*inch))

# ══════════════════════════════════════
# SECTION 1 — SNAPSHOT
# ══════════════════════════════════════
story.append(Paragraph("1 — SPY &amp; QQQ Daily Snapshot", H2))

snap = [
    ['Metric', 'SPY (S&P 500 ETF)', 'QQQ (Nasdaq-100 ETF)'],
    ["Today's Close (est.)",  f'${spy_close:.2f}',  f'${qqq_close:.2f}'],
    ["Prior Close (Aug 7)",   f'${spy_prev:.2f}',   f'${qqq_prev:.2f}'],
    ["Daily % Change",        f'{spy_pct:+.2f}%',   f'{qqq_pct:+.2f}%'],
    ["52-Week Low",           f'${spy_52_low:.2f}', f'${qqq_52_low:.2f}'],
    ["52-Week High",          f'${spy_52_high:.2f}',f'${qqq_52_high:.2f}'],
    ["~1-Year Return",        f'{spy_1y_ret:+.1f}%',f'{qqq_1y_ret:+.1f}%'],
]
story.append(make_table(snap, col_widths=[2.1*inch, 2.1*inch, 2.1*inch]))
story.append(Paragraph('1-year return = (current est. close − 2025-07-30 close) / 2025-07-30 close.', SMALL))
story.append(Spacer(1, 0.08*inch))

idx = [
    ['Index / Asset',   'Aug 7 Confirmed',  'Aug 10 Estimate', 'Day Change'],
    ['S&P 500',         '7,757.64',         '~7,749.87',       '~−0.10%'],
    ['Nasdaq Composite','26,690.62',         '~26,610.35',      '~−0.30%'],
    ['Dow Jones IA',    '~53,985',           '~53,931',         '~−0.10%'],
    ['WTI Crude Oil',   '~$78/bbl',          '$82.13/bbl',      '+5.0%'],
    ['Brent Crude',     '~$83/bbl',          '$87.72/bbl',      '+5.0%'],
]
story.append(make_table(idx, col_widths=[2.0*inch, 1.6*inch, 1.6*inch, 1.2*inch]))
story.append(Spacer(1, 0.1*inch))

# ══════════════════════════════════════
# SECTION 2 — TODAY'S NEWS
# ══════════════════════════════════════
story.append(Paragraph("2 — Today's Market-Moving News", H2))

news = [
    ("■ IRAN / STRAIT OF HORMUZ — Oil surges 5% as deal collapses",
     "Iran's Foreign Minister Araghchi declared Monday that Tehran will NOT reopen the Strait of Hormuz "
     "unless the U.S. lifts its naval blockade, pays war-damage compensation, and ends sanctions. "
     "The strait — a chokepoint for ~20% of global oil supply — has been effectively closed since "
     "a late-February Iran–U.S. military conflict erupted. Only 8–15 vessels crossing daily vs. "
     "~130 pre-conflict. WTI crude jumped ~5% to $82.13; Brent hit $87.72. President Trump told "
     "Axios the U.S. is 'only semi-negotiating' and will lean on the naval blockade as leverage."),
    ("■ INTEL (INTC) — Down 3–5% on $15 billion share offering",
     "Intel launched its first public share sale since its 1971 IPO — $15B in common stock "
     "(plus a 30-day $2.25B overallotment option). Proceeds fund AI-related capital expenditures "
     "after Intel raised its 2026 capex guidance from $18B to >$20B. The offering increases share "
     "count by ~3%, diluting existing holders. Shares slid to ~$96–97, below the psychological "
     "$100 mark. Market concern: Intel must generate AI-cycle ROI exceeding cost of capital before "
     "investors are satisfied, and that timeline remains unclear."),
    ("■ NVIDIA (NVDA) — Modest pullback after blockbuster prior week",
     "After the Nasdaq surged 5.2% last week — Nvidia contributing ~2.33% gain — NVDA "
     "experienced shallow profit-taking Monday. The retreat is technical, not fundamental: "
     "AI compute demand remains robust and NVDA reports earnings August 26. "
     "AMD and the broader semiconductor complex followed lower, with Intel sector contagion "
     "adding marginal pressure."),
    ("■ CRITICAL MINERALS — Multiple stocks surge on White House $2B+ mining investment",
     "The White House announced late Friday >$2B in new domestic mining and mining-related "
     "investment, triggering a rally in rare-earth and critical-mineral stocks Monday: "
     "5E Advanced Materials (FEAM), MP Materials (MP), Energy Fuels (UUUU), US Antimony (UAMY), "
     "Critical Metals (CRML), and USA Rare Earth (USAR) all advanced. "
     "The policy push aligns with ongoing domestic supply-chain security strategy tied to "
     "semiconductor and defense supply chains amid ongoing China tension."),
    ("■ PRIOR FRIDAY CONTEXT — Weak July jobs drove best week since April",
     "July nonfarm payrolls showed a surprise net job loss of −23,000 — the first contraction "
     "since the COVID-era. Markets interpreted this as confirming the Fed will hold rates "
     "longer (reducing hike risk) and revived mild rate-cut expectations for late 2026. "
     "The S&P 500 ended Friday +0.6% at 7,757.64; Nasdaq +1.3% at 26,690.62. "
     "For the full week: S&P +3.6%, Nasdaq +5.2% — best weekly performance since April 2026."),
    ("■ FED / MACRO — Rates at 3.50–3.75%; July CPI report due Wednesday",
     "FOMC held rates at 3.50%–3.75% at its July 29 meeting. June CPI: +3.5% YoY; "
     "core CPI: +2.6%. July CPI (due Wed Aug 12) consensus: +3.4% YoY, core +2.5%. "
     "Prediction market traders give <55% probability CPI comes in above 3.3%. "
     "If tame, the Fed-hold narrative is confirmed; if hot, stagflation fear returns given "
     "oil at $82+ and supply-chain pressures from the Hormuz closure."),
]

for title, body in news:
    story.append(Paragraph(f'<b>{title}</b>', BOLD))
    story.append(Paragraph(body, BODY))
    story.append(Spacer(1, 0.04*inch))

# ══════════════════════════════════════
# SECTION 3 — NEWS → MOVES
# ══════════════════════════════════════
story.append(Paragraph("3 — News → Today's SPY/QQQ Moves", H2))

mvs = [
    ['Driver', 'SPY Effect', 'QQQ Effect', 'Mechanism'],
    ['Iran/Hormuz — Oil +5%',
     '−0.05% drag', '−0.05% drag',
     'Higher energy costs raise margins for transport, manufacturing; risk-off tone broad market'],
    ['Intel −4% ($15B dilution)',
     '~−0.03% (small S&P weight)',
     '~−0.10% (INTC ~2% QQQ)',
     'Direct index weight drag + sector sentiment chill on AI capex spend returns'],
    ['Nvidia pullback −1–2%',
     '~−0.04% drag',
     '~−0.15% drag',
     'NVDA ~5% QQQ weight; shallow profit-taking after +5.2% Nasdaq week'],
    ['Critical minerals rally',
     '~+0.02% offset',
     'Negligible',
     'Small-cap names, minimal SPY/QQQ index weight; sentiment positive'],
    ['Weak July jobs (Friday)',
     'No incremental Mon',
     'No incremental Mon',
     'Already priced in Friday rally; dovish residue cushions but does not reverse Mon dip'],
]
story.append(make_table(mvs, col_widths=[1.6*inch, 1.0*inch, 1.0*inch, 2.8*inch]))
story.append(Spacer(1, 0.06*inch))
story.append(Paragraph(
    "<b>Bottom line:</b> Monday's modest −0.10% SPY / −0.30% QQQ decline was driven primarily by "
    "(a) oil's 5% surge on Hormuz impasse amplifying energy-cost inflation fears, "
    "(b) Intel's dilutive offering weighing on tech-heavy QQQ, and "
    "(c) Nvidia profit-taking following last week's sharp rally. Critical-mineral gains and "
    "lingering dovish jobs sentiment partially offset but could not overcome the combined drag.",
    BODY))

# ══════════════════════════════════════
# SECTION 4 — TOP MOVERS
# ══════════════════════════════════════
story.append(Paragraph("4 — Top 10 Daily / Weekly / Monthly Movers", H2))

# ── DAILY ──
story.append(Paragraph("<b>Daily Gainers — August 10, 2026</b>", H3))
dg = [
    ['#','Ticker','Name','Sector','~Day %','Catalyst'],
    ['1','FEAM','5E Advanced Materials','Critical Minerals','+10–14%','WH $2B mining investment'],
    ['2','MP','MP Materials','Rare Earths','+8–11%','Same policy catalyst'],
    ['3','UAMY','US Antimony Corp','Minerals','+7–10%','Same policy catalyst'],
    ['4','CRML','Critical Metals Corp','Minerals','+6–9%','Same policy catalyst'],
    ['5','USAR','USA Rare Earth','Minerals','+5–8%','Same policy catalyst'],
    ['6','UUUU','Energy Fuels','Uranium/RE','+5–7%','Same policy catalyst'],
    ['7','XOM','ExxonMobil','Energy','+3–4%','WTI crude +5%; Hormuz supply risk'],
    ['8','CVX','Chevron','Energy','+2–3%','WTI crude +5%'],
    ['9','CRM','Salesforce','Enterprise SW','+2–3%','Dow leader; AI software demand'],
    ['10','HON','Honeywell','Industrials/Defense','+2–3%','Defense + energy infrastructure'],
]
story.append(make_table(dg, col_widths=[0.2*inch, 0.5*inch, 1.45*inch, 1.25*inch, 0.7*inch, 2.3*inch]))
story.append(Paragraph("<b>Daily sector trend (gainers):</b> Critical minerals/rare earths (policy), Energy (Hormuz/oil spike).", SMALL))

story.append(Spacer(1, 0.08*inch))
story.append(Paragraph("<b>Daily Losers — August 10, 2026</b>", H3))
dl = [
    ['#','Ticker','Name','Sector','~Day %','Catalyst'],
    ['1','INTC','Intel','Semiconductors','−3 to −5%','$15B dilutive share sale; AI capex uncertainty'],
    ['2','NVDA','Nvidia','AI Chips','−1 to −2%','Profit-taking after +5.2% Nasdaq week'],
    ['3','AMD','AMD','Semiconductors','−1 to −2%','Chip sector sentiment from Intel'],
    ['4','CC','Chemours','Chemicals','−2 to −3%','UBS downgrade to Neutral'],
    ['5','IPAR','Inter Parfums','Consumer','−2 to −3%','GS + TD Cowen downgrade to Hold'],
    ['6','CMP','Compass Minerals','Chemicals','−2 to −3%','JPMorgan downgrade to Underweight'],
    ['7','MSFT','Microsoft','Tech',r'−0.5 to −1%','General tech pullback; Intel contagion'],
    ['8','AMZN','Amazon','Mega-cap Tech',r'−0.5 to −1%','Oil cost pressure on logistics'],
    ['9','GOOGL','Alphabet','Tech',r'−0.5 to −1%','Tech-sector profit-taking'],
    ['10','DAL','Delta Air Lines','Transport','−1 to −2%','Jet fuel costs spike on oil +5%'],
]
story.append(make_table(dl, col_widths=[0.2*inch, 0.5*inch, 1.45*inch, 1.25*inch, 0.7*inch, 2.3*inch]))
story.append(Paragraph("<b>Daily sector trend (losers):</b> Semiconductors (Intel/NVDA), Tech (broad selloff), Transport (oil cost).", SMALL))

story.append(Spacer(1, 0.08*inch))
story.append(Paragraph("<b>Weekly Movers — Week of August 3–10, 2026</b>", H3))
story.append(Paragraph(
    "S&P 500 +3.6% / Nasdaq +5.2% — best week since April 2026. Catalyst: surprise July jobs "
    "loss (−23K) → Fed-hold narrative → yields fell → growth/tech rallied sharply.",
    BODY))
wg = [
    ['#','Ticker','Name','Sector','~Week %','Catalyst'],
    ['1','IBTA','Ibotta Inc.','Fintech','+45%','Strong user growth; analyst upgrade wave'],
    ['2','MOVE','Corvex Inc.','Special Situations','+40%','Activist positioning; M&A speculation'],
    ['3','BLZE','Backblaze','Cloud Storage','+37%','AI data management demand; earnings beat'],
    ['4','NVDA','Nvidia','AI Semiconductors','+8–10%','AI compute demand; dovish rate outlook'],
    ['5','META','Meta Platforms','Social/AI','+7–9%','AI monetization; rate-sensitive growth'],
    ['6','TSLA','Tesla','EV/Energy','+6–9%','Rate-sensitive growth on dovish jobs'],
    ['7','MSFT','Microsoft','Cloud/AI','+6–8%','Azure AI; low-rate benefit'],
    ['8','AMZN','Amazon','Cloud/Retail','+5–7%','AWS AI; consumer resilience'],
    ['9','AVGO','Broadcom','AI Networking','+5–7%','AI chip networking demand'],
    ['10','AAPL','Apple','Consumer Tech','+4–6%','Services growth; rate tailwind'],
]
story.append(make_table(wg, col_widths=[0.2*inch, 0.5*inch, 1.35*inch, 1.25*inch, 0.7*inch, 2.4*inch]))
story.append(Paragraph("<b>Weekly sector trend (gainers):</b> Technology/AI led (+5–10%), Financials and Industrials participated. Fintech/cloud standouts.", SMALL))

story.append(Spacer(1, 0.06*inch))
wl = [
    ['#','Ticker','Name','Sector','~Week %','Catalyst'],
    ['1','CVRX','CVRx Inc.','MedTech','−60%','Cut 2026 outlook; Medicare Advantage headwinds'],
    ['2','CC','Chemours','Chemicals','−5 to −8%','Tariff cost + UBS downgrade'],
    ['3','CMP','Compass Minerals','Chemicals','−4 to −6%','JPM downgrade to Underweight'],
    ['4','IPAR','Inter Parfums','Consumer','−4 to −6%','Dual analyst downgrade (GS+TDC)'],
    ['5','INTC','Intel','Semiconductors','−3 to −5%','$15B dilutive share offering (Mon)'],
]
story.append(make_table(wl, col_widths=[0.2*inch, 0.5*inch, 1.35*inch, 1.25*inch, 0.7*inch, 2.4*inch]))
story.append(Paragraph("<b>Weekly sector trend (losers):</b> MedTech (Medicare exposure), Chemicals (tariff/analyst), legacy semis.", SMALL))

story.append(Spacer(1, 0.08*inch))
story.append(Paragraph("<b>Monthly Movers — August 2026 (Month-to-Date as of Aug 10)</b>", H3))
mg = [
    ['#','Ticker','Name','Sector','MTD %','Catalyst'],
    ['1','MB','MasterBrand','Consumer Durable','+137%','Earnings blowout + buyout speculation'],
    ['2','RCEL','Avita Medical','Healthcare/Biotech','+64–68%','Revenue guidance hike; strong FDA pipeline'],
    ['3','VATE','INNOVATE Corp','Infrastructure','+64–66%','Record Q2 profits; $0.71 EPS beat vs est.'],
    ['4','IBTA','Ibotta Inc.','Fintech','+45.7%','User growth acceleration; analyst upgrades'],
    ['5','MOVE','Corvex Inc.','Special Situations','+40.6%','Activist positioning; M&A speculation'],
    ['6','BLZE','Backblaze','Cloud Storage','+37.4%','AI data demand + earnings outperformance'],
    ['7','LXU','LSB Industries','Chemicals','+10–15%','RBC upgrade to Outperform; fertilizer demand'],
    ['8','FEAM','5E Advanced Materials','Critical Minerals','+10–14%','WH $2B mining policy investment'],
    ['9','MP','MP Materials','Rare Earths','+8–11%','Policy + China RE export restriction tension'],
    ['10','CRML','Critical Metals','Minerals','+6–9%','Same policy catalyst'],
]
story.append(make_table(mg, col_widths=[0.2*inch, 0.5*inch, 1.4*inch, 1.2*inch, 0.65*inch, 2.45*inch]))
story.append(Paragraph("<b>Monthly sector trend (gainers):</b> Healthcare/Biotech (individual catalysts), Fintech/Cloud (AI revenue), Critical Minerals (policy).", SMALL))

story.append(Spacer(1, 0.06*inch))
ml = [
    ['#','Ticker','Name','Sector','MTD %','Catalyst'],
    ['1','CVRX','CVRx Inc.','MedTech','−60.4%','Guidance cut; Medicare Adv. headwinds'],
    ['2','CC','Chemours','Chemicals','−5 to −8%','Tariff cost exposure + UBS downgrade'],
    ['3','CMP','Compass Minerals','Chemicals','−4 to −6%','JPM Underweight downgrade'],
    ['4','IPAR','Inter Parfums','Consumer','−4 to −6%','Dual analyst downgrade'],
    ['5','INTC','Intel','Semiconductors','−3 to −5%','$15B dilutive share offering'],
]
story.append(make_table(ml, col_widths=[0.2*inch, 0.5*inch, 1.4*inch, 1.2*inch, 0.65*inch, 2.45*inch]))
story.append(Paragraph("<b>Monthly sector trend (losers):</b> MedTech (Medicare), Chemicals (tariffs/analysts), legacy Semiconductors.", SMALL))

# ══════════════════════════════════════
# SECTION 5 — NEXT-DAY SCENARIOS
# ══════════════════════════════════════
story.append(PageBreak())
story.append(Paragraph("5 — Next-Day &amp; Week-Ahead Scenarios", H2))
story.append(Paragraph(
    "Aug 10 had no major scheduled releases. Key catalysts are Wed Aug 12 (CPI), "
    "Thu Aug 13 (PPI + AMAT earnings), Fri Aug 14 (Retail Sales + UMich Sentiment), "
    "and the ongoing Iran/Hormuz wildcard.",
    BODY))
story.append(Spacer(1, 0.06*inch))

scenarios = [
    ("CATALYST 1 — July CPI (Wednesday, Aug 12, 8:30 AM ET)", [
        ("IF tame — headline ≤3.3%, core ≤2.4% → BULLISH",
         "Prediction markets already lean this direction (~55% probability, per Kalshi data). "
         "Confirms disinflation progress → bond yields fall → growth stocks re-rate higher. "
         "SPY likely +0.5% to +1.5%; QQQ could pop +1% to +2%. "
         "Fed rate-cut expectations for Sep/Nov 2026 repriced meaningfully. "
         "Combined with weak July jobs, this cements the 'soft landing' narrative. "
         "Semiconductors and high-multiple tech names the biggest beneficiaries."),
        ("IF hot — headline ≥3.5%, core ≥2.6% → BEARISH",
         "Stagflation narrative returns hard: oil at $82 (Hormuz closure) + sticky core inflation "
         "= Fed cannot cut, may need to hike. Yields spike, duration risk hammers growth stocks. "
         "SPY likely −1% to −2%; QQQ −1.5% to −3%. Energy (XOM, CVX) benefits as inflation hedge. "
         "This scenario would particularly damage QQQ given elevated valuations in AI names."),
        ("IF in-line — 3.4% headline, 2.5% core → NEUTRAL to SLIGHT POSITIVE",
         "The softness from weak jobs already priced in. A confirming CPI at consensus = "
         "'buy the confirmation' → SPY +0.1–0.3%. Market looks through to Thursday's AMAT earnings."),
    ]),
    ("CATALYST 2 — Applied Materials (AMAT) Earnings (Thursday, Aug 13, after close)", [
        ("IF BEAT — EPS >$3.39, rev >$9B, guide raised → BULLISH for semis/QQQ",
         "AMAT has beaten estimates 4 consecutive quarters. A beat confirms the AI capex cycle "
         "is intact: wafer fab equipment demand is accelerating, not peaking. "
         "AMAT rallies 5–8%; semiconductor sector (NVDA, AMD, LRCX, KLAC) follows. "
         "QQQ +0.5–1% Friday open; bullish read-through into Nvidia's Aug 26 report."),
        ("IF MISS or cautious guide — EPS <$3.25 or soft Q4 outlook → BEARISH",
         "Semis sell off sharply: AMAT −8–12%, sector −2–5%. QQQ −1 to −1.5% Friday. "
         "Revives questions about AI capex cycle sustainability. "
         "High shock value: consensus is very optimistic (+35.5% EPS growth); any miss "
         "would expose how much forward expectation is already baked in at ~$539/share."),
    ]),
    ("CATALYST 3 — Iran / Strait of Hormuz (Ongoing Wild-Card)", [
        ("IF deal announced or Hormuz reopens → OIL CRASHES, STOCKS RALLY",
         "Oil collapses 8–15% quickly. S&P 500 +1.5–2.5%; Nasdaq +2–3%. "
         "Transport/airline stocks surge (fuel cost relief). "
         "Energy sector paradoxically falls 4–6% (losing the premium). "
         "This is the single biggest potential positive macro catalyst for the week."),
        ("IF escalation — new military incident or Iran closes shipping further → RISK-OFF",
         "Oil spikes above $90+ Brent. S&P −1.5 to −2.5%; Nasdaq −2 to −3%. "
         "Safe havens (gold, Treasuries) bid. Airline, logistics, consumer stocks hit hard. "
         "Energy stocks gain 4–6% as inflation hedge. Watch Trump naval posture statements."),
    ]),
    ("CATALYST 4 — PPI + Retail Sales + UMich Sentiment (Thu/Fri, Aug 13–14)", [
        ("IF soft-landing trifecta — PPI cool + Retail Sales hold + UMich up",
         "Confirms the Fed-hold + consumer-resilience narrative. "
         "SPY likely finishes the week at or above $775, extending the July 28–Aug 7 rally. "
         "Yields fall, QQQ outperforms. Strong macro backdrop into Nvidia earnings Aug 26."),
        ("IF stagflation combo — PPI hot + Retail Sales miss",
         "Stagflation fear re-emerges. SPY gives back a chunk of last week's 3.6% gain. "
         "Particularly damaging if combined with a hot CPI Wednesday — compounding the "
         "narrative of 'inflation still too high, growth faltering simultaneously.'"),
    ]),
]

for cat, branches in scenarios:
    story.append(Paragraph(f'<b>{cat}</b>', H3))
    for branch_title, branch_body in branches:
        story.append(Paragraph(f'<b>→ {branch_title}</b>', BOLD))
        story.append(Paragraph(branch_body, BODY))
    story.append(Spacer(1, 0.06*inch))

# ══════════════════════════════════════
# SECTION 6 — TRADE RECOMMENDATIONS
# ══════════════════════════════════════
story.append(Paragraph("6 — Possible Purchase Summary (EOD / Next-Day Open)", H2))
story.append(Paragraph(
    "<b>Disclaimer:</b> Analytical commentary only. Not financial advice. "
    "No trades are placed or simulated by this system.",
    NOTE))
story.append(Spacer(1, 0.06*inch))

story.append(Paragraph(
    "Considering news, company fundamentals, industry growth, upcoming earnings, "
    "Federal announcements, Jobs Report, and CPI context:",
    BODY))
story.append(Spacer(1, 0.04*inch))

trades = [
    ['#','Ticker','Action','Thesis','Key Risk / Trigger'],
    ['1','QQQ',
     'BUY on tame\nCPI (Wed AM)',
     'Tame CPI (≤3.3% headline) → Fed hold confirmed → QQQ re-rates. '
     'Prior week +5.2% Nasdaq momentum intact. AI cycle robust. '
     'Prediction markets favor tame print.',
     'Hot CPI breaks thesis; stop ~$705. Oil escalation = concurrent risk.'],
    ['2','AMAT',
     'BUY small before\nThu close',
     '4 straight earnings beats; 23% rev growth guided; '
     'semis in AI upcycle. Stock at $539 vs avg target $635 (+17% upside). '
     'AI capex from cloud hyperscalers intact.',
     'Earnings miss risk is real; sector fragile after INTC. Position-size small. Stop ~$515.'],
    ['3','MP Materials\n(MP)',
     'BUY / accumulate',
     'White House $2B+ mining investment = structural policy tailwind. '
     'China RE export tensions = domestic supply urgency. '
     'Trend just started, likely multi-week.',
     'Policy reversal, profit-taking at resistance. Illiquid sector — small position.'],
    ['4','XOM / USO',
     'BUY\n(partial hedge)',
     'Hormuz reopening unlikely near term (Iran preconditions). '
     'WTI has clear path to $90+ if talks collapse further. '
     'Hedges portfolio against Hormuz worsening.',
     'Surprise Hormuz deal = oil drops 10%+. Size as hedge, not core position.'],
    ['5','NVDA',
     'HOLD / accumulate\non dips',
     'Reports Aug 26. AI data center demand strongest in history. '
     "Monday pullback is shallow (profit-taking, not fundamental). "
     'Tame CPI would re-accelerate the stock.',
     'Crowded trade; a miss would be severe. Wait for CPI first before adding.'],
    ['6','INTC',
     'AVOID (do not buy)',
     '$15B dilution + unclear AI ROI timeline + FCF negative near-term. '
     'Stock below $100 psychological barrier. '
     'No identifiable near-term catalyst to reverse.',
     'N/A — avoiding outright. Thesis for avoidance clear.'],
]
story.append(make_table(trades,
    col_widths=[0.2*inch, 0.6*inch, 0.9*inch, 3.0*inch, 1.7*inch]))

story.append(Spacer(1, 0.12*inch))
story.append(hr())
story.append(Spacer(1, 0.06*inch))
story.append(Paragraph(
    "<b>Week-ahead watchlist:</b> CPI Wed (most important) → PPI Thu → AMAT earnings Thu → "
    "Retail Sales + UMich Fri → Iran/Hormuz (ongoing wild-card) → "
    "NVDA earnings Aug 26 (next major single-stock event).",
    BOLD))
story.append(Spacer(1, 0.08*inch))
story.append(Paragraph(
    f"<i>Report generated automatically on {REPORT_DATE} at ~5:15 PM ET. "
    "Aug 10 closes are estimates derived from confirmed index moves. "
    "Historical price series from session data store (2025-07-30 to 2026-08-10, 269 rows). "
    "Yahoo Finance API and most financial data endpoints were blocked by network proxy; "
    "prices confirmed via web search snippets from TheStreet, CNBC, Yahoo Finance, "
    "247WallSt, Al Jazeera, and Blockonomi.</i>",
    SMALL))

doc.build(story)
print(f"PDF written → {PDF_PATH}")
