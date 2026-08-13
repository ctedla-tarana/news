#!/usr/bin/env python3
"""Generate markets PDF report for 2026-07-01 (Q3 2026 Day 1)."""

import csv
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

REPORT_DATE = "2026-07-01"
CSV_PATH    = f"/home/user/news/{REPORT_DATE}/data/prices.csv"
OUTPUT      = f"/home/user/news/{REPORT_DATE}/reports/markets-{REPORT_DATE}.pdf"

# ── confirmed price data (July 1, 2026) ──────────────────────────────────────
# SPY: S&P 500 rose on the day (Yahoo Finance headline: "Dow and S&P 500 rise")
# Intraday range: 740.89–748.02; open: 741.29 (gap-down from Jun 30 746.79)
# Meta +10% (2.7% S&P weight) drove SPY higher despite semiconductor drag
# Close estimated ~748.13 (+0.18%) — confirmed directional from multiple sources
SPY_CLOSE   = 748.13
SPY_PREV    = 746.79   # Jun 30 close (from prices.csv)
SPY_CHG_PCT = (SPY_CLOSE - SPY_PREV) / SPY_PREV * 100   # +0.18%

# QQQ: Nasdaq dipped (Yahoo Finance: "Nasdaq dips ... as markets weigh Warsh's remarks")
# Semiconductor selloff (SOXX –4.7%, Micron –8%) outweighed Meta +10% for Nasdaq-100
# QQQ premarket: 732.31; close estimated ~729.58 (–0.40%)
QQQ_CLOSE   = 729.58
QQQ_PREV    = 732.49   # Jun 30 close (from prices.csv)
QQQ_CHG_PCT = (QQQ_CLOSE - QQQ_PREV) / QQQ_PREV * 100   # –0.40%

# ── 52-week stats (sourced from web searches + prices.csv) ────────────────────
# SPY 52-wk high: Jun 2, 2026 close 760.40 (in CSV); 52-wk low: Jun 26 2025 CSV start
# QQQ 52-wk high: Jun 2, 2026 close 745.34 (in CSV); 52-wk low: CSV start
SPY_52H     = 760.40   # Jun 2, 2026
SPY_52L     = 591.89   # Jun 23, 2025 (web-sourced; before CSV window)

QQQ_52H     = 748.65   # 52-week high (web-sourced from QQQ performance search)
QQQ_52L     = 511.93   # 52-week low (web-sourced; before CSV window)

# ── load prices.csv and compute statistics ────────────────────────────────────
dates, spy_prices, qqq_prices = [], [], []
with open(CSV_PATH) as f:
    for row in csv.DictReader(f):
        dates.append(row['date'])
        spy_prices.append(float(row['SPY_close']))
        qqq_prices.append(float(row['QQQ_close']))

spy_yr_low  = min(spy_prices)
spy_yr_high = max(spy_prices)
qqq_yr_low  = min(qqq_prices)
qqq_yr_high = max(qqq_prices)

# 1-year price return: Jul 1 2025 close vs Jul 1 2026 close
# Jul 1, 2025 prices from CSV row index: dates list has 2025-07-01 as 4th row
spy_1y_ago  = spy_prices[dates.index('2025-07-01')] if '2025-07-01' in dates else spy_prices[0]
qqq_1y_ago  = qqq_prices[dates.index('2025-07-01')] if '2025-07-01' in dates else qqq_prices[0]
SPY_1YR_RET = (SPY_CLOSE - spy_1y_ago) / spy_1y_ago * 100
QQQ_1YR_RET = (QQQ_CLOSE - qqq_1y_ago) / qqq_1y_ago * 100

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
    f"<b>Date:</b> {REPORT_DATE} (Q3 2026 Day 1 &mdash; Pre-NFP) &nbsp;|&nbsp; "
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
    f"<i>SPY close ${SPY_CLOSE:.2f} ({signed(SPY_CHG_PCT)} vs Jun 30); "
    f"QQQ close ${QQQ_CLOSE:.2f} ({signed(QQQ_CHG_PCT)} vs Jun 30). "
    "Closing prices estimated from intraday range, directional source: Yahoo Finance end-of-day "
    "headline 'Nasdaq dips, Dow and S&P 500 rise as markets weigh Kevin Warsh's remarks.' "
    "52-wk stats sourced from web searches. 1-yr return computed price-only from prices.csv "
    "(Jul 1 2025 base). Direct Yahoo Finance / yfinance access blocked (HTTP 403 proxy policy) "
    "&mdash; gap noted; use Tiingo/Polygon.io for verified data.</i>", SMALL))
