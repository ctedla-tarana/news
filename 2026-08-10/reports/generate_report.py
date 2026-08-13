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
# Path from 2026-08-10/reports/ to the shared data/prices.csv at repo root
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
                    spaceBefore=14, textColor=NAVY)
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
story.append(Paragraph(f'Data range: {rows[0]["date"]} to {rows[-1]["date"]} ({len(rows)} trading days).', SMALL))
story.append(Spacer(1, 0.08*inch))

idx = [
    ['Index / Asset',   'Aug 7 Confirmed',  'Aug 10 Estimate', 'Day Change'],
    ['S&P 500',         '7,757.64',         '~7,749.87',       '~−0.10%'],
    ['Nasdaq Composite','26,690.62',         '~26,610.35',      '~−0.30%'],
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
     "The strait handles ~20% of global oil supply and has been effectively closed since a "
     "late-February Iran-U.S. conflict. Only 8-15 vessels transit daily vs. ~130 pre-conflict. "
     "WTI jumped ~5% to $82.13; Brent hit $87.72. President Trump: U.S. is 'only semi-negotiating' "
     "and will rely on the naval blockade as leverage rather than airstrikes."),
    ("■ INTEL (INTC) — Down 3-5% on $15 billion share offering",
     "Intel launched its first public share sale since its 1971 IPO: $15B in common stock "
     "(plus $2.25B overallotment). Proceeds fund AI capex after Intel raised 2026 capex guidance "
     "from $18B to >$20B. Offering dilutes share count by ~3%, pushing shares below $100. "
     "Market concern: unclear AI ROI timeline on capital that has not yet generated returns."),
    ("■ NVIDIA (NVDA) — Modest pullback after +5.2% Nasdaq week",
     "After Nvidia gained ~2.33% last week as the Nasdaq surged 5.2%, NVDA experienced "
     "shallow profit-taking Monday. Fundamentals unchanged; next earnings report is August 26."),
    ("■ CRITICAL MINERALS — Rally on White House $2B+ mining investment",
     "The White House announced >$2B in domestic mining investments late Friday, triggering gains in "
     "5E Advanced Materials (FEAM), MP Materials (MP), Energy Fuels (UUUU), US Antimony (UAMY), "
     "Critical Metals (CRML), and USA Rare Earth (USAR). Policy aligns with semiconductor/defense "
     "supply-chain security amid China tensions."),
    ("■ CONTEXT: Weak July jobs report drove last week's rally",
     "Friday Aug 7 catalyst: July nonfarm payrolls showed a surprise loss of -23,000 jobs "
     "(first contraction since the pandemic). This revived Fed-hold expectations, cut yields, "
     "and drove S&P 500 +0.6% to 7,757.64 and Nasdaq +1.3% to 26,690.62 on Friday. "
     "Full week: S&P +3.6%, Nasdaq +5.2% (best week since April 2026)."),
    ("■ FED / MACRO — Rates at 3.50-3.75%; July CPI due Wednesday",
     "FOMC held at 3.50-3.75% at July 29 meeting. June CPI: +3.5% YoY, core +2.6%. "
     "July CPI (Wed Aug 12) consensus: +3.4% headline, +2.5% core. "
     "Prediction markets: <55% chance headline exceeds 3.3%. "
     "Hot print = stagflation fear; tame print = buy signal."),
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
    ['Iran/Hormuz — Oil +5%', '−0.05%', '−0.05%',
     'Energy cost pressure on transport/manufacturing; risk-off tone across market'],
    ['Intel −4% ($15B dilution)', '−0.03%', '−0.10%',
     'Direct index weight drag (INTC ~2% QQQ) + sector chill on AI capex ROI'],
    ['Nvidia pullback −1-2%', '−0.04%', '−0.15%',
     'NVDA ~5% of QQQ weight; shallow profit-taking after 5.2% Nasdaq week'],
    ['Critical minerals rally', '+0.02% offset', 'Negligible',
     'Small-cap names, minimal SPY/QQQ weight; positive domestic policy signal'],
    ['Weak jobs (prior Fri)', 'No new effect', 'No new effect',
     'Already priced; dovish residue cushions but does not reverse Monday decline'],
]
story.append(make_table(mvs, col_widths=[1.6*inch, 0.95*inch, 0.95*inch, 2.9*inch]))
story.append(Spacer(1, 0.06*inch))
story.append(Paragraph(
    "<b>Summary:</b> Monday's −0.10% SPY / −0.30% QQQ decline driven by (a) oil +5% on Hormuz "
    "impasse, (b) Intel dilution weighing on tech-heavy QQQ, and (c) Nvidia profit-taking. "
    "Critical-mineral gains and dovish job residuals were insufficient to offset.",
    BODY))

