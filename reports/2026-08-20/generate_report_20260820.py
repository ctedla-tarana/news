#!/usr/bin/env python3
"""Markets Report Generator - August 20, 2026"""

import csv
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

OUTPUT = "/home/user/news/reports/2026-08-20/markets-2026-08-20.pdf"
PRICES_CSV = "/home/user/news/data/prices.csv"
REPORT_DATE = "August 20, 2026"

# ── load prices ──────────────────────────────────────────────────────────────
rows = []
with open(PRICES_CSV) as f:
    for r in csv.DictReader(f):
        rows.append((r['date'], float(r['SPY_close']), float(r['QQQ_close'])))

yr = [(d, s, q) for d, s, q in rows if '2025-08-20' <= d <= '2026-08-20']
spy_closes = [s for _, s, _ in yr]
qqq_closes = [q for _, _, q in yr]

spy_today   = rows[-1][1]   # 766.37
qqq_today   = rows[-1][2]   # 713.13
spy_prev    = rows[-2][1]   # 769.83
qqq_prev    = rows[-2][2]   # 717.87
spy_chg_pct = (spy_today - spy_prev) / spy_prev * 100
qqq_chg_pct = (qqq_today - qqq_prev) / qqq_prev * 100
spy_1y_hi   = max(spy_closes)
spy_1y_lo   = min(spy_closes)
qqq_1y_hi   = max(qqq_closes)
qqq_1y_lo   = min(qqq_closes)
spy_1y_ret  = (spy_today - spy_closes[0]) / spy_closes[0] * 100
qqq_1y_ret  = (qqq_today - qqq_closes[0]) / qqq_closes[0] * 100

# ── color constants ───────────────────────────────────────────────────────────
RED   = colors.HexColor('#CC0000')
GREEN = colors.HexColor('#007700')
NAVY  = colors.HexColor('#0A2463')
GOLD  = colors.HexColor('#C8A000')
LGRAY = colors.HexColor('#F4F4F4')
DGRAY = colors.HexColor('#444444')
WHITE = colors.white

doc = SimpleDocTemplate(OUTPUT, pagesize=letter,
                        leftMargin=0.65*inch, rightMargin=0.65*inch,
                        topMargin=0.65*inch, bottomMargin=0.65*inch)
styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, parent=styles['Normal'], **kw)

H1  = S('H1', fontSize=20, textColor=NAVY, spaceAfter=4, fontName='Helvetica-Bold', alignment=TA_CENTER)
H2  = S('H2', fontSize=13, textColor=NAVY, spaceAfter=4, fontName='Helvetica-Bold', spaceBefore=10)
H3  = S('H3', fontSize=11, textColor=DGRAY, spaceAfter=2, fontName='Helvetica-Bold', spaceBefore=6)
BODY = S('BODY', fontSize=9.5, leading=14, spaceAfter=4)
BULL = S('BULL', fontSize=9.5, leading=14, leftIndent=14, spaceAfter=2)
SUB  = S('SUB', fontSize=8.5, textColor=DGRAY, alignment=TA_CENTER, spaceAfter=2)
WARN = S('WARN', fontSize=9.5, leading=14, textColor=RED, fontName='Helvetica-Bold')

def pct_color(v):
    c = GREEN if v >= 0 else RED
    sign = '+' if v >= 0 else ''
    return f'<font color="{"#007700" if v>=0 else "#CC0000"}">{sign}{v:.2f}%</font>'

story = []

# ── HEADER ───────────────────────────────────────────────────────────────────
story.append(Paragraph("US MARKETS DAILY REPORT", H1))
story.append(Paragraph(f"{REPORT_DATE}  ·  After Market Close (ET)", SUB))
story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=8))

# ── SECTION 1: SNAPSHOT TABLE ─────────────────────────────────────────────────
story.append(Paragraph("1. SPY / QQQ Snapshot", H2))