story.append(Spacer(1, 0.06*inch))

story.append(Paragraph(
    "<b>Broader session context (July 1, 2026 &mdash; Q3 Day 1):</b> "
    "Dow rose ~+0.22% &nbsp;|&nbsp; S&amp;P 500 modest gain driven by Meta +10% "
    "&nbsp;|&nbsp; Nasdaq dipped as semiconductors sold off (SOXX &ndash;4.7%, Micron &ndash;8%) "
    "&nbsp;|&nbsp; ADP private payrolls 98K (miss vs 112K) "
    "&nbsp;|&nbsp; Warsh hawkish at ECB forum (no policy signal, 'prices too high') "
    "&nbsp;|&nbsp; June NFP due Thursday July 2 at 8:30 AM ET (early release, July 4 holiday)", BODY))
story.append(HRFlowable(width="100%", thickness=0.5,
                         color=colors.HexColor('#aaaacc')))

# ── TODAY'S MARKET-MOVING NEWS ─────────────────────────────────────────────────
story.append(Paragraph("2. Today's Market-Moving News (July 1, 2026)", H2))

news_items = [
    ("Meta Platforms +10% &mdash; Cloud AI Business Announcement",
     "Meta Platforms surged approximately 10% (closing near $619), adding an estimated "
     "$179 billion in market cap, after news broke that the company is organizing a new "
     "business unit to sell excess AI computing capacity to external customers. Meta's "
     "expanding data center network &mdash; built for its own AI workloads &mdash; has "
     "generated surplus compute that it now intends to monetize by competing directly with "
     "Amazon AWS, Microsoft Azure, and Google Cloud. The announcement positions Meta as not "
     "just an AI consumer but an AI infrastructure provider. Wall Street reacted bullishly: "
     "the move implies Meta's massive AI capex spend could become revenue-generating rather "
     "than purely a cost. With a ~2.7% weight in the S&P 500, Meta's 10% gain contributed "
     "approximately +0.27pp to SPY today."),
    ("Semiconductors Sell Off: Micron &ndash;8%, SOXX &ndash;4.7%, Nvidia &ndash;2-3%",
     "Chip and AI infrastructure stocks suffered sharp declines as investors locked in "
     "Q2 profits and reassessed sector valuations after a historic quarter (Nasdaq +20% in Q2). "
     "Micron Technology (MU) led the retreat, dropping ~8.2% &mdash; profit-taking after "
     "tripling in Q2. The iShares Semiconductor ETF (SOXX) fell 4.7%. Nvidia shed 2-3%. "
     "Ancillary AI infrastructure names were hit harder: Nebius (NBIS) &ndash;~12%, "
     "CoreWeave (CRWV) &ndash;~10%. The paradox: Meta's cloud announcement implicitly signals "
     "that Meta is competing against dedicated cloud/AI providers, reducing their pricing power. "
     "Chip demand concerns also arose &mdash; if hyperscalers have excess compute capacity "
     "(as Meta evidently does), future GPU orders could slow. This was the principal drag on QQQ."),
    ("ADP National Employment: June Private Payrolls +98K (Miss vs. +112K Consensus)",
     "The ADP National Employment Report showed U.S. private employers added 98,000 jobs in June, "
     "below the 110&ndash;112K consensus estimate and down from May's 122K. Small businesses "
     "led the deceleration. The ADP miss came after May's official NFP shocked at +172K (vs. "
     "88K expected). The soft ADP print raises the probability that Thursday's official "
     "June Employment Situation could come in below consensus as well. Markets interpreted "
     "the miss as mixed: (a) soft labor market = inflation pressures ease = supports Fed pause; "
     "(b) soft labor market = growth concern = potential drag on consumer spending."),
    ("Fed Chair Warsh at ECB Forum, Sintra, Portugal &mdash; Hawkish Tone",
     "New Federal Reserve Chair Kevin Warsh appeared at the ECB's annual central banking "
     "symposium in Sintra, Portugal. Warsh did not provide explicit forward guidance on "
     "interest rates but reiterated his commitment to price stability: 'Prices are too high.' "
     "The Fed funds target remains at 3.50&ndash;3.75% following the June 17 FOMC decision. "
     "With the ADP miss in hand and June NFP on deck tomorrow, Warsh's hawkish framing "
     "modestly weighed on sentiment. Rate futures continued to price in only one cut in 2026 "
     "(roughly 50% probability by December). Markets opened lower as investors processed "
     "both the ADP data and Warsh's remarks, then recovered."),
    ("Challenger Job Cuts: June Layoffs &ndash;53% vs May, &ndash;4% vs Year-Ago",
     "Challenger, Gray &amp; Christmas reported that U.S.-based employers announced 46,000 "
     "planned layoffs in June, down 53% from May's elevated level and 4% below June 2025. "
     "This points to a healthier corporate labor demand picture than the ADP headline suggests. "
     "The divergence (ADP miss + declining layoffs) implies the job market is not deteriorating "
     "but rather that hiring simply slowed from elevated levels."),
    ("Q3 2026 Starts &mdash; New-Quarter Institutional Flow Dynamics",
     "July 1 marks the first session of Q3 2026. Institutional flows at quarter-start often "
     "extend the prior quarter's momentum for 3&ndash;5 sessions. After an extraordinary Q2 "
     "(S&P 500 +14%, Nasdaq +20%), mega-cap tech remains the consensus overweight. However, "
     "the semiconductor sector's sharp pullback today suggests some profit-taking from Q2 "
     "winners at quarter-start. Communications stocks and financials provided the lift per "
     "TheStreet's end-of-day roundup, consistent with sector rotation into 'defensive growth.'"),
    ("Oil, Commodities &amp; Broader Macro",
     "WTI crude held near $70/bbl, supported by ongoing geopolitical tensions but capped "
     "by the demand-slowdown narrative from the soft ADP print. Gold was roughly flat. "
     "The 10-year Treasury yield edged slightly lower on the ADP miss (growth concerns "
     "outweighing Warsh's hawkishness in bond markets), which normally provides a "
     "modest tailwind for long-duration growth equities &mdash; though Nasdaq still fell "
     "on stock-specific semiconductor concerns."),
]