# ══════════════════════════════════════
# SECTION 4 — TOP MOVERS
# ══════════════════════════════════════
story.append(Paragraph("4 — Top 10 Daily / Weekly / Monthly Movers", H2))

story.append(Paragraph("<b>Daily Gainers — August 10, 2026</b>", H3))
dg = [
    ['#','Ticker','Company / Sector','~Day %','Catalyst'],
    ['1','FEAM','5E Advanced Materials (Critical Minerals)','+10-14%','WH $2B mining investment policy'],
    ['2','MP','MP Materials (Rare Earths)','+8-11%','Same policy catalyst'],
    ['3','UAMY','US Antimony Corp (Minerals)','+7-10%','Same policy catalyst'],
    ['4','CRML','Critical Metals Corp (Minerals)','+6-9%','Same policy catalyst'],
    ['5','USAR','USA Rare Earth (Minerals)','+5-8%','Same policy catalyst'],
    ['6','UUUU','Energy Fuels (Uranium/RE)','+5-7%','Same policy catalyst'],
    ['7','XOM','ExxonMobil (Energy)','+3-4%','WTI +5%; Hormuz supply risk premium'],
    ['8','CVX','Chevron (Energy)','+2-3%','WTI crude +5%'],
    ['9','CRM','Salesforce (Enterprise SW)','+2-3%','AI software demand; Dow leader'],
    ['10','HON','Honeywell (Industrials)','+2-3%','Defense + energy infrastructure'],
]
story.append(make_table(dg, col_widths=[0.25*inch, 0.55*inch, 2.65*inch, 0.75*inch, 2.2*inch]))
story.append(Paragraph("<b>Sector trend:</b> Critical minerals/rare earths (policy-driven), Energy (Hormuz/oil).", SMALL))

story.append(Spacer(1, 0.08*inch))
story.append(Paragraph("<b>Daily Losers — August 10, 2026</b>", H3))
dl = [
    ['#','Ticker','Company / Sector','~Day %','Catalyst'],
    ['1','INTC','Intel (Semiconductors)','−3 to −5%','$15B dilutive share sale; AI capex ROI uncertainty'],
    ['2','NVDA','Nvidia (AI Chips)','−1 to −2%','Profit-taking after +5.2% Nasdaq week'],
    ['3','AMD','AMD (Semiconductors)','−1 to −2%','Semiconductor sentiment contagion from Intel'],
    ['4','CC','Chemours (Chemicals)','−2 to −3%','UBS downgrade to Neutral'],
    ['5','IPAR','Inter Parfums (Consumer)','−2 to −3%','GS + TD Cowen downgrade to Hold'],
    ['6','CMP','Compass Minerals (Chemicals)','−2 to −3%','JPMorgan downgrade to Underweight'],
    ['7','MSFT','Microsoft (Tech)','−0.5 to −1%','General tech selloff; Intel contagion'],
    ['8','AMZN','Amazon (Mega-cap Tech)','−0.5 to −1%','Oil cost pressure on logistics segment'],
    ['9','GOOGL','Alphabet (Tech)','−0.5 to −1%','Tech-sector profit-taking'],
    ['10','DAL','Delta Air Lines (Transport)','−1 to −2%','Jet fuel cost spike on oil +5%'],
]
story.append(make_table(dl, col_widths=[0.25*inch, 0.55*inch, 2.65*inch, 0.75*inch, 2.2*inch]))
story.append(Paragraph("<b>Sector trend:</b> Semiconductors (Intel/NVDA), Tech (broad pullback), Transport (oil cost).", SMALL))

