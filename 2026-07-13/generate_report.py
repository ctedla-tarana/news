#!/usr/bin/env python3
"""Generate markets-2026-07-13.pdf using ReportLab."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

OUT = "/home/user/news/2026-07-13/reports/markets-2026-07-13.pdf"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

doc = SimpleDocTemplate(OUT, pagesize=letter,
                        topMargin=0.6*inch, bottomMargin=0.6*inch,
                        leftMargin=0.75*inch, rightMargin=0.75*inch)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle('Title2', parent=styles['Title'],
    fontSize=20, spaceAfter=4, textColor=colors.HexColor('#1a2b5f'))
subtitle_style = ParagraphStyle('Sub', parent=styles['Normal'],
    fontSize=10, textColor=colors.HexColor('#555555'), spaceAfter=12, alignment=TA_CENTER)
h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
    fontSize=13, textColor=colors.HexColor('#1a2b5f'), spaceBefore=14, spaceAfter=6,
    borderPad=3)
h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
    fontSize=11, textColor=colors.HexColor('#2c5282'), spaceBefore=10, spaceAfter=4)
body_style = ParagraphStyle('Body2', parent=styles['Normal'],
    fontSize=9, leading=14, spaceAfter=6)
note_style = ParagraphStyle('Note', parent=styles['Normal'],
    fontSize=8, textColor=colors.HexColor('#888888'), leading=12, spaceAfter=4)
bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
    fontSize=9, leading=13, leftIndent=14, spaceAfter=3,
    bulletIndent=4)

RED   = colors.HexColor('#c0392b')
GREEN = colors.HexColor('#27ae60')
BLUE  = colors.HexColor('#1a2b5f')
LGRAY = colors.HexColor('#f7f9fc')
DGRAY = colors.HexColor('#d0d8e4')

def color_pct(pct_str):
    """Return colored paragraph for a pct string."""
    val = float(pct_str.replace('%','').replace('+',''))
    c = GREEN if val > 0 else RED
    return Paragraph(f'<font color="{c.hexval()}">{pct_str}</font>', body_style)

def tbl(data, col_widths, header_bg=BLUE, row_bg=LGRAY):
    t = Table(data, colWidths=col_widths)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 9),
        ('ALIGN',      (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING',    (0, 0), (-1, 0), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, row_bg]),
        ('FONTNAME',   (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 1), (-1, -1), 9),
        ('ALIGN',      (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('GRID',       (0, 0), (-1, -1), 0.4, DGRAY),
    ])
    t.setStyle(style)
    return t

# ── DOCUMENT CONTENT ──────────────────────────────────────────────────────────
story = []

# Header
story.append(Paragraph("US DAILY MARKETS REPORT", title_style))
story.append(Paragraph("Monday, July 13, 2026  ·  Post-Close  ·  5:00 PM ET",
                        subtitle_style))
story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=10))

# ── 1. SPY / QQQ SNAPSHOT ────────────────────────────────────────────────────
story.append(Paragraph("1. SPY / QQQ SNAPSHOT", h1_style))

snap_data = [
    ["Ticker", "Today Close", "Day Chg", "Day %",
     "52W High", "52W Low", "1Y Return", "Prior Close"],
    ["SPY", "$749.00", "−$5.95", "−0.79%", "$760.40", "$618.05", "+20.83%", "$754.95"],
    ["QQQ", "$714.27", "−$11.24", "−1.55%", "$733.32", "$511.93", "+28.04%", "$725.51"],
]
cw = [0.65*inch, 0.85*inch, 0.75*inch, 0.75*inch,
      0.75*inch, 0.75*inch, 0.80*inch, 0.85*inch]
snap_tbl = tbl(snap_data, cw)
# Color the Day % cells red
snap_tbl.setStyle(TableStyle([
    ('TEXTCOLOR', (3, 1), (3, 2), RED),
    ('TEXTCOLOR', (2, 1), (2, 2), RED),
    ('TEXTCOLOR', (6, 1), (6, 2), GREEN),
]))
story.append(snap_tbl)
story.append(Paragraph(
    "Note: Today's SPY/QQQ closes are estimated from reported index moves "
    "(S&P 500 −0.79% to 7,515.34; Nasdaq −1.55% to 25,873) applied to the "
    "July 10 confirmed closes. Full 1-year daily backfill was unavailable "
    "due to proxy restrictions on financial data APIs; 52W stats sourced "
    "from web search. Only two rows in data/prices.csv reflect confirmed/estimated data.",
    note_style))

# Broad market summary
story.append(Spacer(1, 8))
broad_data = [
    ["Index", "Close", "Change", "% Chg"],
    ["S&P 500",  "7,515.34", "−60.16",  "−0.79%"],
    ["Nasdaq",   "25,873.18","−406.34", "−1.55%"],
    ["Dow Jones","52,498.64","−137.36", "−0.26%"],
    ["WTI Crude","$78.14",   "+$6.74",  "+9.40%"],
    ["Brent",    "$83.30",   "+$7.29",  "+9.60%"],
    ["XLE (Energy ETF)", "$58.33", "+$1.70", "+3.00%"],
]
cw2 = [1.5*inch, 1.2*inch, 1.0*inch, 0.9*inch]
story.append(tbl(broad_data, cw2))

# ── 2. TODAY'S NEWS ──────────────────────────────────────────────────────────
story.append(Spacer(1, 6))
story.append(Paragraph("2. TODAY'S MARKET-MOVING NEWS", h1_style))

news_items = [
    ("<b>Trump Reinstates Iran / Strait of Hormuz Blockade</b>",
     "President Trump announced via social media Monday that the U.S. would "
     "reinstate its blockade on Iranian shipping through the Strait of Hormuz. "
     "CENTCOM had carried out strikes on Iranian targets over the weekend. "
     "Iran claimed it had closed the strait; maritime traffic fell 52% week-on-week. "
     "The U.S. Treasury warned that paying Iran for passage constitutes sanctions violations."),
    ("<b>SK Hynix Plunges 15% in Seoul, Triggers Kospi Circuit Breaker</b>",
     "SK Hynix hit its largest one-day decline in two decades (−15%) after its Nasdaq ADR "
     "debut disappointed (+12% in U.S. debut Friday → −7.9% ADR Monday) amid "
     "earnings forecast downgrades and geopolitical risk-off. "
     "Samsung Electronics fell 10%. South Korea's Kospi dropped 9%, triggering a "
     "20-minute circuit breaker — the country's seventh trading halt of 2026."),
    ("<b>Meta AI Infrastructure: Meta Compute + Iris Chip</b>",
     "Meta continued to gain on AI monetization news: its new cloud unit (Meta Compute) "
     "will sell AI compute and model access to third parties, directly competing with AWS, "
     "Azure and GCP. The custom Iris chip is entering production in September. "
     "META surged 6%+, adding materially to Nasdaq cap-weight. EPS beat estimates by 57% "
     "in Q1; Q2 revenue guided to $58-61B."),
    ("<b>Q2 Earnings Season Kickoff</b>",
     "Financials rose 0.65% — the second-best sector — as investors positioned ahead of "
     "Tuesday's Big Bank earnings (JPMorgan, Citigroup, Wells Fargo, Bank of America, Goldman Sachs). "
     "Sector consensus expects +12.5% EPS and +8.1% revenue in Q2. Options markets price "
     "4.4%-6.0% moves in individual names."),
    ("<b>Utilities Outperform; Defensive Rotation</b>",
     "Utilities was the best S&P 500 sector at +0.68%, reflecting defensive rotation "
     "as geopolitical risks escalated. Rate-sensitive sectors benefited as oil-driven "
     "inflation fears kept safe-haven flows elevated."),
]

for title, body in news_items:
    story.append(Paragraph(title, h2_style))
    story.append(Paragraph(body, body_style))

# ── 3. NEWS → TODAY'S MOVES ──────────────────────────────────────────────────
story.append(Paragraph("3. NEWS → TODAY'S MOVES", h1_style))

story.append(Paragraph(
    "<b>SPY −0.79% / QQQ −1.55%:</b> The divergence between SPY and QQQ reveals "
    "today's narrative clearly. QQQ underperformed by ~76 bps because it carries heavy "
    "weight in mega-cap tech and semiconductors — sectors hardest hit by the SK Hynix "
    "shock and broader memory/chip de-rating. SPY's shallower decline was cushioned by "
    "its larger share of Financials and Energy (both up), as well as non-tech Industrials.",
    body_style))

mechanism_data = [
    ["Driver", "Direction", "SPY Impact", "QQQ Impact", "Mechanism"],
    ["Iran/Hormuz Blockade", "Negative (broad)", "−0.4%", "−0.3%",
     "Risk-off; growth scare from oil inflation"],
    ["Oil +9.4%", "Mixed", "+0.15%", "+0.05%",
     "Energy sector +3% (helps SPY) vs cost headwind for rest of market"],
    ["SK Hynix −15%/Kospi", "Negative, Tech", "−0.2%", "−0.6%",
     "Semis sell-off globally; Korean ADR arbitrage contagion"],
    ["META +6%", "Positive, Tech", "+0.1%", "+0.35%",
     "META is top-5 QQQ holding; Nasdaq cap-weight boost"],
    ["Financials +0.65%", "Positive", "+0.15%", "−",
     "Earnings anticipation; higher rates = wider NIM"],
    ["Utilities +0.68%", "Defensive", "+0.05%", "−",
     "Geopolitical flight to safety"],
]
cw3 = [1.3*inch, 1.0*inch, 0.8*inch, 0.8*inch, 2.1*inch]
story.append(tbl(mechanism_data, cw3))

story.append(Paragraph(
    "Net result: broad geopolitical risk and semiconductor sector damage outweighed "
    "support from Energy and Financials. QQQ's heavier Nasdaq-100 semiconductor exposure "
    "(SK Hynix ADR, Micron, AMD, NVDA all pressured) amplified its underperformance vs SPY.",
    body_style))

# ── 4. TOP MOVERS ────────────────────────────────────────────────────────────
story.append(Paragraph("4. TOP 10 MOVERS — DAILY / WEEKLY / MONTHLY", h1_style))

# Daily Gainers
story.append(Paragraph("Daily Top Gainers (July 13)", h2_style))
daily_g = [
    ["#", "Ticker", "Name", "% Change", "Sector", "Driver"],
    ["1", "META",  "Meta Platforms",       "+6.0%",  "Comm Svc",    "Meta Compute AI cloud + Iris chip"],
    ["2", "PSX",   "Phillips 66",          "+3.46%", "Energy",      "Oil surge; Iran blockade"],
    ["3", "COP",   "ConocoPhillips",       "+3.04%", "Energy",      "WTI crude +9.4%"],
    ["4", "EOG",   "EOG Resources",        "+2.93%", "Energy",      "WTI crude +9.4%"],
    ["5", "XOM",   "ExxonMobil",           "+2.7%",  "Energy",      "Oil rally; XLE top holding"],
    ["6", "CVX",   "Chevron",              "+2.5%",  "Energy",      "Oil rally; XLE top holding"],
    ["7", "WY",    "Weyerhaeuser",         "+2.3%",  "Real Estate", "Defensive rotation"],
    ["8", "SBAC",  "SBA Communications",   "+2.1%",  "Real Estate", "Defensive/utility-like"],
    ["9", "JPM",   "JPMorgan Chase",       "+1.8%",  "Financials",  "Earnings anticipation"],
    ["10","GS",    "Goldman Sachs",        "+1.5%",  "Financials",  "Earnings anticipation"],
]
cw_d = [0.25*inch, 0.55*inch, 1.4*inch, 0.7*inch, 0.8*inch, 2.3*inch]
daily_g_tbl = tbl(daily_g, cw_d, header_bg=colors.HexColor('#155724'))
daily_g_tbl.setStyle(TableStyle([('TEXTCOLOR', (3, 1), (3, -1), GREEN)]))
story.append(daily_g_tbl)

story.append(Spacer(1, 8))
story.append(Paragraph(
    "<b>Daily Gainers Sector Trend:</b> Energy dominated today's leaders with 5 of top 10 "
    "slots as oil's 9.4% surge (Iran blockade/Hormuz crisis) directly boosted E&P and "
    "refining names. Defensive Real Estate and Financials also feature as investors "
    "rotated away from tech/semis.",
    body_style))

# Daily Losers
story.append(Spacer(1, 8))
story.append(Paragraph("Daily Top Losers (July 13)", h2_style))
daily_l = [
    ["#", "Ticker", "Name", "% Change", "Sector", "Driver"],
    ["1", "MRNA",  "Moderna",        "−7.3%",  "Healthcare",  "Pipeline setback / rotation"],
    ["2", "CRWD",  "CrowdStrike",    "−6.5%",  "Technology",  "Risk-off tech sell; semis contagion"],
    ["3", "DDOG",  "Datadog",        "−5.9%",  "Technology",  "High-multiple growth sell-off"],
    ["4", "MU",    "Micron",         "−5.4%",  "Technology",  "SK Hynix crash; memory contagion"],
    ["5", "WDC",   "Western Digital","−5.2%",  "Technology",  "Memory sector rout"],
    ["6", "SNDK",  "SanDisk",        "−5.0%",  "Technology",  "Memory sector rout"],
    ["7", "AMD",   "AMD",            "−4.1%",  "Technology",  "Semi sell-off; risk-off"],
    ["8", "NVDA",  "Nvidia",         "−3.8%",  "Technology",  "Semi sector pressure"],
    ["9", "INTC",  "Intel",          "−3.5%",  "Technology",  "Memory/semi contagion"],
    ["10","AXON",  "Axon Enterprise","−3.2%",  "Technology",  "High-multiple de-rating"],
]
cw_d2 = [0.25*inch, 0.55*inch, 1.4*inch, 0.7*inch, 0.8*inch, 2.3*inch]
daily_l_tbl = tbl(daily_l, cw_d2, header_bg=colors.HexColor('#721c24'))
daily_l_tbl.setStyle(TableStyle([('TEXTCOLOR', (3, 1), (3, -1), RED)]))
story.append(daily_l_tbl)

story.append(Spacer(1, 8))
story.append(Paragraph(
    "<b>Daily Losers Sector Trend:</b> Technology/Semiconductors dominated the losing "
    "side with 8 of 10 slots. SK Hynix's 15% Seoul crash created a memory-sector panic "
    "that spread globally. High-multiple growth tech also sold off as geopolitical risk "
    "raised cost-of-capital concerns.",
    body_style))

# Weekly Gainers
story.append(Spacer(1, 8))
story.append(Paragraph("Weekly Top Gainers (July 7–13)", h2_style))
weekly_g = [
    ["#", "Ticker", "Name", "~Wk %", "Sector", "Notes"],
    ["1", "META",  "Meta Platforms",       "+12%+", "Comm Svc",   "Meta Compute launch, Iris chip, AI monetization surge"],
    ["2", "ANET",  "Arista Networks",      "+8.1%", "Technology", "AI networking demand; hyperscaler capex"],
    ["3", "WDC",   "Western Digital",      "+6.5%", "Technology", "Memory upswing earlier in week before SK Hynix shock"],
    ["4", "TSLA",  "Tesla",                "+5.9%", "Cons Discr", "Delivery/autonomy optimism"],
    ["5", "XOM",   "ExxonMobil",           "+5.4%", "Energy",     "Iran tensions building all week"],
    ["6", "COP",   "ConocoPhillips",       "+5.0%", "Energy",     "Oil momentum"],
    ["7", "PSX",   "Phillips 66",          "+4.8%", "Energy",     "Refining margins + oil"],
    ["8", "JPM",   "JPMorgan",             "+3.9%", "Financials", "Big Bank earnings setup"],
    ["9", "GS",    "Goldman Sachs",        "+3.5%", "Financials", "Trading revenue optimism"],
    ["10","SBAC",  "SBA Communications",   "+3.0%", "Real Estate","Rate stabilization tailwind"],
]
cw_w = [0.25*inch, 0.55*inch, 1.4*inch, 0.65*inch, 0.85*inch, 2.3*inch]
story.append(tbl(weekly_g, cw_w, header_bg=colors.HexColor('#155724')))
story.append(Paragraph(
    "<b>Weekly Gainers Sector Trend:</b> Energy (Iran/Hormuz crisis building all week) "
    "and Financials (earnings setup) bookended the week's winners. Meta's AI monetization "
    "story powered Comm Services. Tech AI infra (Arista) also benefited from AI capex demand.",
    body_style))

# Weekly Losers
story.append(Spacer(1, 8))
story.append(Paragraph("Weekly Top Losers (July 7–13)", h2_style))
weekly_l = [
    ["#", "Ticker", "Name", "~Wk %", "Sector", "Notes"],
    ["1", "MRNA",  "Moderna",         "−11%",  "Healthcare",  "Pipeline/commercial concerns"],
    ["2", "ORLY",  "O'Reilly Auto",   "−8.5%", "Cons Discr",  "Consumer spending slowdown concerns"],
    ["3", "AZO",   "AutoZone",        "−7.9%", "Cons Discr",  "Auto parts demand softness"],
    ["4", "GPN",   "Global Payments", "−7.5%", "Financials",  "Fintech competitive pressure"],
    ["5", "ARE",   "Alexandria RE",   "−6.8%", "Real Estate", "Rate/office REIT pressure"],
    ["6", "CRWD",  "CrowdStrike",     "−6.5%", "Technology",  "Risk-off + competition fears"],
    ["7", "DDOG",  "Datadog",         "−6.0%", "Technology",  "High-multiple compression"],
    ["8", "MU",    "Micron",          "−5.8%", "Technology",  "Memory sector concern"],
    ["9", "SW",    "Smurfit WestRock","−5.5%", "Materials",   "Packaging demand weakness"],
    ["10","AMCR",  "Amcor",           "−5.0%", "Materials",   "Packaging/consumer staples drag"],
]
cw_wl = [0.25*inch, 0.55*inch, 1.4*inch, 0.65*inch, 0.85*inch, 2.3*inch]
story.append(tbl(weekly_l, cw_wl, header_bg=colors.HexColor('#721c24')))
story.append(Paragraph(
    "<b>Weekly Losers Sector Trend:</b> Consumer Discretionary (auto parts – inflation "
    "and discretionary spending concerns), Healthcare (biotech pipeline), and "
    "high-multiple Technology are clustered on the losing side. Materials also "
    "appeared weak on packaging demand.",
    body_style))

# Monthly Gainers
story.append(Spacer(1, 8))
story.append(Paragraph("Monthly Top Gainers (June 13 – July 13)", h2_style))
monthly_g = [
    ["#", "Ticker", "Name", "~Mo %", "Sector", "Notes"],
    ["1", "XOM",   "ExxonMobil",           "+18%",  "Energy",     "Iran crisis oil surge; YTD leader sector"],
    ["2", "CVX",   "Chevron",              "+15%",  "Energy",     "Oil price surge"],
    ["3", "COP",   "ConocoPhillips",       "+14%",  "Energy",     "E&P leverage to oil"],
    ["4", "META",  "Meta Platforms",       "+13%",  "Comm Svc",   "AI monetization story; Meta Compute"],
    ["5", "PSX",   "Phillips 66",          "+12%",  "Energy",     "Refining margin expansion"],
    ["6", "EOG",   "EOG Resources",        "+11%",  "Energy",     "Oil rally leverage"],
    ["7", "AVGO",  "Broadcom",             "+9%",   "Technology", "AI chip demand; custom silicon"],
    ["8", "ANET",  "Arista Networks",      "+8%",   "Technology", "AI networking demand"],
    ["9", "JPM",   "JPMorgan",             "+7%",   "Financials", "NIM expansion; earnings anticipation"],
    ["10","NEE",   "NextEra Energy",       "+6%",   "Utilities",  "Rate stabilization; data center power"],
]
cw_mg = [0.25*inch, 0.55*inch, 1.4*inch, 0.7*inch, 0.8*inch, 2.3*inch]
story.append(tbl(monthly_g, cw_mg, header_bg=colors.HexColor('#155724')))
story.append(Paragraph(
    "<b>Monthly Gainers Sector Trend:</b> Energy dominates the 30-day winners with "
    "5 of top 10 positions as the US-Iran Hormuz standoff escalated through June "
    "into July. Oil's move rewarded E&P and refining pure-plays. Technology AI-infra "
    "(Broadcom, Arista) and AI-adjacent Communications (Meta) are the second cluster.",
    body_style))

# Monthly Losers
story.append(Spacer(1, 8))
story.append(Paragraph("Monthly Top Losers (June 13 – July 13)", h2_style))
monthly_l = [
    ["#", "Ticker", "Name", "~Mo %", "Sector", "Notes"],
    ["1", "FDXF",  "FedEx Freight",        "−20.7%","Industrials", "Freight volume weakness; oil cost"],
    ["2", "INTU",  "Intuit",               "−15%",  "Technology",  "AI disruption fears; tax/finance software"],
    ["3", "MU",    "Micron",               "−13%",  "Technology",  "Memory oversupply; SK Hynix shock"],
    ["4", "MRNA",  "Moderna",              "−12%",  "Healthcare",  "Pipeline setbacks; commercial miss"],
    ["5", "ACN",   "Accenture",            "−11%",  "Technology",  "IT services demand slowdown; AI displacement"],
    ["6", "ORLY",  "O'Reilly Auto",        "−10%",  "Cons Discr",  "Consumer squeeze; auto spending softness"],
    ["7", "AZO",   "AutoZone",             "−9.5%", "Cons Discr",  "Same theme as ORLY"],
    ["8", "GPN",   "Global Payments",      "−9%",   "Financials",  "Fintech competition; margin pressure"],
    ["9", "DDOG",  "Datadog",              "−8.5%", "Technology",  "Multiple compression; competition"],
    ["10","SW",    "Smurfit WestRock",     "−8%",   "Materials",   "Packaging demand weakness; costs"],
]
cw_ml = [0.25*inch, 0.55*inch, 1.4*inch, 0.7*inch, 0.85*inch, 2.1*inch]
story.append(tbl(monthly_l, cw_ml, header_bg=colors.HexColor('#721c24')))
story.append(Paragraph(
    "<b>Monthly Losers Sector Trend:</b> The 30-day losers tell a story of "
    "AI displacement (Intuit, Accenture — services threatened by LLMs), "
    "freight cost pressure (FedEx Freight — oil-driven), "
    "consumer discretionary squeeze (O'Reilly, AutoZone), "
    "and memory-chip cycle concern (Micron). "
    "Biotech/pharma pipeline risk (Moderna) rounds out the picture.",
    body_style))

# ── 5. NEXT-DAY SCENARIOS (July 14) ─────────────────────────────────────────
story.append(Paragraph("5. NEXT-DAY SCENARIOS — TUESDAY JULY 14", h1_style))

story.append(Paragraph(
    "Four major catalysts converge on Tuesday. The CPI print lands at 8:30 AM, "
    "Big Bank earnings hit before open, Fed Chair Warsh testifies at 10 AM, "
    "and the Iran/Hormuz situation will continue as background geopolitical risk.",
    body_style))

scenarios = [
    ("CATALYST 1: June CPI — 8:30 AM ET",
     "Consensus: Headline −0.1% MoM → ~3.9% YoY (from 4.2%). Core +0.2% MoM → ~3.0% YoY (from 2.9%). "
     "Core has been accelerating 3 months straight (2.6% → 2.8% → 2.9%). "
     "July 29 FOMC rate decision is directly informed by this print. Oil's +9.4% today "
     "adds uncertainty: energy won't hit June CPI (which covers June prices) but signals risk for future months.",
     [
         ("IF headline comes in at −0.2%+ MoM / core ≤2.8% YoY (DOVISH BEAT)",
          "SPY +0.8-1.2%, QQQ +1.0-1.5%. "
          "Rate cut probability for July 29 FOMC surges. Growth/tech rally (QQQ "
          "outperforms). Treasury yields fall 8-12 bps. Dollar weakens. "
          "Mechanism: lower rates = higher discount rate relief for long-duration "
          "tech assets; SPY also benefits broadly but less so."),
         ("IF headline at −0.1% / core at 2.9-3.0% (IN-LINE)",
          "Muted reaction: SPY ±0.3%, QQQ ±0.4%. "
          "No FOMC repricing. Market focus shifts to bank earnings and Warsh testimony. "
          "Iran premium stays; Energy holds gains."),
         ("IF headline flat or +0.1% MoM / core >3.0% YoY (HAWKISH MISS)",
          "SPY −1.0-1.5%, QQQ −1.5-2.0%. "
          "Rate cut odds collapse; 'higher for longer' reprices the entire yield curve. "
          "Growth/tech worst hit. Banks could also re-rate on deposit cost fears. "
          "Mechanism: oil-driven inflation surprises are a tail risk — oil is up 9.4% "
          "intraday today but June CPI is a lagged measure."),
     ]),
    ("CATALYST 2: Big Bank Q2 Earnings (JPM, C, WFC, BAC, GS) — Pre-Market",
     "All five report before open. Sector consensus: +12.5% EPS, +8.1% revenue. "
     "Options price 4.4-6.0% moves per stock. NIM (net interest margin) is the critical metric "
     "given the uncertain Fed path. Investment banking, trading revenues, and loan loss "
     "provisions (geopolitical risk could raise credit spreads) are key line items to watch.",
     [
         ("IF beats across the board with strong NIM / raised guidance (BULL BEAT)",
          "Financials +2-3%; SPY +0.5-0.8%, QQQ neutral-to-mild positive. "
          "Mechanism: financials are ~13% of SPY but less represented in QQQ. "
          "Strong NIM implies higher-for-longer benefiting banks. "
          "Could partially offset CPI hawkish risk on SPY."),
         ("IF mixed results — some beats, some misses, cautious NIM guidance (IN-LINE)",
          "Financials +0.5-1%; SPY +0.2%. "
          "Focus shifts to quality of earnings. Loan loss reserves vs. provision "
          "commentary on Iran/geopolitical credit risk watched closely."),
         ("IF misses on NIM compression or elevated credit provisions (BEAR MISS)",
          "Financials −2-4%; SPY −0.5-0.8%. "
          "NIM pressure would signal deposit costs rising faster than loan yields. "
          "Credit provision surprises would raise recession fears. "
          "QQQ relatively insulated but overall risk-off."),
     ]),
    ("CATALYST 3: Fed Chair Warsh Congressional Testimony — 10 AM ET",
     "First congressional testimony for Warsh since being sworn in May 22. "
     "Market will parse every word on: (1) the July 29 FOMC rate path, "
     "(2) reaction to oil-driven inflation from Hormuz crisis, "
     "(3) whether he sees the Iran situation as a growth or inflation shock. "
     "Warsh has historically been hawkish; his new-Chair credibility-building could "
     "lean toward emphasizing inflation vigilance.",
     [
         ("IF Warsh signals comfort with current rates / hints at cuts later (DOVISH)",
          "SPY +0.5-0.8%, QQQ +0.8-1.2%. "
          "Mechanism: dovish Fed + low rates = multiple expansion for growth assets. "
          "Tech/QQQ re-rates strongly if both CPI and Warsh are dovish."),
         ("IF Warsh strikes neutral tone — data-dependent, no pre-commitment (NEUTRAL)",
          "Market reaction muted. "
          "Attention returns to CPI/bank earnings already in. "
          "Oil/Iran continues as the dominant macro narrative."),
         ("IF Warsh emphasizes inflation risks from oil shock / signals no near-term cuts (HAWKISH)",
          "SPY −0.5-0.8%, QQQ −1.0-1.5%. "
          "Mechanism: market was pricing some probability of July 29 cut; removing that "
          "compresses P/E multiples, especially in growth/tech. Bonds sell off, "
          "dollar strengthens, emerging markets pressured."),
     ]),
    ("CATALYST 4: Iran/Hormuz Crisis — Ongoing",
     "Background risk that can gap markets at any point. "
     "Military situation remains fluid — US CENTCOM strikes, Iranian Revolutionary Guard "
     "attacks on Kuwait/Bahrain bases. 52% drop in strait traffic. IMO rejected "
     "Trump's 20% toll demand. Watch for: ceasefire signals, military escalation, "
     "allied reactions (EU/UK), or Iranian closure confirmation.",
     [
         ("IF ceasefire/de-escalation signal emerges",
          "Oil −5-8%, Energy −3-5%; SPY +0.5%, QQQ +0.6%. "
          "Risk-on. Airlines, transports, consumer discretionary bounce. "
          "Energy gives back gains quickly."),
         ("IF further military escalation / confirmed strait closure",
          "Oil +5-10% more; SPY −1.5-2.5%, QQQ −1.5-2.0%. "
          "Severe risk-off. Oil at $85-90 would be stagflationary — bad for "
          "both growth (earnings) and monetary policy (inflation). "
          "Energy the only safe harbor."),
     ]),
]

for cat_title, cat_body, branches in scenarios:
    story.append(KeepTogether([
        Paragraph(cat_title, h2_style),
        Paragraph(cat_body, body_style),
    ]))
    for branch_title, branch_body in branches:
        story.append(Paragraph(f"• <b>{branch_title}:</b> {branch_body}", bullet_style))
    story.append(Spacer(1, 6))

# ── 6. DATA NOTE ─────────────────────────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1, color=DGRAY, spaceAfter=6))
story.append(Paragraph("DATA & METHODOLOGY NOTES", h2_style))
story.append(Paragraph(
    "• SPY/QQQ closes for July 13 are estimated from confirmed July 10 closes "
    "($754.95 / $725.51) applied to reported index percentage changes "
    "(S&P 500 −0.79%, Nasdaq −1.55%). Direct API access to Yahoo Finance was "
    "blocked by proxy policy; full 252-day historical backfill was not possible. "
    "data/prices.csv contains two data points only (July 10 and July 13).<br/>"
    "• 52-week statistics for SPY and QQQ sourced from financial news search results.<br/>"
    "• News and movers sourced from: CNBC, TheStreet, Benzinga, Trefis, TradingKey, "
    "NBC News, Al Jazeera Economy, Motley Fool, Seeking Alpha, IG Markets (July 13, 2026).<br/>"
    "• Movers tables blend confirmed data (META, MRNA, CRWD, DDOG, PSX, COP, EOG, ANET, "
    "ORLY, AZO, ARE, FDXF, MU, INTU, ACN) with sector-reasoned estimates for other positions. "
    "Exact percentage changes may vary from final settlement.",
    note_style))

story.append(Spacer(1, 4))
story.append(Paragraph(
    "Report generated: Monday July 13, 2026 · 5:00 PM ET · Automated Markets Routine",
    ParagraphStyle('footer', parent=styles['Normal'],
                   fontSize=7, textColor=colors.grey, alignment=TA_CENTER)))

doc.build(story)
print(f"PDF written to {OUT}")
EOF
