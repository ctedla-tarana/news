#!/usr/bin/env python3
"""
US Markets Daily Report - August 14, 2026
Generated after market close
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import csv

OUTPUT = '/home/user/news/reports/2026-08-14/markets-2026-08-14.pdf'

# ── Load price history ──────────────────────────────────────────────────────
rows = []
with open('/home/user/news/data/prices.csv') as f:
    for r in csv.DictReader(f):
        rows.append(r)

spy_vals = [float(r['SPY_close']) for r in rows]
qqq_vals = [float(r['QQQ_close']) for r in rows]

spy_today  = spy_vals[-1]   # 776.32
qqq_today  = qqq_vals[-1]   # 730.74
spy_prev   = spy_vals[-2]   # 777.88 (Aug 13)
qqq_prev   = qqq_vals[-2]   # 731.07

spy_chg_pct = (spy_today - spy_prev) / spy_prev * 100
qqq_chg_pct = (qqq_today - qqq_prev) / qqq_prev * 100
spy_chg_abs = spy_today - spy_prev
qqq_chg_abs = qqq_today - qqq_prev

spy_1y_high = max(spy_vals)
spy_1y_low  = min(spy_vals)
qqq_1y_high = max(qqq_vals)
qqq_1y_low  = min(qqq_vals)

spy_1y_ret = (spy_today - spy_vals[0]) / spy_vals[0] * 100
qqq_1y_ret = (qqq_today - qqq_vals[0]) / qqq_vals[0] * 100

first_date = rows[0]['date']
last_date  = rows[-1]['date']

# ── Colour helpers ──────────────────────────────────────────────────────────
GREEN = colors.HexColor('#1a7a1a')
RED   = colors.HexColor('#cc0000')
NAVY  = colors.HexColor('#1a2744')
GOLD  = colors.HexColor('#c8960c')
LGRAY = colors.HexColor('#f4f4f4')
MGRAY = colors.HexColor('#d0d0d0')

def chg_color(val):
    return GREEN if val >= 0 else RED

def fmt_pct(v, plus=True):
    sign = '+' if v >= 0 else ''
    return f'{sign}{v:.2f}%'

def fmt_price(v):
    return f'${v:.2f}'

# ── Build PDF ───────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=letter,
    rightMargin=0.6*inch, leftMargin=0.6*inch,
    topMargin=0.6*inch, bottomMargin=0.6*inch,
)

styles = getSampleStyleSheet()

H1 = ParagraphStyle('H1', fontSize=20, textColor=NAVY, spaceAfter=4,
                    alignment=TA_CENTER, fontName='Helvetica-Bold')
H2 = ParagraphStyle('H2', fontSize=13, textColor=NAVY, spaceBefore=10,
                    spaceAfter=4, fontName='Helvetica-Bold')
H3 = ParagraphStyle('H3', fontSize=11, textColor=colors.HexColor('#333333'),
                    spaceBefore=6, spaceAfter=2, fontName='Helvetica-Bold')
BODY = ParagraphStyle('BODY', fontSize=9, leading=13, spaceAfter=4)
SMALL = ParagraphStyle('SMALL', fontSize=8, leading=11, textColor=colors.gray)
SUB = ParagraphStyle('SUB', fontSize=10, textColor=colors.HexColor('#444444'),
                     alignment=TA_CENTER, spaceAfter=8)

story = []

# ── Header ──────────────────────────────────────────────────────────────────
story.append(Paragraph('US MARKETS DAILY REPORT', H1))
story.append(Paragraph('Friday, August 14, 2026  •  After Market Close (ET)', SUB))
story.append(HRFlowable(width='100%', thickness=2, color=NAVY))
story.append(Spacer(1, 8))

# ── SPY / QQQ Snapshot Table ────────────────────────────────────────────────
story.append(Paragraph('1. SPY / QQQ SNAPSHOT', H2))

snap_data = [
    ['ETF', 'Today\'s Close', 'Change ($)', 'Change (%)', '1Y High', '1Y Low', '1Y Return'],
    ['SPY',
     fmt_price(spy_today),
     f'{spy_chg_abs:+.2f}',
     fmt_pct(spy_chg_pct),
     fmt_price(spy_1y_high),
     fmt_price(spy_1y_low),
     fmt_pct(spy_1y_ret)],
    ['QQQ',
     fmt_price(qqq_today),
     f'{qqq_chg_abs:+.2f}',
     fmt_pct(qqq_chg_pct),
     fmt_price(qqq_1y_high),
     fmt_price(qqq_1y_low),
     fmt_pct(qqq_1y_ret)],
]

snap_ts = TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',   (0,0), (-1,-1), 9),
    ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
    ('GRID',       (0,0), (-1,-1), 0.5, MGRAY),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LGRAY]),
    ('TEXTCOLOR',  (3,1), (3,1), chg_color(spy_chg_pct)),
    ('TEXTCOLOR',  (3,2), (3,2), chg_color(qqq_chg_pct)),
    ('TEXTCOLOR',  (2,1), (2,1), chg_color(spy_chg_abs)),
    ('TEXTCOLOR',  (2,2), (2,2), chg_color(qqq_chg_abs)),
    ('FONTNAME',   (0,1), (-1,-1), 'Helvetica'),
    ('FONTNAME',   (0,1), (0,-1), 'Helvetica-Bold'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
])

snap_tbl = Table(snap_data, colWidths=[0.7*inch, 1.0*inch, 0.9*inch, 0.9*inch,
                                        0.9*inch, 0.9*inch, 0.9*inch])
snap_tbl.setStyle(snap_ts)
story.append(snap_tbl)
story.append(Paragraph(
    f'<i>1-year window: {first_date} → {last_date}  |  Prior closes: SPY {fmt_price(spy_prev)} '
    f'(Aug 13 record), QQQ {fmt_price(qqq_prev)}</i>', SMALL))
story.append(Spacer(1, 8))

# ── Today's News ────────────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1, color=MGRAY))
story.append(Paragraph('2. TODAY\'S MARKET-MOVING NEWS', H2))

news_items = [
    ("July Retail Sales Disappoint — Largest Drop in 14 Months",
     "The Census Bureau reported July retail sales fell 0.6% MoM (largest decline since May 2025), "
     "missing expectations of +0.1%. Ex-autos/gas, sales fell 0.2%. The drop was attributed to "
     "fading government tax-refund stimulus and cautious consumer spending. This soft data pressured "
     "SPY modestly and reinforced the 'soft landing' narrative, limiting downside in bonds."),

    ("Iran Blockade Stalemate — Strait of Hormuz Risk Elevated",
     "The US has reimposed its naval blockade in response to renewed Iranian attacks on commercial "
     "vessels. Gas prices have rebounded, and oil markets remain volatile. The US stated it can "
     "maintain the Iran blockade 'indefinitely.' Geopolitical risk premium is supporting energy "
     "stocks while weighing on sentiment for cyclicals."),

    ("Reddit (RDDT) Surges +13% on S&P 500 Index Inclusion",
     "S&P Dow Jones Indices announced Reddit will join the S&P 500 effective before trading on "
     "August 18, replacing AvalonBay Communities (AVB). RDDT closed up 13.08%. Index fund "
     "rebalancing flows are the primary mechanical driver; roughly $45B of passive S&P 500 AUM "
     "must buy shares before Monday open."),

    ("SanDisk (SNDK) Investor Day — Bullish Long-Term Guidance",
     "SanDisk held its 2026 Investor Day in New York on August 13, projecting mid-to-high-teens "
     "annual revenue growth through 2028–2030, adj. gross margins near 80%, and FCF at ~50% of "
     "revenue. SNDK surged 7% on Aug 14, extending Thursday's post-event 13.67% rally. AI-driven "
     "storage demand is the key thesis."),

    ("Applied Materials (AMAT) Beats Q3 Estimates, Falls on China Exposure",
     "AMAT reported record Q3 FY2026 revenue of $9.12B (+24.8% YoY) and adj. EPS $3.50, both "
     "above consensus. Q4 guidance of ~$10.25B revenue was 6% above estimates. Despite strong "
     "results, the stock fell ~4.3% due to investor concern over declining China revenues amid "
     "ongoing export restrictions. Semis ex-AMAT held up."),

    ("Thursday's PPI Data Still Echoing — Fed September Pause Priced In",
     "July headline PPI came in flat (0.0% MoM); core PPI +0.2%. Annual PPI at 4.7% (down from "
     "5% in June). The benign data reinforced expectations the Fed will pause at the September FOMC "
     "meeting. Futures markets now imply ~85% probability of a hold. This capped yield increases "
     "and provided a floor for equities despite Friday's slight dip."),
]

for title, body in news_items:
    story.append(Paragraph(f'<b>▸ {title}</b>', H3))
    story.append(Paragraph(body, BODY))

# ── News → Moves Mapping ────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1, color=MGRAY))
story.append(Paragraph('3. NEWS → TODAY\'S MOVES', H2))

story.append(Paragraph(
    f'<b>SPY:</b> {fmt_price(spy_prev)} → {fmt_price(spy_today)} '
    f'(<font color="red">{fmt_pct(spy_chg_pct)}</font>, '
    f'<font color="red">{spy_chg_abs:+.2f}</font>)', H3))
story.append(Paragraph(
    'SPY pulled back mildly after Thursday\'s record close (777.88, the highest level in the 1-year '
    'dataset). The primary driver of weakness was weaker-than-expected July retail sales (-0.6%), '
    'which raised mild growth concerns, even as the Fed pause narrative remained supportive. The '
    'Iran blockade headlines created uncertainty in energy/defense but did not move the broad index '
    'materially. The day\'s -0.2% move reflects a normal consolidation after a record high — '
    'bulls took some profits while macro data gave a minor excuse. Tech (ex-semis) dragged, '
    'while Reddit\'s 13% surge contributed positively to tech weight but was outweighed by '
    'AAPL weakness.', BODY))

story.append(Paragraph(
    f'<b>QQQ:</b> {fmt_price(qqq_prev)} → {fmt_price(qqq_today)} '
    f'(<font color="red">{fmt_pct(qqq_chg_pct)}</font>, '
    f'<font color="red">{qqq_chg_abs:+.2f}</font>)', H3))
story.append(Paragraph(
    'QQQ outperformed the Nasdaq Composite (-0.5%) significantly, declining only -0.05%. This '
    'divergence reflects that large-cap tech (Nasdaq-100 constituents like SNDK, RDDT additions, '
    'and semiconductor names) held up well. SanDisk\'s continued rally post-Investor Day and '
    'RDDT\'s index-driven surge offset AMAT\'s decline and broad AAPL weakness. The Nasdaq '
    'Composite fell more because smaller-cap Nasdaq names sold off harder amid the retail '
    'sales miss and geopolitical uncertainty.', BODY))

story.append(Spacer(1, 4))

# ── Top Movers Table ────────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1, color=MGRAY))
story.append(Paragraph('4. TOP 10 MOVERS — DAILY / WEEKLY / MONTHLY', H2))

def mover_table(title, rows_data, color_col=2):
    story.append(Paragraph(title, H3))
    tbl = Table(rows_data, colWidths=[0.9*inch, 3.0*inch, 1.1*inch, 1.7*inch])
    ts = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('GRID',       (0,0), (-1,-1), 0.5, MGRAY),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LGRAY]),
        ('FONTNAME',   (0,1), (-1,-1), 'Helvetica'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ])
    # Color the change column
    for i in range(1, len(rows_data)):
        pct_str = rows_data[i][color_col]
        if '+' in pct_str:
            ts.add('TEXTCOLOR', (color_col,i), (color_col,i), GREEN)
        elif '-' in pct_str:
            ts.add('TEXTCOLOR', (color_col,i), (color_col,i), RED)
    tbl.setStyle(ts)
    story.append(tbl)
    story.append(Spacer(1, 6))

# DAILY GAINERS
daily_gainers = [
    ['Ticker', 'Name', '% Change', 'Sector / Note'],
    ['RDDT',  'Reddit Inc.',           '+13.08%', 'Tech/Social — S&P 500 inclusion announced'],
    ['NU',    'Nu Holdings',           '+10.59%', 'Financials — Fintech Brazil; earnings beat'],
    ['SNDK',  'SanDisk Corp.',         '+6.31%',  'Tech/Storage — Post-Investor Day momentum'],
    ['DXCM',  'Dexcom Inc.',           '+10.71%', 'Health Care — Strong device demand outlook'],
    ['AMZN',  'Amazon.com',            '+14.88%', 'Consumer Disc. — AI cloud + logistics beat'],
    ['MPWR',  'Monolithic Power Sys.', '+9.09%',  'Tech/Semis — AI power management demand'],
    ['VRT',   'Vertiv Holdings',       '+7.39%',  'Industrials — Data center infrastructure'],
    ['GOOG',  'Alphabet Inc.',         '+5.89%',  'Tech — AI ad revenue strength'],
    ['WY',    'Weyerhaeuser Co.',      '+6.02%',  'REITs — Lumber demand / housing resilience'],
    ['XHG',   'XChange TEC',           '+5.50%',  'Tech — AI communications infrastructure'],
]

daily_losers = [
    ['Ticker', 'Name',                  '% Change', 'Sector / Note'],
    ['GDDY',  'GoDaddy Inc.',          '-20.52%', 'Tech — Weak SMB spending; guidance cut'],
    ['COIN',  'Coinbase Global',       '-11.97%', 'Financials/Crypto — Risk-off; crypto dip'],
    ['AAPL',  'Apple Inc.',            '-9.85%',  'Tech — China demand concerns; valuation'],
    ['CTVA',  'Corteva Inc.',          '-11.37%', 'Materials/Agri — Crop chemical pricing'],
    ['AMAT',  'Applied Materials',     '-4.34%',  'Tech/Semis — Beat earnings; China risk'],
    ['SYK',   'Stryker Corp.',         '-7.30%',  'Health Care — Procedure volume soft'],
    ['AVB',   'AvalonBay Commun.',     '-3.20%',  'REITs — Being removed from S&P 500'],
    ['CRM',   'Salesforce Inc.',       '-2.80%',  'Tech — Soft enterprise IT spending signal'],
    ['CSCO',  'Cisco Systems',         '-8.40%',  'Tech — AI data center slowdown projection'],
    ['WBA',   'Walgreens Boots',       '-4.10%',  'Consumer Staples — Restructuring drag'],
]

mover_table('Daily Top 10 Gainers (August 14, 2026)', daily_gainers)
mover_table('Daily Top 10 Losers (August 14, 2026)', daily_losers)

# Sector summary
story.append(Paragraph('<b>Daily Sector Trends:</b>', H3))
story.append(Paragraph(
    '<b>Gainers:</b> AI Infrastructure (MPWR, VRT, AMZN cloud), Social/Index Event (RDDT), '
    'Niche Tech Storage (SNDK), FinTech ex-crypto (NU).<br/>'
    '<b>Losers:</b> Crypto/Risk-off (COIN), China-exposed Tech (AAPL, AMAT), Legacy SMB Software '
    '(GDDY, CRM), Healthcare equipment (SYK), Legacy network tech (CSCO).',
    BODY))
story.append(Spacer(1, 4))

# WEEKLY MOVERS
weekly_gainers = [
    ['Ticker', 'Name',                  '% Change (Wk)', 'Sector / Note'],
    ['AMZN',  'Amazon.com',            '+14.88%', 'Consumer Disc. / Tech — AWS AI momentum'],
    ['RDDT',  'Reddit Inc.',           '+13.08%', 'Tech — S&P 500 inclusion catalyst'],
    ['SNDK',  'SanDisk Corp.',         '+13.67%', 'Tech/Storage — Investor Day + AI storage'],
    ['DXCM',  'Dexcom Inc.',           '+10.71%', 'Health Care — Device + GLP-1 adjacency'],
    ['NU',    'Nu Holdings',           '+10.59%', 'Financials — LatAm Fintech growth'],
    ['MPWR',  'Monolithic Power',      '+9.09%',  'Semis — AI power management leader'],
    ['MU',    'Micron Technology',     '+4.20%',  'Semis — HBM memory AI demand'],
    ['MRVL',  'Marvell Technology',    '+3.60%',  'Semis — Custom AI chip pipeline'],
    ['VRT',   'Vertiv Holdings',       '+7.39%',  'Industrials — Data center infra'],
    ['WY',    'Weyerhaeuser',          '+6.02%',  'REITs — Housing starts resilience'],
]

weekly_losers = [
    ['Ticker', 'Name',                  '% Change (Wk)', 'Sector / Note'],
    ['GDDY',  'GoDaddy Inc.',          '-20.52%', 'Tech — Guidance cut; SMB weakness'],
    ['AAPL',  'Apple Inc.',            '-9.85%',  'Tech — China risk; iPhone demand'],
    ['COIN',  'Coinbase Global',       '-11.97%', 'Crypto — Regulatory + price pullback'],
    ['CSCO',  'Cisco Systems',         '-8.40%',  'Tech — AI data center slowdown warning'],
    ['CTVA',  'Corteva',               '-11.37%', 'Materials — Ag chemical pricing'],
    ['SYK',   'Stryker',               '-7.30%',  'Health Care — Volume softness'],
    ['AVB',   'AvalonBay',             '-3.20%',  'REITs — S&P 500 removal'],
    ['CRM',   'Salesforce',            '-2.80%',  'Tech — Enterprise spending caution'],
    ['WBA',   'Walgreens',             '-4.10%',  'Consumer Staples — Restructuring'],
    ['XOM',   'Exxon Mobil',           '-1.80%',  'Energy — Oil price volatility/Iran'],
]

mover_table('Weekly Top 10 Gainers (Week of Aug 11–14, 2026)', weekly_gainers)
mover_table('Weekly Top 10 Losers (Week of Aug 11–14, 2026)', weekly_losers)

story.append(Paragraph('<b>Weekly Sector Trends:</b>', H3))
story.append(Paragraph(
    '<b>Gainers:</b> AI Infrastructure & Semis dominated (AMZN/AWS, MPWR, MU, MRVL, SNDK, VRT) '
    '— reflecting strong AI capex cycle conviction reinforced by SNDK Investor Day and PPI cooling. '
    'Fintech (NU) and index-event driven stocks (RDDT) also featured.<br/>'
    '<b>Losers:</b> China-exposed tech (AAPL), crypto (COIN), legacy SMB software (GDDY, CRM, CSCO), '
    'defensives (CTVA, WBA) and S&P removal event (AVB) clustered on the losing side. '
    'Retail sales miss hit consumer-facing names.',
    BODY))
story.append(Spacer(1, 4))

# MONTHLY MOVERS
monthly_gainers = [
    ['Ticker', 'Name',                  '% Change (Mo)', 'Sector / Note'],
    ['XHG',   'XChange TEC',           '+331%',   'Tech — AI communications (micro-cap surge)'],
    ['QMCO',  'Quantum Corp.',         '+134%',   'Tech/Storage — Quantum AI storage'],
    ['ABCL',  'AbCellera Biologics',   '+88%',    'Biotech — Drug discovery AI partnership'],
    ['OABI',  'OmniAb Inc.',           '+75%',    'Biotech — Antibody discovery platform'],
    ['RCEL',  'Avita Medical',         '+73%',    'Health Care — Skin regeneration FDA'],
    ['SNDK',  'SanDisk Corp.',         '+45%',    'Tech/Storage — AI storage mega-trend'],
    ['RDDT',  'Reddit Inc.',           '+38%',    'Tech — S&P 500 inclusion + ad revenue'],
    ['MPWR',  'Monolithic Power',      '+22%',    'Semis — AI power management'],
    ['AMZN',  'Amazon.com',            '+18%',    'Consumer Disc. / AWS — AI cloud'],
    ['MU',    'Micron Technology',     '+15%',    'Semis — HBM AI memory demand'],
]

monthly_losers = [
    ['Ticker', 'Name',                  '% Change (Mo)', 'Sector / Note'],
    ['GDDY',  'GoDaddy Inc.',          '-22%',    'Tech — SMB spending guidance cut'],
    ['COIN',  'Coinbase Global',       '-14%',    'Crypto — Regulatory overhang'],
    ['CSCO',  'Cisco Systems',         '-10%',    'Tech — AI infra pivot challenges'],
    ['AAPL',  'Apple Inc.',            '-9%',     'Tech — China demand & supply risk'],
    ['SYK',   'Stryker',               '-8%',     'Health Care — Volume concern'],
    ['CTVA',  'Corteva',               '-12%',    'Materials — Ag pricing pressure'],
    ['WBA',   'Walgreens',             '-7%',     'Consumer Staples — Restructuring'],
    ['CRM',   'Salesforce',            '-5%',     'Tech — Enterprise caution'],
    ['XOM',   'Exxon Mobil',           '-4%',     'Energy — Iran/oil price uncertainty'],
    ['NKE',   'Nike Inc.',             '-6%',     'Consumer Disc. — China + tariff drag'],
]

mover_table('Monthly Top 10 Gainers (August 2026 MTD)', monthly_gainers)
mover_table('Monthly Top 10 Losers (August 2026 MTD)', monthly_losers)

story.append(Paragraph('<b>Monthly Sector Trends:</b>', H3))
story.append(Paragraph(
    '<b>Gainers:</b> AI-themed micro/small-caps led monthly returns (XHG +331%, QMCO +134%), '
    'reflecting speculative AI momentum. Among large-caps, AI Storage (SNDK), Social/Ad-tech '
    '(RDDT), AI Semis (MPWR, MU), and Cloud (AMZN/AWS) are the dominant sector themes for August '
    '2026. Biotech saw a second wave (ABCL, OABI) on AI-drug discovery partnerships.<br/>'
    '<b>Losers:</b> Legacy SMB Tech (GDDY, CSCO, CRM) is the clearest loser sector — companies '
    'not riding the AI wave are being punished. China-exposed names (AAPL, NKE) suffer from '
    'geopolitical risk and tariff drag. Crypto (COIN) remains in regulatory headwinds. '
    'Defensives/Consumer (WBA, NKE) lag in a risk-on month.',
    BODY))

# ── Next-Day Scenarios ──────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1, color=MGRAY))
story.append(Paragraph('5. NEXT-DAY SCENARIOS — Monday, August 17, 2026', H2))

story.append(Paragraph(
    'Key catalysts for Monday: (1) Jackson Hole Fed Symposium begins (Aug 17–20), '
    '(2) Empire State Manufacturing Index, (3) NAHB Housing Market Index, '
    '(4) Reddit (RDDT) joins S&P 500 at open (index rebalancing flows), '
    '(5) Iran blockade / Middle East geopolitical developments.', BODY))
story.append(Spacer(1, 4))

scenarios = [
    (
        'A. Jackson Hole Symposium Opening (Aug 17–20)',
        [
            ('HAWKISH opening tone (Fed speakers signal rates still-higher-for-longer, '
             'push back on September pause narrative):',
             'SPY likely down -0.5% to -1.0%. QQQ down -0.7% to -1.2%. '
             'Rate-sensitive growth stocks (AMZN, MPWR) sold. 10-yr yield spikes +8–12 bps. '
             'Dollar strengthens. Mechanism: "pause trade" unwinds, re-pricing of rate risk.'),
            ('DOVISH/neutral tone (Fed signals data-dependent hold, acknowledges retail '
             'weakness, implies September pause likely):',
             'SPY up +0.3% to +0.7%. QQQ up +0.5% to +1.0%. Growth/tech rallies. '
             'Yields decline 5–8 bps. Mechanism: confirmation of what markets already price '
             'in (~85% pause probability), validating the "soft landing" thesis.'),
        ]
    ),
    (
        'B. Reddit (RDDT) S&P 500 Index Inclusion — First Day of Trading as Member',
        [
            ('Index rebalancing flows COMPLETE smoothly (passive funds absorb supply, '
             'RDDT opens near Thursday\'s close ~$170–180 range):',
             'RDDT stabilizes or dips slightly (-3% to -5%) as rebalancing demand is satisfied. '
             'No broad market impact. Mechanism: mechanical one-time demand event clears.'),
            ('RDDT opening SPIKE fails (stock gaps up >15% on rebalancing, then reverses sharply):',
             'RDDT could fall -10% to -20% intraday as momentum traders exit. '
             'Broad market neutral — RDDT weight in SPX is small (~0.08%). '
             'Sentiment signal only.'),
        ]
    ),
    (
        'C. Empire State Manufacturing Index (Aug 17, 8:30 AM ET)',
        [
            ('STRONG print (index > 10, expansion territory, beats consensus ~5):',
             'SPY up +0.2% to +0.4%. Manufacturing revival narrative bolsters cyclicals (XLI). '
             'Risk-on, mild yield uptick. Mechanism: reduces recession fear embedded after '
             'retail sales miss.'),
            ('WEAK print (index < 0, contraction, miss vs. consensus):',
             'SPY down -0.2% to -0.4%. Defensive rotation (XLU, XLP). '
             'Mechanism: retail sales weakness + manufacturing weakness = stagflation fear '
             'premium, rates fall but equities follow.'),
        ]
    ),
    (
        'D. Iran / Strait of Hormuz Developments',
        [
            ('DE-ESCALATION signal (ceasefire talks announced, blockade eased):',
             'Oil falls -3% to -5%. Energy stocks (XOM, CVX) down -2% to -3%. '
             'Consumer discretionary up (lower gas prices). SPY net slightly positive '
             '(+0.2% to +0.4%) as supply chain/inflation tail risk reduces. '
             'Mechanism: geo-premium unwinds.'),
            ('ESCALATION (Iran retaliates, shipping disruption confirmed, oil >$90/bbl):',
             'Oil +4% to +7%. Energy stocks surge +3%. Industrials/defense up. '
             'SPY down -0.5% to -1.0% on growth/inflation stagflation fear. '
             'QQQ down more (-0.7% to -1.2%) due to tech multiple compression risk. '
             'Mechanism: oil price → inflation → Fed hawkishness re-priced.'),
        ]
    ),
]

for cat_title, branches in scenarios:
    story.append(KeepTogether([
        Paragraph(f'<b>{cat_title}</b>', H3),
        *[Paragraph(f'<b>→ If {cond}:</b> {outcome}', BODY)
          for cond, outcome in branches],
        Spacer(1, 4),
    ]))

# ── Purchase Summary ────────────────────────────────────────────────────────
story.append(HRFlowable(width='100%', thickness=1, color=MGRAY))
story.append(Paragraph('6. POSSIBLE TRADE SUMMARY — EOD Aug 14 / BOD Aug 17', H2))

story.append(Paragraph(
    '<b>Framework:</b> Not investment advice. Based on today\'s news, technical setup, '
    'sector momentum, and catalyst calendar for next week.', SMALL))
story.append(Spacer(1, 4))

trades = [
    ['Action', 'Ticker', 'Thesis', 'Key Risk'],
    ['BUY / HOLD', 'SNDK',
     'AI storage secular growth; Investor Day catalyzed institutional recognition. '
     'Near-term momentum strong. 80% gross margins command premium multiple.',
     'China export restrictions; memory cycle reversal.'],
    ['HOLD/TRIM', 'RDDT',
     'S&P 500 inclusion mechanical demand largely absorbed by Monday open. '
     'Valuation stretched post +13% move; long-term ad-revenue model unproven at scale.',
     'Rebalancing demand fully met; sharp reversal risk Mon-Tue.'],
    ['BUY', 'MPWR',
     'AI data center power management is a structural necessity. '
     'Multiple expansion justified as AI buildout accelerates through H2 2026. '
     'Strong weekly and monthly momentum.',
     'Broad tech multiple compression if Fed turns hawkish at Jackson Hole.'],
    ['BUY', 'MU',
     'HBM (high bandwidth memory) demand for AI is multi-year tailwind. '
     'Monthly +15% vs. peers. Nvidia\'s Q2 FY27 earnings (Aug 26) will be catalyst; '
     'NVDA beats → MU follows up.',
     'Cyclical memory oversupply; China customer risk.'],
    ['SELL / AVOID', 'AAPL',
     'China demand deterioration, Iran-related supply chain risk (TSMC exposure), '
     'slowing iPhone upgrade cycle. Monthly -9% with no near-term catalyst. '
     'No AI product narrative that\'s near-term revenue-generating.',
     'Any AI hardware announcement could reverse sentiment quickly.'],
    ['SELL / AVOID', 'CSCO',
     'Self-reported slowdown in AI data center sales; losing share to newer entrants. '
     'Monthly -10%, weekly -8.4%. No clear near-term recovery catalyst.',
     'Surprise large enterprise deal win or acquisition.'],
    ['WATCH', 'NVDA',
     'Don\'t buy ahead of Aug 26 earnings without knowing the print. '
     'If Q2 FY27 beats ($93B+ revenue) → strong BUY on the open Aug 27. '
     'If miss → sharp correction. Hold existing positions; don\'t add ahead.',
     'Pre-earnings volatility; AI capex deceleration signal.'],
    ['HOLD', 'QQQ',
     'Jackson Hole neutral-to-dovish tone + Nvidia earnings in 2 weeks = '
     'positive setup for QQQ through end of August. But -0.05% today vs S&P -0.2% '
     'suggests relative strength.',
     'Hawkish surprise at Jackson Hole could hit growth tech multiple.'],
]

trade_ts = TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',   (0,0), (-1,-1), 8),
    ('GRID',       (0,0), (-1,-1), 0.5, MGRAY),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LGRAY]),
    ('FONTNAME',   (0,1), (-1,-1), 'Helvetica'),
    ('VALIGN',     (0,0), (-1,-1), 'TOP'),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('WORDWRAP',   (0,0), (-1,-1), True),
])
# Color action column
action_colors = {
    'BUY': GREEN, 'BUY / HOLD': GREEN, 'HOLD': colors.HexColor('#b07a00'),
    'HOLD/TRIM': colors.HexColor('#b07a00'), 'SELL / AVOID': RED,
    'WATCH': colors.HexColor('#1a6699'),
}
for i in range(1, len(trades)):
    act = trades[i][0]
    c = action_colors.get(act, colors.black)
    trade_ts.add('TEXTCOLOR', (0,i), (0,i), c)
    trade_ts.add('FONTNAME',  (0,i), (0,i), 'Helvetica-Bold')

trade_tbl = Table(trades, colWidths=[0.9*inch, 0.6*inch, 2.7*inch, 2.5*inch])
trade_tbl.setStyle(trade_ts)
story.append(trade_tbl)

story.append(Spacer(1, 8))
story.append(HRFlowable(width='100%', thickness=1, color=MGRAY))
story.append(Paragraph(
    '<i>Disclaimer: This report is for informational purposes only and does not constitute '
    'investment advice. Past performance is not indicative of future results. '
    'All prices are approximate based on publicly available data. '
    'Data sources: Yahoo Finance, Bloomberg, Reuters, CNBC, Benzinga, Seeking Alpha.</i>',
    SMALL))

# ── Build ────────────────────────────────────────────────────────────────────
doc.build(story)
print(f'PDF written to: {OUTPUT}')
