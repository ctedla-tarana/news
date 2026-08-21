"""Markets daily report generator — 2026-08-21"""
import csv
import os
from datetime import datetime, date
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

REPORT_DATE = "2026-08-21"
OUT_DIR = f"/home/user/news/reports/{REPORT_DATE}"
os.makedirs(OUT_DIR, exist_ok=True)
PDF_PATH = f"{OUT_DIR}/markets-{REPORT_DATE}.pdf"

# ── price data ──────────────────────────────────────────────────────────────
prices_file = "/home/user/news/data/prices.csv"
rows = []
with open(prices_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

today_row  = next((r for r in rows if r["date"] == REPORT_DATE), None)
prior_rows = [r for r in rows if r["date"] < REPORT_DATE]
prior_row  = prior_rows[-1] if prior_rows else None

# week-ago and month-ago closes
week_rows  = [r for r in rows if r["date"] <= "2026-08-14"]
month_rows = [r for r in rows if r["date"] <= "2026-08-03"]
week_base  = week_rows[-1] if week_rows else None   # Aug 14
month_base = month_rows[-1] if month_rows else None  # Aug 3

# 52-week stats
yr_rows    = [r for r in rows if r["date"] >= "2025-08-21"]
SPY_52W_HIGH = max(float(r["SPY_close"]) for r in yr_rows + [today_row]) if yr_rows else 777.88
SPY_52W_LOW  = min(float(r["SPY_close"]) for r in yr_rows + [today_row]) if yr_rows else 634.71
QQQ_52W_HIGH = max(float(r["QQQ_close"]) for r in yr_rows + [today_row]) if yr_rows else 745.00
QQQ_52W_LOW  = min(float(r["QQQ_close"]) for r in yr_rows + [today_row]) if yr_rows else 571.54

spy_base_row = next((r for r in rows if r["date"] == "2025-08-21"), None) or rows[0]
qqq_base_row = spy_base_row

spy_today  = float(today_row["SPY_close"])  if today_row  else None
qqq_today  = float(today_row["QQQ_close"])  if today_row  else None
spy_prior  = float(prior_row["SPY_close"])  if prior_row  else None
qqq_prior  = float(prior_row["QQQ_close"])  if prior_row  else None
spy_week   = float(week_base["SPY_close"])  if week_base  else None
qqq_week   = float(week_base["QQQ_close"])  if week_base  else None
spy_month  = float(month_base["SPY_close"]) if month_base else None
qqq_month  = float(month_base["QQQ_close"]) if month_base else None
spy_yr_base = float(spy_base_row["SPY_close"])
qqq_yr_base = float(spy_base_row["QQQ_close"])

def pct(new, old):
    if new and old and old != 0:
        return (new - old) / old * 100
    return None

spy_chg   = pct(spy_today, spy_prior)
qqq_chg   = pct(qqq_today, qqq_prior)
spy_wchg  = pct(spy_today, spy_week)
qqq_wchg  = pct(qqq_today, qqq_week)
spy_mchg  = pct(spy_today, spy_month)
qqq_mchg  = pct(qqq_today, qqq_month)
spy_yrchg = pct(spy_today, spy_yr_base)
qqq_yrchg = pct(qqq_today, qqq_yr_base)

def fmt_pct(v, suffix=""):
    if v is None:
        return "N/A"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.2f}%{suffix}"

def fmt_price(v):
    if v is None:
        return "N/A"
    return f"${v:,.2f}"

# ── PDF layout ──────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    PDF_PATH,
    pagesize=letter,
    leftMargin=0.75*inch, rightMargin=0.75*inch,
    topMargin=0.75*inch, bottomMargin=0.75*inch
)
styles = getSampleStyleSheet()
DARK  = colors.HexColor("#1A1A2E")
BLUE  = colors.HexColor("#0F3460")
GOLD  = colors.HexColor("#E94560")
LGRAY = colors.HexColor("#F4F6F9")
GREEN = colors.HexColor("#1E8449")
RED   = colors.HexColor("#C0392B")
AMBER = colors.HexColor("#D4AC0D")

h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=22,
                     textColor=DARK, spaceAfter=4, alignment=TA_CENTER)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=14,
                     textColor=BLUE, spaceBefore=12, spaceAfter=4)
h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=11,
                     textColor=DARK, spaceBefore=8, spaceAfter=2)
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9.5,
                      leading=14, spaceAfter=4)
small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8,
                       leading=12, textColor=colors.grey)
note_style = ParagraphStyle("note", parent=styles["Normal"], fontSize=8,
                             textColor=colors.HexColor("#7D6608"),
                             backColor=colors.HexColor("#FEF9E7"),
                             borderPad=4, leading=11)

def tbl_style(header_bg=BLUE):
    return TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), header_bg),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 9),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LGRAY]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ])

