#!/usr/bin/env python3
"""Generate markets PDF report for 2026-06-29."""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

REPORT_DATE = "2026-06-29"
OUTPUT = f"/home/user/news/{REPORT_DATE}/reports/markets-{REPORT_DATE}.pdf"

# ── verified data ────────────────────────────────────────────────────────────
SPY_CLOSE    = 738.44
SPY_PREV     = 728.99
SPY_CHG_PCT  = (SPY_CLOSE - SPY_PREV) / SPY_PREV * 100   # +1.30%
SPY_52H      = 760.40
SPY_52L      = 591.89
SPY_1YR_RET  = 18.55   # % from search results

QQQ_CLOSE    = 723.00
QQQ_PREV     = 707.12  # estimated: QQQ_CLOSE / 1.0225
QQQ_CHG_PCT  = (QQQ_CLOSE - QQQ_PREV) / QQQ_PREV * 100   # +2.24%
QQQ_52H      = 733.32
QQQ_52L      = 511.93
QQQ_1YR_RET  = 30.61

def arrow(pct):
    return "▲" if pct >= 0 else "▼"

def signed(pct):
    return f"{arrow(pct)} {abs(pct):.2f}%"

# ── build doc ────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(OUTPUT, pagesize=LETTER,
                        rightMargin=0.75*inch, leftMargin=0.75*inch,
                        topMargin=0.75*inch, bottomMargin=0.75*inch)

styles = getSampleStyleSheet()
H1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=18,
                    spaceAfter=4, textColor=colors.HexColor('#1a1a2e'))
H2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13,
                    spaceAfter=4, spaceBefore=12,
                    textColor=colors.HexColor('#16213e'))
BODY = ParagraphStyle('BODY', parent=styles['Normal'], fontSize=9.5,
                      leading=14, spaceAfter=6)
BOLD = ParagraphStyle('BOLD', parent=BODY, fontName='Helvetica-Bold')
SMALL = ParagraphStyle('SMALL', parent=BODY, fontSize=8,
                       textColor=colors.HexColor('#555555'))
CENTER = ParagraphStyle('CENTER', parent=BODY, alignment=TA_CENTER)

story = []

# ── HEADER ───────────────────────────────────────────────────────────────────
story.append(Paragraph("US Markets Daily Report", H1))
story.append(Paragraph(f"<b>Date:</b> {REPORT_DATE} &nbsp;|&nbsp; "
                        f"<b>As of:</b> 4:00 PM ET (market close)", BODY))
story.append(HRFlowable(width="100%", thickness=1.5,
                         color=colors.HexColor('#16213e')))
story.append(Spacer(1, 0.12*inch))

# ── SNAPSHOT TABLE ────────────────────────────────────────────────────────────
story.append(Paragraph("1. SPY / QQQ Snapshot", H2))

snap_data = [
    ['Ticker', 'Close', 'Chg (Day)', '52-Wk High', '52-Wk Low', '1-Yr Return'],
    ['SPY',
     f"${SPY_CLOSE:.2f}",
     signed(SPY_CHG_PCT),
     f"${SPY_52H:.2f}",
     f"${SPY_52L:.2f}",
     signed(SPY_1YR_RET)],
    ['QQQ',
     f"${QQQ_CLOSE:.2f}",
     signed(QQQ_CHG_PCT),
     f"${QQQ_52H:.2f}",
     f"${QQQ_52L:.2f}",
     signed(QQQ_1YR_RET)],
]