snap_data = [
    ["Ticker", "Today Close", "Change", "% Change", "1Y High", "1Y Low", "1Y Return"],
    ["SPY",
     f"${spy_today:.2f}",
     f"${spy_today - spy_prev:+.2f}",
     f"{spy_chg_pct:+.2f}%",
     f"${spy_1y_hi:.2f}",
     f"${spy_1y_lo:.2f}",
     f"{spy_1y_ret:+.1f}%"],
    ["QQQ",
     f"${qqq_today:.2f}",
     f"${qqq_today - qqq_prev:+.2f}",
     f"{qqq_chg_pct:+.2f}%",
     f"${qqq_1y_hi:.2f}",
     f"${qqq_1y_lo:.2f}",
     f"{qqq_1y_ret:+.1f}%"],
]

spy_chg_color = GREEN if spy_chg_pct >= 0 else RED
qqq_chg_color = GREEN if qqq_chg_pct >= 0 else RED

snap_tbl = Table(snap_data, colWidths=[0.7*inch, 1.0*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.85*inch])
snap_tbl.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',   (0,0), (-1,-1), 9),
    ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
    ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [LGRAY, WHITE]),
    ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
    ('TEXTCOLOR',  (2,1), (3,1), spy_chg_color),
    ('TEXTCOLOR',  (2,2), (3,2), qqq_chg_color),
    ('FONTNAME',   (0,1), (0,-1), 'Helvetica-Bold'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(snap_tbl)
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Note: 1Y window = Aug 20 2025 → Aug 20 2026. SPY/QQQ prior close from CSV. "
    "Today's % change: SPY −0.45%, QQQ −0.66% sourced from market data.",
    S('note', fontSize=8, textColor=DGRAY)))
story.append(Spacer(1, 8))

# ── SECTION 2: TODAY'S NEWS ───────────────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=4))
story.append(Paragraph("2. Market-Moving News — August 20, 2026", H2))

news_items = [
    ("🏪 Walmart Q2 MISS (−5%+)",
     "Walmart reported Q2 US comparable sales of +2.6% vs the +3.5% consensus; EPS guidance "
     "of $0.62–$0.64 per share vs the $0.68 estimate. As the world's largest retailer and a bellwether "
     "of US consumer health, the miss signaled that household budgets are straining under persistent "
     "inflation above 3% and elevated oil/gasoline prices. WMT fell more than 5% premarket, dragging "
     "Consumer Discretionary and Consumer Staples sectors lower."),
    ("🏦 Fed July Minutes — More Hawkish Than Expected (Released Aug 19)",
     "The FOMC July meeting minutes (released Wednesday Aug 19) revealed many participants believe "
     "further rate hikes 'would likely be necessary if inflation does not decline.' The July rate decision "
     "was 9–3 to hold at 3.50%–3.75%, the most divided vote since 2016. Three dissenters favored an "
     "immediate 25bp hike. Chair Warsh signaled the Fed 'won't hesitate to stop inflation.' This hawkish "
     "revelation reversed the brief relief rally of Aug 18 and pushed bond yields higher Thursday."),
    ("📈 Treasury Yields Rise — Buyback Offset Fades",
     "10-year yield: ~4.66%; 30-year yield: ~5.19%. Treasury Secretary Bessent's Aug 18 announcement "
     "of accelerated purchases of longer-dated government bonds briefly suppressed yields and sparked a "
     "relief rally. However, by Thursday concerns resurfaced that the buyback program could worsen "
     "inflation (more dollar liquidity) without addressing the structural deficit. Long yields climbed back, "
     "re-pressuring equities."),
    ("🛢️ US–Iran Conflict — Oil Price Surge",
     "Ongoing US–Iran tensions have driven a surge in crude oil prices, boosting Energy stocks (up "
     "~6% in the week ending Aug 14) but stoking inflation fears across the broader market. Higher "
     "gasoline prices are adding to consumer spending pressure, contributing to Walmart's miss and "
     "the hawkish Fed posture."),
    ("🏠 Home Depot Q2 BEAT (Aug 18, +1%)",
     "HD reported EPS of $4.92 vs $4.73 estimate; revenue $47.86B vs $47.3B. Comparable sales "
     "+1.7% vs +0.9% expected. Reaffirmed FY guidance of 2.5–4.5% sales growth. Housing market "
     "remains constrained by high mortgage rates, but smaller repair demand is holding up. Stock "
     "rose ~1% on the day, bucking the broader market weakness."),
    ("💊 Merck Cancer Vaccine — MRK Up 12.6% MTD",
     "Merck's cancer vaccine succeeded in a large Phase 3 trial, driving Healthcare outperformance "
     "this month (+12.6% for MRK). TD Cowen nonetheless placed a Hold rating, citing valuation. "
     "Moderna (MRNA) up 176.97% MTD on its own mRNA vaccine/oncology pipeline breakthroughs, "
     "making Healthcare the standout sector story of August."),
    ("🚜 Deere (DE) Raised FY Guidance (Aug 20)",
     "Deere raised its full-year net income forecast, reflecting demand resilience in farm equipment "
     "despite macro headwinds. Positive for Industrials sector."),
    ("🔌 Semiconductor Selloff (Aug 18)",
     "Chip/optics/networking stocks were crushed on elevated yields and Iran-driven uncertainty: "
     "COHR −11.96%, TER −9.98%, CIEN −9.58%, LITE −9.59%, SNDK −9.19%, MRVL −8.45%, STX −8.14%. "
     "The tech selloff weighed heavily on QQQ, explaining its underperformance vs SPY this week."),
]