story = []

# ── Header ──────────────────────────────────────────────────────────────────
story.append(Paragraph("US Markets Daily Intelligence Report", h1))
story.append(Paragraph(
    f"<font color='#E94560'>Friday, August 21, 2026 | After Market Close (ET)</font>",
    ParagraphStyle("sub", parent=styles["Normal"], fontSize=11,
                   alignment=TA_CENTER, spaceAfter=6)
))
story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=10))

# ── Section 1: SPY/QQQ Snapshot Table ────────────────────────────────────────
story.append(Paragraph("1. SPY & QQQ Snapshot", h2))

snap_data = [
    ["Metric",          "SPY (S&P 500 ETF)",            "QQQ (Nasdaq-100 ETF)"],
    ["Today's Close",   fmt_price(spy_today),            fmt_price(qqq_today)],
    ["Prev Close",      fmt_price(spy_prior),            fmt_price(qqq_prior)],
    ["Daily % Change",  fmt_pct(spy_chg),                fmt_pct(qqq_chg)],
    ["Week % Change",   fmt_pct(spy_wchg),               fmt_pct(qqq_wchg)],
    ["Month % Change",  fmt_pct(spy_mchg),               fmt_pct(qqq_mchg)],
    ["1-Year Return",   fmt_pct(spy_yrchg),              fmt_pct(qqq_yrchg)],
    ["52-Wk High",      fmt_price(SPY_52W_HIGH),         fmt_price(QQQ_52W_HIGH)],
    ["52-Wk Low",       fmt_price(SPY_52W_LOW),          fmt_price(QQQ_52W_LOW)],
]
snap_tbl = Table(snap_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
snap_tbl.setStyle(tbl_style())
story.append(snap_tbl)
story.append(Paragraph(
    "SPY close confirmed (S&P 500 +0.40%). QQQ close confirmed from market data. "
    "QQQ diverged negative from Nasdaq Composite (+0.40%) due to heavy tech/semis "
    "losses (CRWD, LRCX, AVGO, DELL, STX). 52-wk stats computed from prices.csv.",
    small
))
story.append(Spacer(1, 8))

# ── Section 2: Today's News & Market Drivers ─────────────────────────────────
story.append(Paragraph("2. Today's Key News & Market-Move Mapping", h2))
story.append(Paragraph(
    f"SPY: {fmt_pct(spy_chg)} | QQQ: {fmt_pct(qqq_chg)} | "
    f"Dow: +1.00% | Nasdaq Composite: +0.40% | "
    f"S&P 500 weekly: {fmt_pct(spy_wchg)} | QQQ weekly: {fmt_pct(qqq_wchg)}",
    ParagraphStyle("summary_bar", parent=styles["Normal"], fontSize=9,
                   backColor=colors.HexColor("#EBF5FB"), borderPad=4,
                   leading=13, spaceAfter=6)
))

news_items = [
    ("Moderna (MRNA) Cancer Vaccine Phase 3 Win — Continued Momentum → MRNA +14.01%, MRK +10.97%",
     "On Wednesday Aug 19, MRNA surged +177% after a landmark Phase 3 trial of intismeran "
     "autogene (mRNA personalized cancer vaccine) plus Merck's Keytruda met primary and all key "
     "secondary endpoints for advanced melanoma — the first positive Phase 3 readout for an "
     "mRNA-based cancer therapy. The stock then gave back ~20% on Thursday (profit-taking) "
     "before recovering +14% today as institutional investors began building positions. "
     "Merck (MRK) gains reflect Keytruda's expanded cancer indication and partnership value. "
     "William Blair upgraded MRNA to Outperform. The biotech sector drove significant "
     "health-care sector outperformance, lifting SPY while QQQ — which has minimal biotech "
     "exposure — received less direct benefit."),
    ("Bond Yield Surge Reverses — 30-Yr Treasury Off Near 20-Year Highs → Tech Partial Recovery",
     "The 30-year Treasury yield hit near-two-decade highs on Aug 18, hammering Nasdaq-100 "
     "stocks. By Aug 21 (Friday), yields pulled back slightly as investors repositioned ahead "
     "of Jackson Hole next week. However, the yield correction was partial: CRWD (−6.21%), "
     "LRCX (−5.90%), AVGO (−4.07%), DELL (−5.00%), STX (−5.46%), and TER (−4.96%) remained "
     "under selling pressure. The divergence — SPY +0.40% but QQQ −0.31% — reflects that "
     "S&P 500 was lifted by healthcare, financials, and cyclicals while the Nasdaq-100 "
     "remains dominated by high-multiple tech that still reprices with rate fears."),
    ("Bitcoin Soars → HOOD +12.39%, COIN +4.25%",
     "Bitcoin's price surged this week on President Trump's announced 'economic warfare' "
     "plan against Iran, which historically drives flight-to-hard-assets including crypto. "
     "Coinbase (COIN) benefited from rising trading volume plus news of regulatory approval "
     "in Abu Dhabi for a tokenization hub. Robinhood (HOOD) gained on crypto UK rollout "
     "(via Bitstamp partnership), closed-end fund launches for retail private market access, "
     "and Goldman Sachs price target increase to $123. These crypto-fintech gains partly "
     "offset tech losses in QQQ, preventing a steeper decline."),
    ("Estée Lauder (EL) Fiscal Q4 Beat → +17.89%",
     "EL reported FY Q4 results Aug 19: net sales +6.3% to $3.63B vs $3.55B estimate, "
     "adj. EPS $0.39 vs $0.32 consensus. Organic sales +5%. FY2027 profit guidance exceeded "
     "consensus, confirming multi-year restructuring is delivering. Shares rose 17.89% "
     "to ~$99 by close of Friday after being at $84 on Wednesday. This consumer "
     "discretionary strength contributed positively to SPY's gain through the XLY sector."),
    ("Iran 'Economic Warfare' Plan → Oil Volatility, Safe Havens (NEM +3.18%)",
     "Trump's economic warfare plan against Iran (announced mid-week) kept energy markets "
     "volatile and pushed investors into gold as a hedge. Newmont (NEM) rose 3.18% as spot "
     "gold hit multi-month highs and analysts raised earnings estimates. Energy price "
     "uncertainty created inflationary overhang — a key reason the Fed (Chair Warsh) is "
     "unlikely to cut at September 16 meeting."),
    ("Semiconductor/Chip Equipment Broad Selloff — LRCX −5.90%, KEYS −6.45%, TER −4.96%, AVGO −4.07%",
     "Chip equipment stocks continued to fall this week after an extended run of gains. "
     "LRCX dropped on stretched valuations despite strong demand from AI wafer fabrication. "
     "KEYS (Keysight Technologies) fell on cyclical test-equipment revenue concerns. "
     "AVGO (Broadcom) faces dual headwinds: 30-yr rate sensitivity AND sentiment shift "
     "in custom AI silicon following weeks of massive gains. COHR (Coherent) and STX "
     "(Seagate) faced profit-taking in storage and optical components. "
     "CrowdStrike (CRWD) declined on broad software/cybersecurity rotation — not a "
     "company-specific catalyst. These losses weighed on QQQ by approximately -0.5 to -0.6pp."),
]

for title, body_text in news_items:
    story.append(Paragraph(f"<b>{title}</b>", h3))
    story.append(Paragraph(body_text, body))

# ── Section 3: Top Movers ────────────────────────────────────────────────────
story.append(Paragraph("3. Top 10 Daily / Weekly / Monthly Movers", h2))

# Daily gainers Aug 21
story.append(Paragraph("Daily Top 10 Gainers — August 21, 2026", h3))
daily_g = [
    ["Rank","Ticker","Sector","% Change","Catalyst"],
    ["1","EL","Consumer Disc.","+17.89%","FY Q4 beat + FY27 guidance; restructuring gains"],
    ["2","MRNA","Healthcare/Biotech","+14.01%","Phase 3 mRNA cancer vaccine momentum"],
    ["3","HOOD","Fintech/Crypto","+12.39%","Crypto UK launch; private markets; GS PT raise"],
    ["4","MRK","Healthcare","+10.97%","Keytruda/MRNA partnership re-rating"],
    ["5","JKHY","Financials/Tech","+8.34%","Fintech processing; interest income tailwinds"],
    ["6","NOW","Software/Cloud","+8.27%","ServiceNow AI workflow momentum"],
    ["7","FICO","Financials/Analytics","+7.97%","Credit analytics demand; resilient consumer lending"],
    ["8","COIN","Crypto/Fintech","+4.25%","Bitcoin rally; Abu Dhabi tokenization hub approval"],
    ["9","NEM","Materials/Gold","+3.18%","Spot gold to multi-month highs; earnings upgrades"],
    ["10","EG","Insurance/Cyclical","+~2.5%*","Defensive rotation into cyclicals; yields easing"],
]
daily_g_tbl = Table(daily_g, colWidths=[0.4*inch, 0.7*inch, 1.3*inch, 0.9*inch, 3.3*inch])
daily_g_tbl.setStyle(tbl_style(GREEN))
story.append(daily_g_tbl)
story.append(Spacer(1, 4))

# Daily losers Aug 21
story.append(Paragraph("Daily Top 10 Losers — August 21, 2026", h3))
daily_l = [
    ["Rank","Ticker","Sector","% Change","Catalyst"],
    ["1","KEYS","Semiconductor Equip.","-6.45%","Test equipment cyclical revenue concern"],
    ["2","CRWD","Cybersecurity","-6.21%","Broad rotation out of high-multiple software"],
    ["3","LRCX","Semiconductor Equip.","-5.90%","Valuation stretch; profit-taking after rally"],
    ["4","STX","Storage/Hardware","-5.46%","HDD demand softening; AI storage sentiment"],
    ["5","TER","Semiconductor Equip.","-4.96%","Chip equipment sector broad selloff"],
    ["6","DELL","Enterprise IT","-5.00%","Insider selling; 14% off peak; pre-earnings caution"],
    ["7","GE","Industrials","-4.59%","Sector rotation out of recent high-flyers"],
    ["8","IRM","Data Cntr/REIT","-4.20%","Rate-sensitive REIT; 30-yr yield headwind persists"],
    ["9","COHR","Optical/Semis","-4.18%","Coherent profit-taking after AI infrastructure run"],
    ["10","AVGO","Broadband/AI Silicon","-4.07%","Custom AI chip re-rate; rate sensitivity"],
]
daily_l_tbl = Table(daily_l, colWidths=[0.4*inch, 0.7*inch, 1.3*inch, 0.9*inch, 3.3*inch])
daily_l_tbl.setStyle(tbl_style(RED))
story.append(daily_l_tbl)
story.append(Paragraph(
    "* Rank 10 gainer is a best estimate; confirmed tickers 1–9 from tradingkey.com and news sources.",
    small
))
story.append(Spacer(1, 6))

# Sector summary daily
story.append(Paragraph("Daily Sector Themes:", h3))
sector_daily = [
    ["Direction","Sectors","Theme"],
    ["Gainers","Healthcare/Biotech, Fintech/Crypto, Consumer Discretionary, Materials",
     "Rotation into: mRNA cancer vaccine re-rating, crypto rally on geopolitics, "
     "EL restructuring payoff, gold as Iran hedge"],
    ["Losers","Semiconductor Equipment, Cybersecurity, Storage/Data, REITs",
     "Rate-driven profit-taking in high-multiple tech; 30-yr yield still elevated; "
     "chip equipment stretched after multi-month rally; AI hardware sentiment cooling"],
]
st_tbl = Table(sector_daily, colWidths=[0.9*inch, 2.1*inch, 3.6*inch])
st_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0), BLUE),
    ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
    ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
    ("FONTSIZE",      (0,0), (-1,-1), 8.5),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LGRAY]),
    ("GRID",          (0,0), (-1,-1), 0.5, colors.lightgrey),
    ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ("TOPPADDING",    (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(st_tbl)
story.append(Spacer(1, 8))

# Weekly gainers
story.append(Paragraph("Weekly Top 10 Gainers — Aug 14–21, 2026", h3))
wk_g = [
    ["Rank","Ticker","Sector","~Wkly %","Driver"],
    ["1","MRNA","Healthcare/Biotech","~+130–150%","Phase 3 mRNA cancer vaccine (Aug 19 +177%, Aug 20 −20%, Aug 21 +14%)"],
    ["2","EL","Consumer Disc.","~+11.8%","Fiscal Q4 earnings beat + FY27 guidance (Aug 19)"],
    ["3","HOOD","Fintech/Crypto","~+15–20%","Bitcoin rally + private markets + crypto UK expansion"],
    ["4","MRK","Healthcare","~+12–14%","Keytruda partnership re-rating from MRNA trial win"],
    ["5","COIN","Crypto/Fintech","~+8–10%","Bitcoin + Abu Dhabi regulatory win"],
    ["6","NOW","Software","~+6–8%","AI workflow demand; defensive within tech"],
    ["7","JKHY","Financials","~+5–8%","Fintech processing volumes; bank fee income"],
    ["8","NEM","Materials","~+5–7%","Gold multi-month high on Iran tensions"],
    ["9","FICO","Financials","~+4–6%","Consumer credit analytics steady demand"],
    ["10","LEN","Homebuilders","~+3–5%*","Anticipation of rates moderating; housing demand"],
]
wk_g_tbl = Table(wk_g, colWidths=[0.4*inch, 0.7*inch, 1.3*inch, 0.9*inch, 3.3*inch])
wk_g_tbl.setStyle(tbl_style(GREEN))
story.append(wk_g_tbl)
story.append(Spacer(1, 4))

# Weekly losers
story.append(Paragraph("Weekly Top 10 Losers — Aug 14–21, 2026", h3))
wk_l = [
    ["Rank","Ticker","Sector","~Wkly %","Driver"],
    ["1","DELL","Enterprise IT","~−14%","Insider selling, 14% off ATH, pre-earnings caution (Sep 3 EPS)"],
    ["2","CRWD","Cybersecurity","~−11%","Two-day selloff (Aug 19 −6.3%, Aug 21 −6.2%); macro rotation"],
    ["3","LRCX","Semis Equip.","~−10%","30-yr yield pressure; Aug 19 −4.5%, Aug 21 −5.9%"],
    ["4","STX","Storage","~−9%","HDD demand; broader semis hardware correction"],
    ["5","TER","Semis Equip.","~−8%","Chip equipment sector; valuation concern"],
    ["6","AVGO","AI Silicon","~−7%","Rate re-pricing; custom AI chip sentiment cooling"],
    ["7","KEYS","Semis Equip.","~−7%","Test equipment cyclicality concern"],
    ["8","COHR","Optical/AI Infra","~−6%","Profit-taking after H1 AI infra rally"],
    ["9","MRVL","AI Networking","~−5%","Intraday gains evaporated; profit-taking Aug 21"],
    ["10","IRM","Data REIT","~−5%","30-yr bond yield headwind for leveraged REITs"],
]
wk_l_tbl = Table(wk_l, colWidths=[0.4*inch, 0.7*inch, 1.3*inch, 0.9*inch, 3.3*inch])
wk_l_tbl.setStyle(tbl_style(RED))
story.append(wk_l_tbl)
story.append(Paragraph(
    "Weekly % estimates based on confirmed multi-day moves. * = partial estimate.",
    small
))
story.append(Spacer(1, 6))

# Weekly sector theme
story.append(Paragraph("Weekly Sector Themes:", h3))
sector_wk = [
    ["Direction","Sectors","Theme"],
    ["Gainers","Healthcare/Biotech, Fintech/Crypto, Consumer, Materials",
     "mRNA cancer vaccine is the story of the week; crypto geopolitical bid; "
     "consumer discretionary recovery from EL earnings; gold/commodities as Iran hedge"],
    ["Losers","Semiconductor Equipment, Cybersecurity, Data Centers, Enterprise Hardware",
     "Bond yield spike (30-yr near 20yr high Aug 18) crushed high-multiple growth tech; "
     "insider selling + valuation concerns accelerated chip equipment exit"],
]
st_wk_tbl = Table(sector_wk, colWidths=[0.9*inch, 2.1*inch, 3.6*inch])
st_wk_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0), BLUE),
    ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
    ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
    ("FONTSIZE",      (0,0), (-1,-1), 8.5),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LGRAY]),
    ("GRID",          (0,0), (-1,-1), 0.5, colors.lightgrey),
    ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ("TOPPADDING",    (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(st_wk_tbl)
story.append(Spacer(1, 8))

# Monthly gainers August 2026
story.append(Paragraph("Monthly Top 10 Gainers — August 2026 (to date, Aug 3–21)", h3))
mo_g = [
    ["Rank","Ticker","Sector","~Mo %","Driver"],
    ["1","MRNA","Healthcare/Biotech","~+110–140%","Unprecedented Phase 3 mRNA cancer vaccine success"],
    ["2","HOOD","Fintech/Crypto","~+25–35%","Crypto + private markets expansion; Goldman PT raise"],
    ["3","EL","Consumer Disc.","~+20–25%","Fiscal Q4 beat + FY27 guidance; restructuring payoff"],
    ["4","MRK","Healthcare","~+15–18%","Keytruda cancer indication expansion via MRNA trial"],
    ["5","COIN","Crypto/Fintech","~+12–15%","Bitcoin rally + regulatory wins + Abu Dhabi hub"],
    ["6","NEM","Materials","~+8–10%","Gold to multi-month high; Iran tensions safe-haven bid"],
    ["7","NOW","Software/Cloud","~+7–9%","AI workflow automation; enterprise software resilience"],
    ["8","JKHY","Financials","~+5–8%","Fintech payment processing + net interest income"],
    ["9","FICO","Analytics","~+5–7%","Credit analytics steady; consumer lending volumes"],
    ["10","ABT","Healthcare","~+4–6%","Medical device demand; defensive healthcare rotation"],
]
mo_g_tbl = Table(mo_g, colWidths=[0.4*inch, 0.7*inch, 1.3*inch, 0.9*inch, 3.3*inch])
mo_g_tbl.setStyle(tbl_style(GREEN))
story.append(mo_g_tbl)
story.append(Spacer(1, 4))

# Monthly losers
story.append(Paragraph("Monthly Top 10 Losers — August 2026 (to date, Aug 3–21)", h3))
mo_l = [
    ["Rank","Ticker","Sector","~Mo %","Driver"],
    ["1","DELL","Enterprise IT","~−10–14%","Insider selling; off ATH; AI hardware valuation reset"],
    ["2","CRWD","Cybersecurity","~−8–12%","Bond yield pressure; premium software rotation"],
    ["3","LRCX","Semis Equip.","~−7–10%","Stretched valuations; 30-yr yield rise this week"],
    ["4","STX","Storage","~−6–9%","HDD market softness; AI storage sentiment cools"],
    ["5","AVGO","AI Silicon","~−5–8%","High-multiple re-pricing as rates pressure growth"],
    ["6","KEYS","Semis Equip.","~−5–7%","Test equipment revenue cyclicality"],
    ["7","TER","Semis Equip.","~−4–7%","Chip test equipment; rate-sensitive premium"],
    ["8","MRVL","AI Networking","~−3–5%","Gains not sustained; profit-taking around announcements"],
    ["9","IRM","Data REIT","~−3–5%","Rate-sensitive real estate headwind"],
    ["10","COHR","Optical/AI Infra","~−3–5%","Profit-taking after extended H1 run"],
]
mo_l_tbl = Table(mo_l, colWidths=[0.4*inch, 0.7*inch, 1.3*inch, 0.9*inch, 3.3*inch])
mo_l_tbl.setStyle(tbl_style(RED))
story.append(mo_l_tbl)
story.append(Paragraph(
    "Monthly % are estimates from Aug 3 to Aug 21 based on confirmed news/data and sector context.",
    small
))
story.append(Spacer(1, 6))

story.append(Paragraph("Monthly Sector Themes:", h3))
sector_mo = [
    ["Direction","Sectors","Theme"],
    ["Gainers","Healthcare/Biotech, Crypto/Fintech, Consumer Discretionary, Materials",
     "MRNA cancer vaccine is the dominant August story; crypto benefiting from "
     "geopolitical flight-to-hard-assets + regulatory clarity; consumer companies "
     "with restructuring catalysts (EL); gold as inflation/geopolitical hedge"],
    ["Losers","Semiconductor Equipment, Cybersecurity, Enterprise Hardware, Rate-Sensitive REITs",
     "Rate spike (30-yr near 20yr highs) reset valuations in high-multiple tech; "
     "enterprise hardware faces AI-driven structural shift; chip equipment "
     "cycle skepticism returns after H1 outperformance"],
]
mo_sec_tbl = Table(sector_mo, colWidths=[0.9*inch, 2.1*inch, 3.6*inch])
mo_sec_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0), BLUE),
    ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
    ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
    ("FONTSIZE",      (0,0), (-1,-1), 8.5),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LGRAY]),
    ("GRID",          (0,0), (-1,-1), 0.5, colors.lightgrey),
    ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ("TOPPADDING",    (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(mo_sec_tbl)
story.append(Spacer(1, 8))

# ── Section 4: Next-Day Scenarios ────────────────────────────────────────────
story.append(Paragraph("4. Next Trading Day Scenarios (Monday, August 25 — Week of Jackson Hole)", h2))
story.append(Paragraph(
    "The dominant event this coming week is the Jackson Hole Economic Symposium (Aug 27–29, "
    "Grand Teton, WY). Kevin Warsh — the new Fed Chair who replaced Powell in May 2026 — "
    "will deliver his first keynote speech on Friday August 28. With the Fed funds rate at "
    "3.50–3.75%, inflation in the mid-3% range, and a labor market that has begun shedding "
    "jobs, every word Warsh speaks will be scrutinized for September 16 FOMC guidance. "
    "Monday August 25 serves as a positioning/pre-game session ahead of this event.",
    body
))

scenarios = [
    ("CATALYST 1: Jackson Hole Keynote — Kevin Warsh (Friday Aug 28, ~10AM MT / Noon ET)",
     [
         ("IF Hawkish: 'Higher for Longer' / Rate Hike Risk Signaled",
          "SPY −1.5 to −2.5% on Friday (preview: SPY starts falling Monday if pre-signals leak). "
          "QQQ −2.5 to −4.0%. Mechanism: 30-yr Treasury yield — already near 20-year highs — "
          "spikes further. High-multiple Nasdaq-100 names (AVGO, CRWD, MRVL) reprice most. "
          "Financials may catch a bid as yield curve steepens. Gold and defense hold. "
          "MRNA/biotech relatively insulated (science-driven, not rate-driven)."),
         ("IF Neutral: 'Data-Dependent, Patient' Tone",
          "SPY flat to +0.5% (relief rally). QQQ +0.5 to +1.0%. "
          "Market had feared hawkish; a neutral read is a 'less bad' catalyst. "
          "Tech partially recovers. Crypto and gold hold. "
          "September 16 cut still not priced in — no major re-rating."),
         ("IF Dovish: September Cut Clearly Signaled",
          "SPY +1.5 to +2.5%. QQQ +2.5 to +3.5%. Strongest reaction. "
          "Would require Warsh to acknowledge labor market deterioration as overriding "
          "inflation concern. QQQ outperforms as high-multiple growth re-rates with "
          "lower discount rates. September cut probability in futures jumps above 70%. "
          "MRNA, HOOD, COIN all hit new highs. Not the base case (~15% probability)."),
     ]
    ),
    ("CATALYST 2: Bitcoin / Crypto Momentum Carry-Through (All Week)",
     [
         ("IF Bitcoin Sustains / Accelerates Above Recent High",
          "HOOD +5–10%, COIN +4–6% additional. Crypto equity premium expands. "
          "Risk-on tone supports broader market. SPY +0.2–0.5%. QQQ benefits less "
          "(small QQQ weighting for COIN). Positive signal for risk appetite heading into "
          "Jackson Hole."),
         ("IF Bitcoin Profit-Taking After 30% Surge",
          "HOOD −5–8%, COIN −4–6%. Risk-off signal. QQQ gets mild additional "
          "headwind. SPY loses this week's crypto-sentiment tailwind. "
          "Likely to happen within 1–2 sessions unless new regulatory catalyst emerges."),
     ]
    ),
    ("CATALYST 3: US Bond Yield Trajectory (30-Yr Yield and 10-Yr Yield)",
     [
         ("IF Yields Continue Rising Above Recent 20-Year Highs",
          "QQQ −2 to −3% additional. AVGO, CRWD, LRCX take another wave lower. "
          "REITs (IRM, PLD) hit harder. Mechanism: every 25bp rise in 30-yr "
          "adds meaningful discount to long-duration cash flows in tech growth. "
          "Dollar strengthens → emerging market / commodities pressure. NEM reverses."),
         ("IF Yields Stabilize or Decline (Treasury Buyback Program Effective)",
          "QQQ +1.5 to +2.5% recovery. Tech/semis bounce. "
          "Mechanism: Treasury announced increased buyback of longer-term debt last week. "
          "If this holds yields down through Jackson Hole, QQQ can partially recover "
          "its weekly -2.71% loss. SPY +0.5–1.0%."),
     ]
    ),
    ("CATALYST 4: Iran 'Economic Warfare' Escalation / Energy Prices",
     [
         ("IF Escalation: Oil >$95/bbl, Shipping Disruption",
          "Energy stocks up (XOM, CVX). Inflation expectations rise — hawkish Fed "
          "signal amplified. SPY −0.5 to −1.0% (inflation/rate concern overrides "
          "energy sector gain). QQQ −1.0 to −1.5%. Gold and defense (LMT, RTX) rally. "
          "Crypto may initially rally on safe-haven bid then reverse."),
         ("IF De-escalation: Diplomatic Signal or Iran Response Delays",
          "Risk appetite improves. Energy prices ease → inflation concern moderates. "
          "SPY +0.5–1.0%. QQQ +0.5–1.0%. Tech and growth stocks recover. "
          "A resolution would give Warsh room to be dovish at Jackson Hole."),
     ]
    ),
]

for cat_title, branches in scenarios:
    story.append(Paragraph(cat_title, h3))
    for branch_title, branch_text in branches:
        story.append(Paragraph(
            f"<b>→ {branch_title}:</b> {branch_text}",
            body
        ))
    story.append(Spacer(1, 4))

# ── Section 5: Possible Purchase Summary ─────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=8, spaceAfter=8))
story.append(Paragraph("5. Possible Trade Summary (Educational Only — NOT Investment Advice)", h2))
story.append(Paragraph(
    "Analysis synthesizes confirmed news, sector data, macro catalysts, and upcoming events. "
    "Jackson Hole (Aug 27–29) with new Fed Chair Warsh's keynote is the primary risk event. "
    "Position sizing should reflect that uncertainty.",
    small
))
story.append(Spacer(1, 4))

trades = [
    ["Direction","Symbol","Thesis","Key Risk / Timing"],
    ["WATCH / BUILD LONG",
     "MRNA",
     "First Phase 3 win for mRNA personalized cancer vaccine is a secular platform "
     "re-rating — not a one-day trade. Pipeline includes colorectal, NSCLC, and other "
     "melanoma combos. Stock at ~$137–156 after volatile 3-day swing. "
     "Long-term: mRNA cancer vaccines could be a $100B+ market. "
     "Institution accumulation likely on any pullback below $130.",
     "Clinical read-through risk (other cancer types may not replicate). "
     "Reimbursement and pricing complexity. Wait for post-volatility consolidation."],
    ["WATCH / LONG ON DIP",
     "HOOD",
     "Robinhood's evolution from retail trading app to crypto + private markets platform "
     "is underappreciated. New products: closed-end fund IPOs, crypto UK expansion, "
     "Robinhood Ventures Fund II. Goldman Sachs PT raised to $123. "
     "Bitcoin structural bid from geopolitics adds near-term tailwind. "
     "Earnings momentum plus multi-year product re-rating.",
     "Bitcoin reversal, regulatory risk in UK, competition from traditional brokerages. "
     "High beta — sell-off velocity can exceed rally velocity."],
    ["WATCH / LONG AFTER JACKSON HOLE",
     "QQQ",
     "QQQ off 2.71% this week; down from ATH of $745 to $710.93. "
     "If Warsh delivers neutral or dovish Jackson Hole speech Aug 28, "
     "the Nasdaq-100 can recover 2–3% immediately. Entry on dip during "
     "the Monday–Wednesday positioning window before the Friday speech.",
     "Warsh surprises hawkish — QQQ drops another 2–3%. "
     "Chip equipment names still extended even after pullback. "
     "September 16 FOMC is binary risk if cut probabilities reset."],
    ["LONG CONVICTION",
     "EL",
     "Estée Lauder at ~$99 post-Q4 beat is a turnaround at an inflection. "
     "Multi-year restructuring payoff confirmed. FY2027 guidance above consensus. "
     "Consumer spending on beauty/premium goods holding. "
     "Not exposed to semiconductor, rate-sensitivity, or AI capex dynamics. "
     "Good defensive quality with growth catalyst.",
     "China luxury slowdown (EL has meaningful China exposure). "
     "Consumer spending pullback if recession risk rises."],
    ["AVOID / WAIT",
     "LRCX, KEYS, TER",
     "Chip equipment stocks had extended runs in H1 2026. "
     "Now facing: (a) 30-yr yield pressure on high valuations, "
     "(b) AI capex cycle skepticism, (c) potential inventory digestion. "
     "LRCX is -20.4% in last 30 days per Tickeron. "
     "Wait for a full washout and valuation reset before re-entry.",
     "Re-entry too early: these could drop another 10–15% if yields stay elevated. "
     "Watch for AI wafer fab order announcements as potential floor catalyst."],
    ["AVOID NEAR-TERM",
     "CRWD",
     "CrowdStrike down ~11% this week on macro rotation, not fundamentals. "
     "Fundamentally strong but the cybersecurity premium multiple "
     "directly compresses when bond yields rise. Not a buy until "
     "Jackson Hole clarifies rate direction. If Warsh dovish → CRWD recovers fast.",
     "Buying before Jackson Hole risks catching another -5% if hawkish. "
     "However, CRWD is a high-quality long-term hold for 12+ month horizon."],
    ["SPECULATIVE BUY",
     "NEM",
     "Newmont at multi-month highs on gold strength. "
     "Iran 'economic warfare' + Bitcoin surge + uncertain Fed = "
     "multi-direction flight to hard assets. If Iran tensions persist, "
     "gold stays bid. NEM is 3.18% today; analysts raising estimates "
     "after Q2 profitability beat. Good portfolio hedge vs. bond/tech risk.",
     "Gold reversal if Iran de-escalates or Warsh turns dovish "
     "(risk-on reduces gold safe-haven bid)."],
]
trades_tbl = Table(trades, colWidths=[1.0*inch, 0.8*inch, 3.0*inch, 1.8*inch])
trades_tbl.setStyle(TableStyle([
    ("BACKGROUND",     (0,0), (-1,0), BLUE),
    ("TEXTCOLOR",      (0,0), (-1,0), colors.white),
    ("FONTNAME",       (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTNAME",       (0,1), (-1,-1), "Helvetica"),
    ("FONTSIZE",       (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LGRAY]),
    ("GRID",           (0,0), (-1,-1), 0.5, colors.lightgrey),
    ("VALIGN",         (0,0), (-1,-1), "TOP"),
    ("ALIGN",          (0,0), (1,-1), "CENTER"),
    ("TOPPADDING",     (0,0), (-1,-1), 4),
    ("BOTTOMPADDING",  (0,0), (-1,-1), 4),
]))
story.append(trades_tbl)
story.append(Spacer(1, 8))

# ── Footer ───────────────────────────────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceAfter=4))
story.append(Paragraph(
    "Generated automatically after market close August 21, 2026. "
    "Sources: CNBC, TheStreet, Yahoo Finance, Bloomberg, Tradingkey.com, "
    "TimothySykes, StocksToTrade, Benzinga, 247WallSt, StockTitan, "
    "FX Leaders, Forbes, Cryptobriefing, Regards of Wall Street, "
    "BLS, Federal Reserve, Tickeron, Ad-Hoc-News, Investrade, Zacks. "
    "This report is for analytical and educational purposes only — "
    "not investment advice. Always do your own research.",
    small
))

# ── Build ────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF written to: {PDF_PATH}")