snap_col_widths = [0.7*inch, 0.85*inch, 1.0*inch, 0.9*inch, 0.9*inch, 1.0*inch]
snap_tbl = Table(snap_data, colWidths=snap_col_widths)
snap_tbl.setStyle(TableStyle([
    ('BACKGROUND',   (0,0), (-1,0),  colors.HexColor('#16213e')),
    ('TEXTCOLOR',    (0,0), (-1,0),  colors.white),
    ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
    ('FONTSIZE',     (0,0), (-1,-1), 9),
    ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
    ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.HexColor('#f0f4ff'),
                                      colors.HexColor('#e0e8ff')]),
    ('GRID',         (0,0), (-1,-1), 0.5, colors.HexColor('#aaaacc')),
    ('TOPPADDING',   (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
]))
story.append(snap_tbl)
story.append(Paragraph(
    "<i>1-yr return sourced from web searches (52-wk data). "
    "Historical prices.csv currently holds 2 confirmed trading days "
    "(Jun 26–29) due to upstream data-source 403 blocks; "
    "full backfill requires a non-blocked Yahoo Finance / data API connection.</i>",
    SMALL))
story.append(Spacer(1, 0.1*inch))

# Market-wide context
story.append(Paragraph(
    "<b>Broader indices close (June 29, 2026):</b> "
    "DJIA 52,182.74 (+0.59%) — <i>first-ever close above 52,000, Alphabet's debut</i> &nbsp;|&nbsp; "
    "S&P 500 7,440.43 (+1.18%) &nbsp;|&nbsp; "
    "Nasdaq Composite 25,820.14 (+2.07%) &nbsp;|&nbsp; "
    "Nasdaq-100 +2.25%",
    BODY))
story.append(HRFlowable(width="100%", thickness=0.5,
                         color=colors.HexColor('#aaaacc')))

# ── NEWS SUMMARY ──────────────────────────────────────────────────────────────
story.append(Paragraph("2. Today's Market-Moving News", H2))

news_items = [
    ("US–Iran Ceasefire Announced",
     "The US and Iran agreed Sunday to end hostilities in their four-month war, "
     "with a framework calling for reopening of the Strait of Hormuz as soon as Friday. "
     "Oil futures fell sharply; stock futures surged overnight. "
     "Asia surged Monday morning (Nikkei 225 +5.5%, Kospi +5.7%)."),
    ("Supreme Court Upholds Fed Independence — Lisa Cook Stays",
     "SCOTUS ruled 5-4 (Chief Justice Roberts writing for majority) that President Trump "
     "cannot fire Federal Reserve Board Governor Lisa Cook — the first governor "
     "ever fired in the Fed's 111-year history — without cause. "
     "The ruling preserves the structural independence of the Fed Board."),
    ("Alphabet Joins the Dow Jones Industrial Average",
     "Alphabet (GOOGL) made its debut in the DJIA today, replacing a prior component. "
     "Shares rose approximately 4% in late morning trading, pushing the DJIA above 52,000 for the first time."),
    ("Mag-7 / Hyperscaler Tech Rebound",
     "After a paltry performance the prior week, large-cap tech stocks broadly rallied. "
     "The Nasdaq-100 gained +2.25%. Key names include Microsoft, Nvidia, Meta, Apple, Amazon."),
    ("Iridium Communications +21% — Rocket Lab $8B Acquisition",
     "Rocket Lab announced an $8 billion deal to acquire satellite-communications company Iridium. "
     "IRDM surged 21%; Rocket Lab (RKLB) gained 8.3%."),
    ("Charter Communications +14.5% & Comcast +9.8% — Telecom Restructuring",
     "Comcast unveiled a restructuring plan and reports surfaced of SpaceX discussions involving "
     "Charter, driving a sharp re-rating of cable/telecom."),
    ("Viasat +14.2% — Defense/Space Wins",
     "Viasat rallied on investor enthusiasm following recent contract wins with the US Space Force."),
    ("PCE Inflation: 4.10% Annual (May 2026, released June 25)",
     "Personal Consumption Expenditures rose to 4.10% YoY in May from 3.80% in April. "
     "Fed held rates at 3.50–3.75% for a 4th consecutive meeting (June 17 FOMC), "
     "dropped easing-leaning forward guidance; new Chair Kevin Warsh has adopted a hawkish-patience stance."),
]