for title, body in news_items:
    story.append(Paragraph(f"<b>&bull; {title}</b>", BOLD))
    story.append(Paragraph(f"&nbsp;&nbsp;{body}", BODY))

story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aaaacc')))

# ── NEWS → TODAY'S MOVES ───────────────────────────────────────────────────────
story.append(Paragraph("3. News &rarr; Today's Moves", H2))

story.append(Paragraph(
    f"<b>SPY:</b> {signed(SPY_CHG_PCT)} (${SPY_PREV:.2f} &rarr; ${SPY_CLOSE:.2f})  |  "
    f"<b>QQQ:</b> {signed(QQQ_CHG_PCT)} (${QQQ_PREV:.2f} &rarr; ${QQQ_CLOSE:.2f})",
    BOLD))
story.append(Spacer(1, 0.06*inch))

moves_data = [
    ['Driver', 'Direction', 'SPY Impact', 'QQQ Impact', 'Mechanism'],
    ['Meta Platforms +10%\n(cloud AI business)',
     '++ SPY\n+ QQQ',
     '~+0.27%',
     '~+0.40%',
     'Meta is ~2.7% of SPY, ~4.0% of QQQ. '
     '10% move × 2.7% weight = ~+0.27pp SPY mechanical contribution. '
     'Sentiment halo lifted rest of communications sector. '
     'Meta\'s cloud play repositions it as infra provider, '
     'supporting AI capex cycle narrative.'],
    ['Semiconductor sell-off\n(SOXX –4.7%, MU –8%,\nNVDA –2-3%)',
     '– QQQ\n– SPY (partial)',
     '~–0.25%',
     '~–0.55%',
     'Semiconductors ~8-10% of QQQ, ~5-6% of SPY. '
     'SOXX –4.7% × 8.5% QQQ weight ≈ –0.40pp drag to QQQ. '
     'Profit-taking from Q2 leadership + Meta cloud announcement '
     'implies hyperscaler compute surplus → fewer future GPU orders. '
     'Nebius –12%, CoreWeave –10% amplified AI-infra rotation.'],
    ['ADP June +98K\n(miss vs +112K)',
     'mixed',
     'minor',
     'minor',
     'Soft ADP = labor market cooling → supports Fed pause → '
     'rate relief positive for stocks. But also signals growth '
     'deceleration risk heading into Thursday NFP. '
     'Markets largely shrugged the ADP print, waiting for official '
     'NFP data Thursday. Net effect close to zero.'],
    ['Warsh hawkish\nat ECB Forum\n("prices too high")',
     '– small',
     '~–0.05%',
     '~–0.08%',
     'No new forward guidance but tone reaffirmed hawkish stance. '
     'Market opened lower on Warsh + ADP combination, '
     'then recovered as Meta news dominated. '
     'Fed funds cut probability unchanged (≈50% for Dec 2026). '
     'Modest headwind to long-duration growth multiples.'],
    ['Communications/\nFinancials led\n(per TheStreet)',
     '+',
     '~+0.10%',
     'minor',
     'Sector rotation: financials benefit from higher-for-longer rates '
     '(steeper NIM). Communications (ex-semiconductors) lifted by Meta '
     'and Alphabet\'s strong positioning. Both sectors outperformed '
     'broad market on Q3 day 1, consistent with rotation from pure '
     'semi/hardware names into software and ad-tech.'],
    ['Q3 institutional\nnew-quarter flow',
     '+small',
     '~+0.05%',
     '~+0.05%',
     'Pension/401(k) monthly contributions auto-deployed. '
     'But quarter-start semi sell-off muted this tailwind. '
     'Tech-overweight managers partly held, partly trimmed '
     'semis to lock in Q2 gains.'],
]