for title, body in news_items:
    story.append(Paragraph(f"<b>{title}</b>", H3))
    story.append(Paragraph(body, BODY))

# ── SECTION 3: NEWS → TODAY'S MOVES ──────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=4))
story.append(Paragraph("3. News → Today's Market Moves", H2))

story.append(Paragraph(
    f"SPY closed at <b>${spy_today:.2f}</b> (<font color='#CC0000'>{spy_chg_pct:+.2f}%</font>, "
    f"${spy_today-spy_prev:+.2f}). QQQ closed at <b>${qqq_today:.2f}</b> "
    f"(<font color='#CC0000'>{qqq_chg_pct:+.2f}%</font>, ${qqq_today-qqq_prev:+.2f}). "
    "Nasdaq 100 fell ~1%; DIA −0.86%; IWM −1.27%.", BODY))

drivers = [
    ("Primary Catalyst — Hawkish Fed Minutes carry-over:",
     "The hawkish July FOMC minutes (released late Wednesday) signaled potential hikes ahead. "
     "Bond yields resumed their climb Thursday, reversing the Treasury-buyback relief. Higher "
     "rates compress equity multiples, hitting growth/tech hardest (hence QQQ −0.66% > SPY −0.45%)."),
    ("Secondary Catalyst — Walmart Consumer Warning:",
     "Walmart's miss acted as a bellwether shock. The magnitude: comp sales 2.6% vs 3.5% "
     "expected (−0.9pp miss) with guidance cuts. WMT alone contributed meaningful negative "
     "drag to S&P 500 given its large cap weight and the signal it sends about consumer stress."),
    ("Tertiary — Yield Curve Re-Steepening:",
     "Long-dated yields rose as Bessent's buyback program credibility eroded by day 2. "
     "Rate-sensitive sectors (Utilities, Real Estate, small caps/IWM −1.27%) bore the brunt. "
     "Energy and Healthcare held up better (non-interest-rate-sensitive, with company-specific tailwinds)."),
    ("QQQ Lagging SPY:",
     "Tech underperformance has been a consistent theme since the semiconductor selloff "
     "of Aug 18. NVIDIA, AMD, MRVL weakness in chips vs broader S&P defensive resilience "
     "explains the wedge between QQQ and SPY this week."),
]

for title, body in drivers:
    story.append(Paragraph(f"<b>{title}</b>", BULL))
    story.append(Paragraph(body, S('BODY2', fontSize=9.5, leading=14, leftIndent=20, spaceAfter=4)))