for title, body in news_items:
    story.append(Paragraph(f"<b>• {title}</b>", BOLD))
    story.append(Paragraph(f"  {body}", BODY))

story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aaaacc')))

# ── NEWS → TODAY'S MOVES ──────────────────────────────────────────────────────
story.append(Paragraph("3. News → Today's Moves", H2))

story.append(Paragraph(
    f"<b>SPY:</b> {signed(SPY_CHG_PCT)} (${SPY_PREV:.2f} → ${SPY_CLOSE:.2f})  |  "
    f"<b>QQQ:</b> {signed(QQQ_CHG_PCT)} (${QQQ_PREV:.2f}* → ${QQQ_CLOSE:.2f})  "
    f"<i>(*QQQ prior close estimated from Nasdaq-100 +2.25% intraday move)</i>",
    BOLD))
story.append(Spacer(1, 0.06*inch))

moves_data = [
    ['Driver', 'Direction', 'SPY Impact', 'QQQ Impact', 'Mechanism'],
    ['US–Iran Ceasefire',
     '++', '+0.7–0.9%', '+0.9–1.2%',
     'Risk-on global surge; oil-cost deflation boosts growth expectations; '
     'supply-chain / logistics risk premium collapses; '
     'Asia gap-up carried through US open'],
    ['SCOTUS: Fed Independence',
     '+', '+0.2–0.3%', '+0.1–0.2%',
     'Removes tail risk of politically compromised Fed; '
     'reduces rate-policy uncertainty; '
     'financial sector (banks, insurance) re-rates positively'],
    ['Alphabet joins DJIA (+4%)',
     '+', '+0.1%', '+0.5–0.7%',
     'Index-inclusion forced buying from DJIA trackers; '
     'Alphabet is a top QQQ weight (~4%), '
     'mechanically lifting QQQ by ~0.16% per 4% GOOGL move; '
     'sentiment halo for Mag-7'],
    ['Tech / Mag-7 rebound',
     '+', '+0.3–0.4%', '+0.8–1.0%',
     'Rotation back into growth after prior-week weakness; '
     'AI spend narrative re-affirmed; '
     'QQQ\'s ~50%+ tech weighting amplifies the move vs SPY'],
    ['Iridium / Rocket Lab M&A',
     'neutral→+', 'minimal', 'minimal',
     'Idiosyncratic; boosts sentiment around "new space" / satellite; '
     'small absolute weight in indices'],
    ['Elevated PCE 4.1%',
     '–', 'offset ~0.1%', 'offset ~0.1%',
     'Hawkish headwind — keeps Fed on hold, compresses P/E multiples; '
     'partially masked today by risk-on geopolitical relief'],
]

mv_col_widths = [1.0*inch, 0.55*inch, 0.75*inch, 0.75*inch, 3.25*inch]
mv_tbl = Table(moves_data, colWidths=mv_col_widths)
mv_tbl.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#16213e')),
    ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
    ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',      (0,0), (-1,-1), 8),
    ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ('WORDWRAP',      (0,0), (-1,-1), 'CJK'),
    ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.HexColor('#f9fafb'),
                                       colors.HexColor('#eef2ff')]),
    ('GRID',          (0,0), (-1,-1), 0.4, colors.HexColor('#aaaacc')),
    ('TOPPADDING',    (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING',   (0,0), (-1,-1), 4),
]))
story.append(mv_tbl)
story.append(Paragraph(
    "<b>Summary:</b> Today's +1.30% SPY and +2.24% QQQ were driven <i>primarily</i> by "
    "geopolitical relief (US–Iran ceasefire removing a four-month oil-shock and "
    "supply-chain risk premium), <i>secondarily</i> by the SCOTUS ruling preserving "
    "Fed Board independence (reducing rate-policy uncertainty), and "
    "<i>thirdly</i> by Alphabet's DJIA debut igniting a broader Mag-7 / tech rebound. "
    "QQQ outperformed SPY by ~94 bps given its heavier tech/Nasdaq-100 concentration. "
    "Elevated PCE (4.10%) acted as a mild headwind but was overwhelmed by the risk-on tone.",
    BODY))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aaaacc')))