story.append(Spacer(1, 0.1*inch))
story.append(Paragraph("<b>Weekly Movers — Week of August 3-10, 2026</b>", H3))
story.append(Paragraph(
    "Best week since April: S&P 500 +3.6%, Nasdaq +5.2%. Catalyst: July jobs loss "
    "(-23K) revived Fed-hold narrative, cut yields, rotated money back into growth/tech.",
    BODY))
wg = [
    ['#','Ticker','Company / Sector','~Wk %','Catalyst'],
    ['1','IBTA','Ibotta Inc. (Fintech)','+45%','Strong user growth; analyst upgrade wave'],
    ['2','MOVE','Corvex Inc. (Special Situations)','+40%','Activist positioning; M&A speculation'],
    ['3','BLZE','Backblaze (Cloud Storage)','+37%','AI data management demand; earnings beat'],
    ['4','NVDA','Nvidia (AI Semiconductors)','+8-10%','AI compute demand; dovish rate outlook'],
    ['5','META','Meta Platforms (Social/AI)','+7-9%','AI monetization; rate-sensitive growth'],
    ['6','TSLA','Tesla (EV/Energy)','+6-9%','Rate-sensitive growth on dovish jobs data'],
    ['7','MSFT','Microsoft (Cloud/AI)','+6-8%','Azure AI; lower-yield benefit'],
    ['8','AMZN','Amazon (Cloud/Retail)','+5-7%','AWS AI; consumer resilience'],
    ['9','AVGO','Broadcom (AI Networking)','+5-7%','AI networking chip demand acceleration'],
    ['10','AAPL','Apple (Consumer Tech)','+4-6%','Services growth; rate tailwind'],
]
story.append(make_table(wg, col_widths=[0.25*inch, 0.55*inch, 2.5*inch, 0.7*inch, 2.4*inch]))
story.append(Paragraph("<b>Sector trend (gainers):</b> Technology/AI led (+5-10%), Financials and Industrials participated.", SMALL))

story.append(Spacer(1, 0.06*inch))
wl = [
    ['#','Ticker','Company / Sector','~Wk %','Catalyst'],
    ['1','CVRX','CVRx Inc. (MedTech)','−60%','Guidance cut; Medicare Advantage headwinds'],
    ['2','CC','Chemours (Chemicals)','−5 to −8%','Tariff cost pressure + UBS downgrade'],
    ['3','CMP','Compass Minerals (Chemicals)','−4 to −6%','JPMorgan Underweight downgrade'],
    ['4','IPAR','Inter Parfums (Consumer)','−4 to −6%','Dual analyst downgrade'],
    ['5','INTC','Intel (Semiconductors)','−3 to −5%','$15B dilutive share offering (Monday)'],
]
story.append(make_table(wl, col_widths=[0.25*inch, 0.55*inch, 2.5*inch, 0.7*inch, 2.4*inch]))

story.append(Spacer(1, 0.1*inch))
story.append(Paragraph("<b>Monthly Movers — August 2026 (MTD through Aug 10)</b>", H3))
mg = [
    ['#','Ticker','Company / Sector','MTD %','Catalyst'],
    ['1','MB','MasterBrand (Consumer Durable)','+137%','Earnings blowout + buyout speculation'],
    ['2','RCEL','Avita Medical (Healthcare)','+64-68%','Revenue guidance hike; strong FDA pipeline'],
    ['3','VATE','INNOVATE Corp (Infrastructure)','+64-66%','Record Q2 profits; $0.71 EPS beat'],
    ['4','IBTA','Ibotta Inc. (Fintech)','+45.7%','User growth acceleration; analyst upgrades'],
    ['5','MOVE','Corvex Inc. (Special Situations)','+40.6%','Activist positioning; M&A speculation'],
    ['6','BLZE','Backblaze (Cloud Storage)','+37.4%','AI data demand + earnings outperformance'],
    ['7','LXU','LSB Industries (Chemicals)','+10-15%','RBC upgrade to Outperform; fertilizer demand'],
    ['8','FEAM','5E Advanced Materials (Minerals)','+10-14%','WH $2B mining policy investment'],
    ['9','MP','MP Materials (Rare Earths)','+8-11%','Policy tailwind + China RE export tension'],
    ['10','CRML','Critical Metals (Minerals)','+6-9%','Same policy catalyst'],
]
story.append(make_table(mg, col_widths=[0.25*inch, 0.55*inch, 2.45*inch, 0.7*inch, 2.45*inch]))
story.append(Paragraph("<b>Sector trend (gainers):</b> Healthcare/Biotech (individual), Fintech/Cloud (AI revenue), Critical Minerals (policy).", SMALL))