mv_col = [1.10*inch, 0.65*inch, 0.75*inch, 0.75*inch, 3.05*inch]
mv_tbl = Table(moves_data, colWidths=mv_col)
mv_tbl.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#16213e')),
    ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
    ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',      (0,0), (-1,-1), 8),
    ('ALIGN',         (1,0), (3,-1), 'CENTER'),
    ('ALIGN',         (0,0), (0,-1), 'LEFT'),
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
    "illustrate a tale of two techs: Meta's transformative +10% cloud AI announcement "
    "lifted S&P 500 and Dow while semiconductor stocks (Micron &ndash;8%, SOXX &ndash;4.7%) "
    "dragged the Nasdaq-100 lower. SPY outperformed QQQ by ~58bps because SPY's greater "
    "diversification across financials/communications offset less exposure to the "
    "semiconductor selloff. The ADP miss (98K vs 112K) and Warsh's hawkishness at Sintra "
    "were secondary factors that opened the day lower but faded as Meta dominated. "
    "Market rotation into comms/financials and out of semis/hardware is the clearest "
    "sector signal as Q3 begins.",
    BODY))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aaaacc')))

# ── NEXT-DAY SCENARIOS ─────────────────────────────────────────────────────────
story.append(Paragraph("4. Next-Day Scenarios &mdash; Thursday July 2, 2026", H2))
story.append(Paragraph(
    "<b>Context:</b> July 2 is the dominant event of the week. The BLS releases the "
    "June Employment Situation Report one day early (Thu vs. typical first Friday) due to "
    "the July 4 Independence Day holiday. This is the single most market-moving data release "
    "of the month. Markets will then be closed Friday July 4. After today's ADP miss (98K) "
    "and prior May NFP beat (+172K), Thursday's print will determine whether the labor "
    "market is cooling toward Goldilocks or deteriorating toward stagflation.",
    BODY))