# ── NEXT-DAY SCENARIOS ────────────────────────────────────────────────────────
story.append(Paragraph("4. Next-Day Scenarios — Tuesday June 30, 2026", H2))
story.append(Paragraph(
    "<b>Context:</b> June 30 is <i>end-of-quarter (Q2 2026)</i> — institutional "
    "rebalancing flows can amplify intraday volatility. The week is holiday-shortened "
    "(markets closed Friday July 4, observed). The dominant overhang is Thursday's "
    "June Jobs Report (July 2, released one day early).",
    BODY))
story.append(Spacer(1, 0.06*inch))

scenarios = [
    ("1. Conference Board Consumer Confidence — June 2026 (Tue AM release)",
     [("Strong / Beat prior month",
       "SPY +0.3–0.5%, QQQ +0.2–0.4%",
       "Shows consumer resilient despite 4.1% PCE; validates soft-landing thesis; "
       "cyclicals and discretionary (XLY) outperform. "
       "Mechanism: higher confidence → forward spending → revenue visibility for S&P 500 earners."),
      ("Weak / Miss prior month",
       "SPY –0.3–0.6%, QQQ –0.2–0.4%",
       "Consumer feeling inflation squeeze; stagflation narrative resurfaces; "
       "retail/discretionary sell off. "
       "Mechanism: confidence collapse historically leads spending by 1-2 quarters, "
       "threatening 2H EPS estimates."),
     ]),
    ("2. US–Iran Ceasefire Durability (Developing Story)",
     [("Ceasefire holds / Hormuz reopening confirmed",
       "SPY flat to +0.2%, QQQ flat to +0.2%; oil remains lower",
       "Market has already priced much of the relief; "
       "confirming news is a gentle incremental positive. "
       "Energy (XLE) continues lower; industrials/transport benefit from "
       "lower fuel costs. No major SPY/QQQ reaction expected unless new positive details emerge."),
      ("Ceasefire fractures / new hostilities",
       "SPY –1.5% to –2.5%, QQQ –1.5% to –2.0%; oil +3–5%",
       "Violent reversal of today's gains. "
       "Mechanism: Strait of Hormuz closure risk reprices ~5-7% of global oil supply; "
       "inflation expectations spike → Fed stays higher longer → "
       "growth multiple compression hits QQQ hardest."),
     ]),
    ("3. End-of-Quarter Rebalancing (June 30 = Q2 close)",
     [("Tech was Q2's outperformer — institutional rebalancing sells equities",
       "QQQ –0.5% to –1.0% intraday pressure, SPY –0.2% to –0.5%",
       "60/40 funds and pension rebalancers mechanically sell equities (especially "
       "outperforming tech) to buy bonds at quarter-end. "
       "This is a <i>technical</i> / flow-driven move, not fundamental. "
       "Often reverses in the first days of July as new quarter begins."),
      ("Bond buying absorbs equity selling without large moves",
       "SPY/QQQ range-bound ±0.3%",
       "If bond demand meets the rebalancing supply cleanly, equities see "
       "mild volatility but no directional trend. "
       "Watch the last 30 minutes of the session (window-dressing flows)."),
     ]),
    ("4. June Jobs Report Preview Risk (Thursday July 2 — Shadow over Tuesday)",
     [("Consensus at ~110K payrolls; market positioning cautious ahead",
       "Tuesday likely sees reduced risk-taking / higher-than-usual hedging",
       "With jobs +172K in May and June consensus at +110K, "
       "investors are pre-positioning for a potential slowdown read. "
       "Any soft Tuesday data (confidence miss) could amplify Thursday-preview jitters, "
       "pulling SPY –0.5% to –0.8% as markets de-risk before the number. "
       "Mechanism: weaker jobs → potential Fed cut scenario → "
       "short-term negative (recession fear) but longer-term positive (easing)."),
      ("Jobs report pre-leak / survey data surprises to the upside on Tuesday",
       "SPY +0.5–0.8%, QQQ +0.4–0.7%",
       "If ISM services or JOLTS (if released) signal labor-market strength, "
       "markets may trade relief (soft landing confirmed), "
       "especially with geopolitical risk now diminished. "
       "Financials and cyclicals would lead."),
     ]),
]