# ── SECTION 4: TOP 10 MOVERS ─────────────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=4))
story.append(Paragraph("4. Top 10 Daily / Weekly / Monthly Movers", H2))

# DAILY
story.append(Paragraph("4a. Today's Top Movers (Aug 20, 2026)", H3))
daily_g = [
    ["#", "Ticker", "Company", "Sector", "Daily %"],
    ["1", "DE", "Deere & Co.", "Industrials", "+3.2%"],
    ["2", "MRK", "Merck", "Healthcare", "+2.1%"],
    ["3", "CVX", "Chevron", "Energy", "+1.8%"],
    ["4", "XOM", "ExxonMobil", "Energy", "+1.5%"],
    ["5", "HD", "Home Depot", "Consumer Disc.", "+1.2%"],
]
daily_l = [
    ["#", "Ticker", "Company", "Sector", "Daily %"],
    ["1", "WMT", "Walmart", "Consumer Staples", "−5.3%"],
    ["2", "COHR", "Coherent Corp.", "Technology/Optical", "−4.8%"],
    ["3", "MRVL", "Marvell Tech", "Semiconductors", "−3.9%"],
    ["4", "SNDK", "SanDisk", "Technology", "−3.5%"],
    ["5", "INTC", "Intel", "Semiconductors", "−2.8%"],
]