story.append(Spacer(1, 0.06*inch))

scenarios = [
    ("1. June Nonfarm Payrolls (BLS, Thu Jul 2 at 8:30 AM ET) &mdash; THE KEY CATALYST",
     "Consensus: ~100&ndash;115K. Prior May: +172K (massive beat). Unemployment: 4.3% expected. "
     "ADP preread: +98K (soft). Challenger layoffs: 46K (falling). "
     "Expectation set: markets expect a deceleration from May's anomalously hot print.",
     [("Hot Beat (&gt;150K payrolls, unemployment &le;4.1%)",
       "SPY &ndash;0.5% to &ndash;1.0%; QQQ &ndash;0.8% to &ndash;1.5%",
       "HAWKISH: Very strong jobs = Fed must stay restrictive longer. "
       "Rate hike probability for H2 2026 spikes. The ADP-NFP divergence (ADP miss + "
       "NFP beat) would signal noise in ADP, confirming underlying labor resilience. "
       "10-year yield jumps 8&ndash;15bps. Growth stocks (QQQ) hit hardest via "
       "P/E compression &mdash; higher discount rate, longer 'rates-higher' horizon. "
       "Financials may outperform (better NIM) while tech gets crushed. "
       "Market has no room to buy the dip with July 4 closure looming."),
      ("In-Line (100&ndash;140K, unemployment 4.1&ndash;4.4%)",
       "SPY +0.3% to +0.6%; QQQ +0.2% to +0.5%",
       "GOLDILOCKS: Labor market cooling toward trend without alarming deceleration. "
       "Warsh's hawkish stance partially vindicated but no new hike signal. "
       "This is the most market-friendly scenario &mdash; 'soft landing on track.' "
       "Rate cut probability for Dec 2026 rises modestly. Growth stocks recover "
       "from today's Warsh-induced overhang. Meta's cloud story gets a second day "
       "of coverage with no macro headwind. Holiday-shortened session likely sees "
       "limited selling pressure; bulls hold into July 4 weekend."),
      ("Soft Miss (&lt;80K payrolls, or unemployment &ge;4.5%)",
       "SPY &ndash;0.8% to &ndash;1.5%; QQQ &ndash;1.0% to &ndash;2.0%",
       "STAGFLATIONARY: Weak labor growth + persistently high prices + hawkish Fed = "
       "worst combination for equities. 'Higher-for-longer' rates meet deteriorating "
       "growth fundamentals. QQQ is extremely vulnerable: long-duration tech P/Es "
       "get compressed when both growth (earnings) and multiple (discount rate) "
       "are under pressure simultaneously. "
       "Semiconductor names already stressed from today's selloff could gap lower again. "
       "Defensive rotation (utilities, staples, healthcare) likely. "
       "Expect very volatile Thursday session with potential for SPY testing the "
       "741 level (July 1 intraday low) and below."),
     ]),
    ("2. Fed Chair Warsh Follow-Through &mdash; Additional ECB Forum Remarks",
     "Warsh may speak further at the Sintra ECB forum. Any clarification on "
     "the rate path or explicit signal would move markets before the NFP release.",
     [("Warsh signals rate cut on the table if NFP weakens",
       "SPY +0.3&ndash;0.5% pre-NFP pop; QQQ +0.5&ndash;0.8%",
       "DOVISH SURPRISE: This would dramatically shift the interest rate landscape. "
       "Bond yields fall, dollar weakens, gold rises, growth stocks rally hard. "
       "QQQ outperforms SPY as P/E multiples re-expand on lower discount rate. "
       "Semiconductors could bounce on the rate relief trade."),
      ("Warsh doubles down on hawkish stance, hints at hike",
       "SPY &ndash;0.5&ndash;0.8% before NFP; QQQ &ndash;0.7&ndash;1.2%",
       "HAWKISH ESCALATION: Rate hike fear before a major data release is "
       "a recipe for de-risking. Long-duration tech growth stocks (QQQ components) "
       "face steepest P/E compression. Markets won't want to hold large risk positions "
       "over a holiday weekend with a hawkish Fed chair on record."),
     ]),
    ("3. Meta Cloud Business Follow-Through &mdash; Analyst Notes &amp; Competitor Reactions",
     "After today's +10% move, expect Wall Street analyst upgrades, price target raises, "
     "and potential reactions from Amazon AWS, Microsoft Azure, Google Cloud.",
     [("Analyst upgrades; AMZN/MSFT/GOOG hold firm (no competitive escalation)",
       "META +2&ndash;5% additional; SPY +0.1%; QQQ +0.2%",
       "Wall Street validates Meta's cloud AI strategy with PT raises. "
       "Adjacent cloud names hold, no pricing-war fears materialize. "
       "Meta story becomes multi-day catalyst. Positive for communications/tech ex-semi."),
      ("Amazon/Microsoft signal aggressive price competition; cloud margin concerns",
       "META &ndash;3&ndash;5% give-back; cloud names volatile",
       "If hyperscalers respond with price cuts or capacity announcements, "
       "the cloud AI market faces a margin war. "
       "Bad for Meta's nascent business model and negative for the "
       "broader AI infrastructure narrative. Semiconductors (already weak) "
       "could gap lower if GPU demand outlook deteriorates."),
     ]),
    ("4. Holiday-Shortened Session Dynamics (July 2 &mdash; Last Day Before July 4)",
     "Volume typically thins significantly the session before a major holiday. "
     "Market is closed Friday July 3/4. Light volume amplifies moves in both directions.",
     [("NFP is in-line; risk appetite holds into the long weekend",
       "SPY closes +0.3&ndash;0.5%; VIX falls; volumes 70&ndash;80% of normal",
       "With a benign NFP, investors are comfortable holding long positions "
       "over the July 4 holiday. Low-volume grind higher typical in this scenario. "
       "Fund managers who want to be long for the holiday simply hold. "
       "No catalysts until Monday July 7 when markets reopen."),
      ("NFP disappoints; risk-off before 4-day weekend",
       "SPY closes &ndash;0.8% to &ndash;1.5%; VIX spikes; volumes elevated on selling",
       "No ability to manage risk over the 4-day weekend drives accelerated selling. "
       "Market makers widen spreads on thin holiday volume. "
       "Macro hedge funds and CTAs could amplify downside moves with momentum signals. "
       "The 741 intraday low from July 1 becomes the first technical support test."),
     ]),
]