for cat_title, branches in scenarios:
    story.append(Paragraph(f"<b>{cat_title}</b>", BOLD))
    for branch_label, reaction, mechanism in branches:
        story.append(Paragraph(
            f"&nbsp;&nbsp;<b>IF</b> {branch_label}: "
            f"<b>{reaction}</b> — {mechanism}",
            BODY))
    story.append(Spacer(1, 0.04*inch))

story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aaaacc')))

# ── WEEK-AHEAD CALENDAR ───────────────────────────────────────────────────────
story.append(Paragraph("5. Week-Ahead Calendar (Jun 30 – Jul 3, 2026)", H2))
cal_data = [
    ['Date', 'Event', 'Consensus / Notes'],
    ['Tue Jun 30', 'Conference Board Consumer Confidence (Jun)', 'Prior month reading; June = Q2 close'],
    ['Tue Jun 30', 'End of Q2 2026', 'Institutional rebalancing / window-dressing flows'],
    ['Wed Jul 1',  'ISM Manufacturing PMI (Jun)', 'Manufacturing contraction / expansion threshold at 50'],
    ['Thu Jul 2',  'June Employment Situation (BLS) — EARLY release', 'Consensus: ~110K NFP; May was +172K'],
    ['Thu Jul 2',  'Initial Jobless Claims', 'Weekly labor-market pulse'],
    ['Fri Jul 3',  'US markets CLOSED — Independence Day (observed)', ''],
]

cal_tbl = Table(cal_data, colWidths=[1.0*inch, 2.5*inch, 3.05*inch])
cal_tbl.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#16213e')),
    ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
    ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',      (0,0), (-1,-1), 8.5),
    ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
    ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.HexColor('#f9fafb'),
                                       colors.HexColor('#eef2ff')]),
    ('GRID',          (0,0), (-1,-1), 0.4, colors.HexColor('#aaaacc')),
    ('TOPPADDING',    (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING',   (0,0), (-1,-1), 4),
    ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
]))
story.append(cal_tbl)
story.append(Spacer(1, 0.08*inch))

# ── DATA NOTES ────────────────────────────────────────────────────────────────
story.append(Paragraph("Data Sources & Notes", H2))
story.append(Paragraph(
    "• SPY close $738.44 and QQQ close $723.00 sourced via web search (Kalshi/Bitget prediction market data, "
    "TheStreet market recap, multiple aggregator searches) as of June 29, 2026 4:00 PM ET.<br/>"
    "• Prior closes: SPY $728.99 confirmed (Jun 26 search result); "
    "QQQ $707.12 <i>estimated</i> back-calculated from Nasdaq-100 +2.25% session move.<br/>"
    "• 52-week stats (SPY: H $760.40 Jun 2 / L $591.89 Jun 23 2025; "
    "QQQ: H $733.32 May 27 / L $511.93 May 30 2025) and 1-year returns "
    "(SPY +18.55%, QQQ +30.61%) sourced from web search aggregators.<br/>"
    "• Full 252-day historical backfill to prices.csv was blocked (HTTP 403) from "
    "Yahoo Finance, MacroTrends, StockAnalysis, Stooq, and yfinance — gap noted. "
    "Use a direct brokerage API or Tiingo/Polygon.io key to enable automated nightly append.<br/>"
    "• All analysis is read-only / observational. No trades placed or simulated.",
    SMALL))

# ── BUILD ─────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF written: {OUTPUT}")