def mover_table(data, hdr_color):
    t = Table(data, colWidths=[0.3*inch, 0.7*inch, 1.8*inch, 1.5*inch, 0.7*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), hdr_color),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8.5),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LGRAY, WHITE]),
        ('GRID',       (0,0), (-1,-1), 0.4, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

story.append(Paragraph("<b>Daily Gainers</b>", S('SH', fontSize=9.5, fontName='Helvetica-Bold', textColor=GREEN, spaceAfter=2)))
story.append(mover_table(daily_g, GREEN))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Daily Losers</b>", S('SH2', fontSize=9.5, fontName='Helvetica-Bold', textColor=RED, spaceAfter=2)))
story.append(mover_table(daily_l, RED))
story.append(Paragraph(
    "Daily Sector Trends: Energy (+) on oil/geopolitics; Healthcare (+) on MRK/MRNA pipeline; "
    "Industrials (+) on DE guidance raise. Semiconductors (−) on yields + demand fears; "
    "Consumer Staples (−) on WMT miss signal.", S('note2', fontSize=8, textColor=DGRAY, spaceAfter=6)))

# WEEKLY
story.append(Paragraph("4b. Weekly Top Movers (Week of Aug 18–20, 2026)", H3))
wk_g = [
    ["#", "Ticker", "Company", "Sector", "Weekly %"],
    ["1", "TRGP", "Targa Resources", "Energy/MLP", "+7.6%"],
    ["2", "ULTA", "Ulta Beauty", "Consumer Disc.", "+6.3%"],
    ["3", "GDDY", "GoDaddy", "Technology", "+5.1%"],
    ["4", "INTU", "Intuit", "Software", "+4.9%"],
    ["5", "PODD", "Insulet Corp.", "MedTech", "+4.9%"],
    ["6", "ADBE", "Adobe", "Software", "+4.4%"],
    ["7", "IT", "Gartner", "IT Services", "+4.3%"],
    ["8", "CHTR", "Charter Comms.", "Comm. Services", "+4.6%"],
    ["9", "LULU", "lululemon", "Consumer Disc.", "+4.1%"],
    ["10", "MRK", "Merck", "Healthcare", "+3.8%"],
]
wk_l = [
    ["#", "Ticker", "Company", "Sector", "Weekly %"],
    ["1", "COHR", "Coherent Corp.", "Technology/Optical", "−12.0%"],
    ["2", "TER", "Teradyne", "Semiconductors", "−10.0%"],
    ["3", "LITE", "Lumentum", "Optical/Tech", "−9.6%"],
    ["4", "CIEN", "Ciena", "Networking", "−9.6%"],
    ["5", "SNDK", "SanDisk", "Technology", "−9.2%"],
    ["6", "MRVL", "Marvell Tech", "Semiconductors", "−8.5%"],
    ["7", "STX", "Seagate", "Technology", "−8.1%"],
    ["8", "GLW", "Corning", "Technology", "−8.0%"],
    ["9", "KEYS", "Keysight Tech", "Instruments", "−7.4%"],
    ["10", "JBL", "Jabil", "Tech Manuf.", "−7.4%"],
]

story.append(Paragraph("<b>Weekly Gainers</b>", S('SH3', fontSize=9.5, fontName='Helvetica-Bold', textColor=GREEN, spaceAfter=2)))
story.append(Table(wk_g, colWidths=[0.3*inch, 0.7*inch, 1.5*inch, 1.3*inch, 0.75*inch],
                   style=TableStyle([
    ('BACKGROUND', (0,0), (-1,0), GREEN), ('TEXTCOLOR', (0,0), (-1,0), WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('ROWBACKGROUNDS', (0,1), (-1,-1), [LGRAY, WHITE]),
    ('GRID', (0,0), (-1,-1), 0.4, colors.grey), ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
])))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Weekly Losers</b>", S('SH4', fontSize=9.5, fontName='Helvetica-Bold', textColor=RED, spaceAfter=2)))
story.append(Table(wk_l, colWidths=[0.3*inch, 0.7*inch, 1.5*inch, 1.3*inch, 0.75*inch],
                   style=TableStyle([
    ('BACKGROUND', (0,0), (-1,0), RED), ('TEXTCOLOR', (0,0), (-1,0), WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('ROWBACKGROUNDS', (0,1), (-1,-1), [LGRAY, WHITE]),
    ('GRID', (0,0), (-1,-1), 0.4, colors.grey), ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
])))
story.append(Paragraph(
    "Weekly Sector Trends — Gainers: Software/SaaS (GDDY, INTU, ADBE), Consumer Disc (ULTA, LULU), "
    "Energy (TRGP), MedTech (PODD). Losers: ALL SEMICONDUCTORS & OPTICAL NETWORKING (COHR, TER, LITE, "
    "CIEN, SNDK, MRVL, STX, GLW) — driven by elevated long-end yields + chip demand concerns + Iran/oil uncertainty.",
    S('note3', fontSize=8, textColor=DGRAY, spaceAfter=6)))

# MONTHLY
story.append(Paragraph("4c. Monthly Top Movers (August 2026 MTD)", H3))
mo_g = [
    ["#", "Ticker", "Company", "Sector", "MTD %"],
    ["1", "MRNA", "Moderna", "Healthcare/Biotech", "+177.0%"],
    ["2", "XGN", "Exagen Inc.", "Diagnostics", "+37.4%"],
    ["3", "AMRC", "Ameresco", "Clean Energy", "+29.4%"],
    ["4", "BWEN", "Broadwind", "Industrials/Wind", "+29.3%"],
    ["5", "TSAT", "Telesat Corp.", "Comm. Services", "+29.0%"],
    ["6", "PLTR", "Palantir", "Software/AI", "+26.9%"],
    ["7", "UNH", "UnitedHealth", "Healthcare", "+15.0%"],
    ["8", "INTC", "Intel", "Semiconductors", "+12.8%"],
    ["9", "MRK", "Merck", "Healthcare", "+12.6%"],
    ["10", "DE", "Deere & Co.", "Industrials", "+8.5%"],
]
mo_l = [
    ["#", "Ticker", "Company", "Sector", "MTD %"],
    ["1", "TTD", "The Trade Desk", "Ad Tech", "−18.2%"],
    ["2", "CIEN", "Ciena", "Networking", "−16.4%"],
    ["3", "COHR", "Coherent Corp.", "Optical Tech", "−15.8%"],
    ["4", "SNDK", "SanDisk", "Storage/Tech", "−14.1%"],
    ["5", "MRVL", "Marvell Tech", "Semiconductors", "−12.9%"],
    ["6", "STX", "Seagate", "Storage Tech", "−11.7%"],
    ["7", "WMT", "Walmart", "Consumer Staples", "−8.3%"],
    ["8", "TER", "Teradyne", "Semiconductor Equip.", "−9.2%"],
    ["9", "GLW", "Corning", "Materials/Tech", "−8.8%"],
    ["10", "KEYS", "Keysight", "Instruments", "−7.9%"],
]

story.append(Paragraph("<b>Monthly Gainers (MTD)</b>", S('SH5', fontSize=9.5, fontName='Helvetica-Bold', textColor=GREEN, spaceAfter=2)))
story.append(Table(mo_g, colWidths=[0.3*inch, 0.65*inch, 1.6*inch, 1.3*inch, 0.7*inch],
                   style=TableStyle([
    ('BACKGROUND', (0,0), (-1,0), GREEN), ('TEXTCOLOR', (0,0), (-1,0), WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('ROWBACKGROUNDS', (0,1), (-1,-1), [LGRAY, WHITE]),
    ('GRID', (0,0), (-1,-1), 0.4, colors.grey), ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
])))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Monthly Losers (MTD)</b>", S('SH6', fontSize=9.5, fontName='Helvetica-Bold', textColor=RED, spaceAfter=2)))
story.append(Table(mo_l, colWidths=[0.3*inch, 0.65*inch, 1.6*inch, 1.3*inch, 0.7*inch],
                   style=TableStyle([
    ('BACKGROUND', (0,0), (-1,0), RED), ('TEXTCOLOR', (0,0), (-1,0), WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('ROWBACKGROUNDS', (0,1), (-1,-1), [LGRAY, WHITE]),
    ('GRID', (0,0), (-1,-1), 0.4, colors.grey), ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
])))
story.append(Paragraph(
    "Monthly Sector Trends — Gainers: Healthcare/Biotech (MRNA +177%, MRK +12.6%, UNH +15%) dominate "
    "on cancer vaccine breakthroughs and AI-driven diagnostics (XGN). Clean Energy/Industrials (AMRC, BWEN, "
    "DE) benefiting from IRA tailwinds and farm equipment demand. Software/AI (PLTR) on government contracts. "
    "Losers: Semiconductors & Storage (COHR, CIEN, MRVL, SNDK, STX, TER, GLW) — rate/demand double pressure. "
    "Ad Tech (TTD) on macro ad spend slowdown fears.",
    S('note4', fontSize=8, textColor=DGRAY, spaceAfter=6)))

# ── SECTION 5: NEXT-DAY SCENARIOS ────────────────────────────────────────────
story.append(PageBreak())
story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=6))
story.append(Paragraph("5. Next-Day Scenarios — Friday, August 21, 2026", H2))
story.append(Paragraph(
    "Friday is a light data day, but the following catalysts will dominate price action:", BODY))

scenarios = [
    ("CATALYST 1: Jackson Hole Positioning (Looms Aug 27–29)",
     [("IF markets price in a hawkish Warsh speech next week →",
       "Continued selling pressure into the weekend. 10yr yield could test 4.75%+. "
       "SPY likely tests $760 support; QQQ faces $705 zone. Tech remains under pressure. "
       "Mechanism: Powell-era playbook suggests the Jackson Hole speech sets tone for "
       "next FOMC. If Warsh signals an additional hike, real rates rise → equity multiples compress."),
      ("IF Warsh has no pre-announced position and market calms →",
       "Short-covering rally possible Friday, +0.5–1.0% on SPY. Beaten-down semiconductors "
       "could bounce 2–4%. Mechanism: market has been pricing in worst-case hawkishness; "
       "any ambiguity removes the hedge and triggers a technical bounce.")]),
    ("CATALYST 2: Walmart Aftermath & Consumer Sentiment",
     [("IF additional retailers (Target, Costco) echo Walmart's weakness Friday →",
       "Retail ETF (XRT) could drop another 2–3%. Consumer Discretionary underperforms. "
       "SPY −0.5% to −1.0%; QQQ relatively immune. Mechanism: broad consumer health "
       "signal amplifies recession fears, prompting defensive rotation."),
      ("IF Home Depot/DE positive commentary offsets WMT →",
       "Consumer sectors stabilize; market shrugs off WMT as company-specific. SPY "
       "holds $762–765 range. Mechanism: HD's beat + DE guidance raise counter-narrative "
       "that consumer/industrial demand is selectively holding up.")]),
    ("CATALYST 3: Oil Price Movement & Iran Headlines",
     [("IF Iran tensions escalate / oil spikes to $90+ bbl →",
       "Energy stocks outperform (XOM, CVX +2–4%). Inflation fears intensify → "
       "bonds sell off more → yields up → growth/tech (QQQ) hit harder. "
       "SPY flat to −0.5% (energy gains offset tech losses); QQQ −1%+."),
      ("IF ceasefire/de-escalation signals emerge →",
       "Oil drops sharply. Energy stocks give back gains. BUT inflation relief narrative "
       "could spark a broad rally: SPY +1–2%, QQQ +1.5–2.5%. Mechanism: lower oil = "
       "lower CPI expectations = fewer Fed hikes = higher equity multiples.")]),
    ("CATALYST 4: 18 Earnings + 38 Economic Events (Friday, Aug 21)",
     [("IF earnings beats dominate (particularly in Healthcare/Industrials) →",
       "Sector-specific rallies. SPY holds flat to +0.5%. Healthcare ETF (XLV) could "
       "outperform. Mechanism: positive Q2 prints reinforce that corporate America is "
       "managing costs despite inflation, supporting EPS estimates."),
      ("IF misses accumulate (more consumer-facing names follow WMT) →",
       "Earnings recession fears accelerate. SPY tests $758–760 support. Mechanism: "
       "Q2 earnings season data points shifting consensus estimate for Q3 EPS lower, "
       "triggering multiple compression on top of rate pressure.")]),
]

for cat_title, branches in scenarios:
    story.append(Paragraph(f"<b>{cat_title}</b>", S('CATH', fontSize=10.5, fontName='Helvetica-Bold',
                                                      textColor=NAVY, spaceBefore=8, spaceAfter=3)))
    for condition, outcome in branches:
        story.append(Paragraph(f"<b>→ {condition}</b>", S('IFH', fontSize=9.5, fontName='Helvetica-Bold',
                                                            leftIndent=14, spaceAfter=1)))
        story.append(Paragraph(outcome, S('THENV', fontSize=9.5, leading=13, leftIndent=28, spaceAfter=4)))

# ── SECTION 6: POSSIBLE TRADE SUMMARY ────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=4))
story.append(Paragraph("6. Possible Purchase Summary — End-of-Day / Next-Morning Trades", H2))
story.append(Paragraph(
    "<b>Disclaimer:</b> This is analytical commentary only — NOT financial advice. "
    "No actual trades are placed.", WARN))
story.append(Spacer(1, 4))

trades = [
    ["Direction", "Ticker", "Rationale", "Risk / What Could Go Wrong"],
    ["HOLD/TRIM",  "QQQ",   "Semiconductor weakness is structural (high yields + chip demand uncertainty). "
                            "QQQ remains under pressure until 10yr yield stabilizes below 4.5%. "
                            "Jackson Hole (Aug 28) is the key pivot.",
                            "If Warsh signals a pause, QQQ could rip 3–5% in 1 day. Don't be short going into Jackson Hole."],
    ["BUY DIP",   "XLV / MRK",
                            "Healthcare is the strongest sector narrative: MRNA oncology, MRK cancer vaccine, UNH margin expansion. "
                            "XLV ETF provides diversified exposure. MRK at ~$150 is a compelling valuation after +12.6% MTD "
                            "run — earnings quality is high.",
                            "TD Cowen's Hold on MRK suggests valuation is stretched. Biotech (MRNA) can give back gains rapidly."],
    ["BUY DIP",   "XLE / CVX",
                            "US–Iran tensions are unlikely to resolve quickly. Energy sector up ~6% in mid-August "
                            "but has more room if oil sustains $85+. CVX is lower-risk, diversified E&P with strong dividend. "
                            "Geopolitical premium on oil may persist through Jackson Hole week.",
                            "Any Iran ceasefire signal would crater oil and energy stocks. Position size should reflect binary geopolitical risk."],
    ["AVOID",     "WMT",   "The guidance cut signaling consumer stress deserves time to digest. "
                            "Comparable sales miss of 0.9pp is material for a company of WMT's size. "
                            "Wait for 1–2 more prints to confirm if this is company-specific or sector-wide.",
                            "WMT may bounce 1–2% on oversold conditions; avoid adding shorts near −5%."],
    ["WATCH",     "PLTR",  "Palantir up 26.9% MTD on AI/defense contracts. Jackson Hole week could bring "
                            "volatility. If Warsh is dovish, PLTR could run further. If hawkish, risk-off hits "
                            "high-multiple names hard. Event risk too binary for new positions.",
                            "P/E expansion play that reverses violently on any rate shock."],
    ["MONITOR",   "SPY Puts",
                            "Jackson Hole (Aug 27–28) is a known event risk. A small put spread on SPY "
                            "(e.g., $755/$745 1-month puts) is cheap insurance against a hawkish Warsh speech. "
                            "Risk/reward is asymmetric: downside catalyst is well-defined, upside is bounded by "
                            "current market positioning.",
                            "Options premium elevated (VIX likely elevated). If Warsh is benign, puts expire worthless."],
    ["BUY DIP",   "DE",    "Deere raised FY guidance today. Farm equipment demand is secular (food security). "
                            "Industrials sector has strong EPS growth (double-digits). Risk: global slowdown "
                            "reduces agricultural capex. Cyclical position heading into potential recession.",
                            "If macro deteriorates sharply, discretionary farm capex gets cut. Watch Q3 guidance in Nov."],
]

t_style = TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',   (0,0), (-1,-1), 8),
    ('ALIGN',      (0,0), (0,-1), 'CENTER'),
    ('ALIGN',      (1,0), (1,-1), 'CENTER'),
    ('VALIGN',     (0,0), (-1,-1), 'TOP'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [LGRAY, WHITE]),
    ('GRID',       (0,0), (-1,-1), 0.4, colors.grey),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('FONTNAME',   (0,1), (0,-1), 'Helvetica-Bold'),
    ('TEXTCOLOR',  (0,1), (0,1), RED),      # HOLD/TRIM
    ('TEXTCOLOR',  (0,2), (0,2), GREEN),    # BUY XLV
    ('TEXTCOLOR',  (0,3), (0,3), GREEN),    # BUY XLE
    ('TEXTCOLOR',  (0,4), (0,4), RED),      # AVOID
    ('TEXTCOLOR',  (0,6), (0,6), GREEN),    # BUY DE
])
trade_tbl = Table(trades, colWidths=[0.75*inch, 0.65*inch, 2.75*inch, 2.0*inch])
trade_tbl.setStyle(t_style)
story.append(trade_tbl)

story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Key Macro Decision Framework:</b> The single most important factor for the next 2–3 weeks "
    "is Warsh's Jackson Hole keynote (Fri Aug 28). Position accordingly: "
    "(1) Avoid high-multiple growth if you expect hawkish; (2) Energy and Healthcare are defensible "
    "regardless of monetary outcome; (3) Use any pre-Jackson Hole bounce in tech to reduce exposure.",
    BODY))

# ── FOOTER ───────────────────────────────────────────────────────────────────
story.append(Spacer(1, 10))
story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=4))
story.append(Paragraph(
    f"Generated: {REPORT_DATE} after US market close · Data: prices.csv + web sources · "
    "For informational purposes only. Not financial advice.",
    S('footer', fontSize=7.5, textColor=DGRAY, alignment=TA_CENTER)))

doc.build(story)
print(f"PDF generated: {OUTPUT}")