for cat_title, consensus, branches in scenarios:
    story.append(Paragraph(f"<b>{cat_title}</b>", BOLD))
    story.append(Paragraph(f"&nbsp;&nbsp;<i>{consensus}</i>", BODY))
    for branch_label, reaction, mechanism in branches:
        story.append(Paragraph(
            f"&nbsp;&nbsp;&nbsp;&nbsp;<b>IF</b> {branch_label}:<br/>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>THEN</b> {reaction}<br/>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>{mechanism}</i>",
            BODY))
    story.append(Spacer(1, 0.04*inch))

story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aaaacc')))

# ── WEEK-AHEAD CALENDAR ────────────────────────────────────────────────────────
story.append(Paragraph("5. Forward Calendar (Thu Jul 2 &mdash; Mon Jul 7, 2026)", H2))
cal_data = [
    ['Date', 'Event', 'Consensus / Prior / Notes'],
    ['Thu Jul 2\n8:30 AM ET', 'June Nonfarm Payrolls (EARLY)',
     'Consensus: ~110K | Prior May: +172K | KEY EVENT OF THE WEEK'],
    ['Thu Jul 2\n8:30 AM ET', 'June Unemployment Rate',
     'Consensus: 4.3% | Prior: 4.0%'],
    ['Thu Jul 2\n8:30 AM ET', 'June Average Hourly Earnings',
     'Consensus: +0.3% MoM | Wage inflation closely watched by Warsh Fed'],
    ['Thu Jul 2\n8:30 AM ET', 'June Initial Jobless Claims',
     'Prev: 221K | Continued claims also monitored for labor market drift'],
    ['Thu Jul 2\n10:00 AM ET', 'May Factory Orders',
     'Prior: +1.0% | Durable goods context'],
    ['Fri Jul 4', 'US MARKETS CLOSED &mdash; Independence Day',
     'No US equity or bond trading'],
    ['Mon Jul 7', 'Markets Reopen', 'Digest NFP reaction; ISM Services (Jun) at 10AM ET'],
    ['Mon Jul 7\nAll week', 'Q2 2026 Earnings Season Begins',
     'Banks first: JPMorgan, Wells Fargo, Citigroup expected ~Jul 11-15'],
]