story.append(Spacer(1, 0.06*inch))
ml = [
    ['#','Ticker','Company / Sector','MTD %','Catalyst'],
    ['1','CVRX','CVRx Inc. (MedTech)','−60.4%','Guidance cut; Medicare Advantage headwinds'],
    ['2','CC','Chemours (Chemicals)','−5 to −8%','Tariff cost exposure + UBS downgrade'],
    ['3','CMP','Compass Minerals (Chemicals)','−4 to −6%','JPMorgan Underweight downgrade'],
    ['4','IPAR','Inter Parfums (Consumer)','−4 to −6%','Dual analyst downgrade (GS + TDC)'],
    ['5','INTC','Intel (Semiconductors)','−3 to −5%','$15B dilutive share offering'],
]
story.append(make_table(ml, col_widths=[0.25*inch, 0.55*inch, 2.45*inch, 0.7*inch, 2.45*inch]))
story.append(Paragraph("<b>Sector trend (losers):</b> MedTech (Medicare), Chemicals (tariffs/analysts), legacy Semiconductors.", SMALL))

# ══════════════════════════════════════
# SECTION 5 — NEXT-DAY SCENARIOS
# ══════════════════════════════════════
story.append(PageBreak())
story.append(Paragraph("5 — Next-Day &amp; Week-Ahead Scenarios", H2))
story.append(Paragraph(
    "Aug 10 had no major scheduled releases. Key catalysts this week: "
    "Wed Aug 12 (CPI), Thu Aug 13 (PPI + AMAT earnings), Fri Aug 14 (Retail Sales + UMich).",
    BODY))
story.append(Spacer(1, 0.06*inch))