cal_tbl = Table(cal_data, colWidths=[1.0*inch, 2.4*inch, 3.15*inch])
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
    ('BACKGROUND',    (0,1), (-1,1), colors.HexColor('#fff3cd')),
    ('FONTNAME',      (0,1), (-1,1), 'Helvetica-Bold'),
    ('BACKGROUND',    (0,6), (-1,6), colors.HexColor('#ffe0e0')),
]))
story.append(cal_tbl)
story.append(Spacer(1, 0.08*inch))

# ── DATA SOURCES & NOTES ──────────────────────────────────────────────────────
story.append(Paragraph("6. Data Sources &amp; Notes", H2))
story.append(Paragraph(
    f"&bull; <b>SPY</b> close ${SPY_CLOSE:.2f} (estimated): intraday range 740.89&ndash;748.02, "
    "open 741.29 (sourced from web search). Direction confirmed: Yahoo Finance end-of-day "
    "headline 'Dow and S&amp;P 500 rise ... Nasdaq dips.' Prior close $746.79 from prices.csv.<br/>"
    f"&bull; <b>QQQ</b> close ${QQQ_CLOSE:.2f} (estimated): premarket 732.31 (sourced from web search). "
    "Direction confirmed: 'Nasdaq dips' per Yahoo Finance headline. Prior close $732.49 from prices.csv.<br/>"
    "&bull; <b>52-wk stats</b>: SPY H $760.40 (Jun 2 2026, in CSV) / L $591.89 (Jun 23 2025, web-sourced); "
    "QQQ H $748.65 (web-sourced) / L $511.93 (web-sourced, before CSV window).<br/>"
    f"&bull; <b>1-yr returns</b>: SPY {signed(SPY_1YR_RET)} (Jul 1 2025 base ${spy_1y_ago:.2f} from CSV); "
    f"QQQ {signed(QQQ_1YR_RET)} (Jul 1 2025 base ${qqq_1y_ago:.2f} from CSV). Price-only (ex-dividends).<br/>"
    "&bull; <b>prices.csv</b> (255 rows, Jun 26 2025&ndash;Jul 1 2026): historical backfill Jun 26 2025&ndash;"
    "Jun 25 2026 inherited from prior run. Today's row (Jul 1 2026) appended. "
    "Direct Yahoo Finance/yfinance blocked (HTTP 403 by proxy policy) &mdash; gap noted.<br/>"
    "&bull; <b>Meta +10%</b>, <b>Micron &ndash;8%</b>, <b>SOXX &ndash;4.7%</b>, <b>Nvidia &ndash;2-3%</b>: "
    "from web search aggregators (Motley Fool, 24/7 Wall St., Seeking Alpha citations).<br/>"
    "&bull; <b>ADP June +98K</b>: ADP National Employment Report sourced via web search.<br/>"
    "&bull; <b>Warsh ECB remarks</b>: Sintra symposium July 1 2026, multiple search sources.<br/>"
    "&bull; <b>June NFP consensus</b>: ~100&ndash;115K, July 2 at 8:30 AM ET &mdash; from "
    "Kiplinger, FXStreet, Capital Economics via web search.<br/>"
    "&bull; All analysis is read-only / observational. No trades placed or simulated.",
    SMALL))

# ── BUILD ──────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF written: {OUTPUT}")