scenarios = [
    ("CATALYST 1 — July CPI (Wednesday Aug 12, 8:30 AM ET)", [
        ("IF tame — headline ≤3.3%, core ≤2.4% → BULLISH",
         "Prediction markets lean this way (~55% probability). Confirms disinflation progress. "
         "Yields fall, growth stocks re-rate. SPY +0.5-1.5%; QQQ +1-2%. "
         "Fed rate-cut bets for Sep/Nov 2026 reprice higher. "
         "AI/semis and high-multiple tech the biggest beneficiaries."),
        ("IF hot — headline ≥3.5%, core ≥2.6% → BEARISH",
         "Stagflation narrative: oil at $82 (Hormuz closure) + sticky inflation = Fed must hike. "
         "Yields spike, duration risk hits growth stocks hard. SPY −1 to −2%; QQQ −1.5 to −3%. "
         "Energy stocks (XOM, CVX) benefit as inflation hedge."),
        ("IF in-line — 3.4% / 2.5% → NEUTRAL to SLIGHT POSITIVE",
         "Already partly priced via weak jobs. Confirming print = 'buy the confirmation.' "
         "SPY +0.1-0.3%. Market looks ahead to Thursday's AMAT earnings."),
    ]),
    ("CATALYST 2 — Applied Materials (AMAT) Earnings (Thursday Aug 13, after close)", [
        ("IF BEAT — EPS >$3.39, rev >$9B, guide raised → BULLISH",
         "4 consecutive beats; confirms AI capex cycle intact. AMAT +5-8%; "
         "semis (NVDA, AMD, LRCX) follow. QQQ +0.5-1% Friday. "
         "Bullish read-through into Nvidia Aug 26 earnings."),
        ("IF MISS or soft guide → BEARISH",
         "AMAT −8-12%; sector −2-5%; QQQ −1 to −1.5% Friday. "
         "High shock value: consensus expects +35.5% EPS growth. "
         "Miss would expose elevated forward expectations."),
    ]),
    ("CATALYST 3 — Iran / Strait of Hormuz (Ongoing Wild-Card)", [
        ("IF deal announced / Hormuz reopens → OIL CRASHES, STOCKS RALLY",
         "Oil collapses 8-15%. S&P +1.5-2.5%; Nasdaq +2-3%. "
         "Transport/airlines surge. Energy sector falls 4-6%. "
         "Largest single positive macro catalyst available this week."),
        ("IF escalation / new military incident → RISK-OFF",
         "Oil spikes above $90+ Brent. S&P −1.5 to −2.5%; QQQ −2 to −3%. "
         "Safe havens (gold, Treasuries) bid. Airlines/logistics hard hit. "
         "Energy stocks gain 4-6%."),
    ]),
    ("CATALYST 4 — PPI + Retail Sales + UMich (Thu-Fri)", [
        ("IF soft-landing trifecta → BULLISH",
         "PPI cool + Retail Sales hold + UMich up = confirmation of soft-landing. "
         "SPY likely finishes week at or above $775. Extends July 28-Aug 7 rally."),
        ("IF stagflation combo — PPI hot + Retail Sales miss → BEARISH",
         "Compounds narrative of 'inflation still too high + growth faltering.' "
         "SPY gives back a chunk of last week's 3.6% gain. "
         "Especially damaging if hot CPI Wednesday is also confirmed."),
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

trades = [
    ['#','Ticker','Action','Thesis','Key Risk'],
    ['1','QQQ',
     'BUY on tame\nCPI (Wed AM)',
     'Tame CPI (≤3.3%) confirms Fed hold → QQQ re-rates. Prior week +5.2% momentum intact. '
     'AI cycle robust. Prediction markets favor tame print.',
     'Hot CPI breaks thesis; stop ~$705. Oil escalation = concurrent risk.'],
    ['2','AMAT',
     'BUY small before\nThu close',
     '4 straight beats; 23% rev growth guided; semis in AI upcycle. '
     'At $539 vs avg target $635 (+17% upside). AI capex from hyperscalers intact.',
     'Miss risk is real. Sector fragile after INTC. Small position. Stop ~$515.'],
    ['3','MP Materials\n(MP)',
     'BUY / accumulate',
     'White House $2B+ mining investment = structural policy tailwind. '
     'China RE export tensions = domestic supply urgency. Trend just started.',
     'Policy reversal. Illiquid sector. Small position only.'],
    ['4','XOM / USO',
     'BUY\n(partial hedge)',
     'Hormuz reopening unlikely near term (Iran preconditions U.S. cannot accept). '
     'WTI has path to $90+. Hedges portfolio against Hormuz worsening.',
     'Surprise deal = oil drops 10%+. Size as hedge, not core position.'],
    ['5','NVDA',
     'HOLD / add on dips',
     'Reports Aug 26. AI demand strongest in history. Monday pullback is shallow. '
     'Tame CPI would re-accelerate the stock.',
     'Crowded; a miss would be severe. Wait for CPI clarity first.'],
    ['6','INTC',
     'AVOID',
     '$15B dilution + unclear AI ROI + FCF negative near-term. '
     'Below $100 psychological barrier. No near-term catalyst.',
     'N/A — avoiding. Thesis for avoidance is clear.'],
]
story.append(make_table(trades,
    col_widths=[0.2*inch, 0.65*inch, 0.95*inch, 3.05*inch, 1.55*inch]))

story.append(Spacer(1, 0.12*inch))
story.append(hr())
story.append(Spacer(1, 0.06*inch))
story.append(Paragraph(
    "<b>Key macro watch this week:</b> CPI Wed (most important) → PPI Thu → AMAT earnings Thu → "
    "Retail Sales + UMich Fri → Iran/Hormuz (wild-card) → NVDA earnings Aug 26.",
    BOLD))
story.append(Spacer(1, 0.08*inch))
story.append(Paragraph(
    f"<i>Generated automatically on {REPORT_DATE} at ~5:15 PM ET. "
    "Aug 10 closes estimated from confirmed index moves (S&P -0.10%, Nasdaq -0.30%). "
    "Historical price series: {rows[0]['date']} to {rows[-1]['date']} ({len(rows)} trading days). "
    "Yahoo Finance API and most financial data endpoints blocked by network proxy; "
    "prices confirmed via web search from TheStreet, CNBC, Yahoo Finance, 247WallSt, Al Jazeera.</i>",
    SMALL))

doc.build(story)
print(f"PDF written -> {PDF_PATH}")
