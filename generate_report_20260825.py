"""
Market Report Generator — 2026-08-25
Generates data/prices.csv row append + PDF report
"""
import csv, os
from pathlib import Path
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── 1. APPEND TODAY'S PRICE ROW ──────────────────────────────────────────────
TODAY = "2026-08-25"
SPY_CLOSE  = 767.12
QQQ_CLOSE  = 710.60

csv_path = Path("data/prices.csv")
rows = []
with open(csv_path) as f:
    reader = csv.DictReader(f)
    rows = list(reader)

dates = [r["date"] for r in rows]
if TODAY not in dates:
    rows.append({"date": TODAY, "SPY_close": SPY_CLOSE, "QQQ_close": QQQ_CLOSE})
    rows.sort(key=lambda r: r["date"])
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date","SPY_close","QQQ_close"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Appended {TODAY}: SPY={SPY_CLOSE}, QQQ={QQQ_CLOSE}")
else:
    print(f"{TODAY} already present — no update needed")

# ── 2. COMPUTE STATS FROM prices.csv ─────────────────────────────────────────
spy_prices = [(r["date"], float(r["SPY_close"])) for r in rows]
qqq_prices = [(r["date"], float(r["QQQ_close"])) for r in rows]

# today and prior close
spy_today = SPY_CLOSE
qqq_today = QQQ_CLOSE
spy_prev  = float([r for r in rows if r["date"] < TODAY][-1]["SPY_close"])
qqq_prev  = float([r for r in rows if r["date"] < TODAY][-1]["QQQ_close"])

spy_chg_pct = (spy_today - spy_prev) / spy_prev * 100
qqq_chg_pct = (qqq_today - qqq_prev) / qqq_prev * 100

# 1-year window: from 2025-08-25 through 2026-08-25
yr_spy = [(d, p) for d, p in spy_prices if "2025-08-25" <= d <= TODAY]
yr_qqq = [(d, p) for d, p in qqq_prices if "2025-08-25" <= d <= TODAY]

spy_1y_start = yr_spy[0][1] if yr_spy else spy_today
qqq_1y_start = yr_qqq[0][1] if yr_qqq else qqq_today
spy_1y_hi  = max(p for _, p in yr_spy)
spy_1y_lo  = min(p for _, p in yr_spy)
qqq_1y_hi  = max(p for _, p in yr_qqq)
qqq_1y_lo  = min(p for _, p in yr_qqq)
spy_1y_ret = (spy_today - spy_1y_start) / spy_1y_start * 100
qqq_1y_ret = (qqq_today - qqq_1y_start) / qqq_1y_start * 100

def fmt_pct(v):
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.2f}%"

print(f"SPY: ${spy_today:.2f}  {fmt_pct(spy_chg_pct)} | 1Y High: ${spy_1y_hi:.2f}  Low: ${spy_1y_lo:.2f}  Return: {fmt_pct(spy_1y_ret)}")
print(f"QQQ: ${qqq_today:.2f}  {fmt_pct(qqq_chg_pct)} | 1Y High: ${qqq_1y_hi:.2f}  Low: ${qqq_1y_lo:.2f}  Return: {fmt_pct(qqq_1y_ret)}")

# ── 3. BUILD PDF ──────────────────────────────────────────────────────────────
report_dir = Path(f"reports/{TODAY}")
report_dir.mkdir(parents=True, exist_ok=True)
pdf_path = report_dir / f"markets-{TODAY}.pdf"

doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=letter,
    rightMargin=0.75*inch, leftMargin=0.75*inch,
    topMargin=0.75*inch, bottomMargin=0.75*inch,
)

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Title"], fontSize=18, spaceAfter=4,
                     textColor=colors.HexColor("#1a237e"))
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceAfter=4,
                     textColor=colors.HexColor("#0d47a1"), spaceBefore=12)
H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, spaceAfter=3,
                     textColor=colors.HexColor("#1565c0"), spaceBefore=8)
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontSize=9.5, leading=14,
                       spaceAfter=4)
SMALL = ParagraphStyle("SMALL", parent=styles["Normal"], fontSize=8.5, leading=12)
NOTE = ParagraphStyle("NOTE", parent=styles["Normal"], fontSize=8, leading=11,
                       textColor=colors.grey, leftIndent=10)

TBL_HEADER = colors.HexColor("#1a237e")
TBL_ALT    = colors.HexColor("#e8eaf6")
TBL_WHITE  = colors.white
RED   = colors.HexColor("#c62828")
GREEN = colors.HexColor("#1b5e20")

def color_pct(v):
    """Return colored string for a % change."""
    sign = "+" if v >= 0 else ""
    s = f"{sign}{v:.2f}%"
    c = "#1b5e20" if v >= 0 else "#c62828"
    return f'<font color="{c}">{s}</font>'

story = []

# ─── HEADER ──────────────────────────────────────────────────────────────────
story.append(Paragraph("US Markets Daily Report", H1))
story.append(Paragraph(f"Date: {TODAY} | Generated after NYSE close (ET)",
                        ParagraphStyle("sub", parent=SMALL, textColor=colors.grey)))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a237e")))
story.append(Spacer(1, 8))

# ─── 1. SPY / QQQ SNAPSHOT ───────────────────────────────────────────────────
story.append(Paragraph("1. SPY &amp; QQQ Snapshot", H2))

snap_data = [
    ["", "Close", "Day Change", "1Y High", "1Y Low", "1Y Return"],
    [
        "SPY (S&P 500)",
        f"${spy_today:.2f}",
        fmt_pct(spy_chg_pct),
        f"${spy_1y_hi:.2f}",
        f"${spy_1y_lo:.2f}",
        fmt_pct(spy_1y_ret),
    ],
    [
        "QQQ (Nasdaq-100)",
        f"${qqq_today:.2f}",
        fmt_pct(qqq_chg_pct),
        f"${qqq_1y_hi:.2f}",
        f"${qqq_1y_lo:.2f}",
        fmt_pct(qqq_1y_ret),
    ],
]
snap_tbl = Table(snap_data, colWidths=[1.5*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
snap_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0), TBL_HEADER),
    ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
    ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",      (0,0), (-1,-1), 9),
    ("ALIGN",         (1,0), (-1,-1), "CENTER"),
    ("BACKGROUND",    (0,1), (-1,1), TBL_ALT),
    ("BACKGROUND",    (0,2), (-1,2), TBL_WHITE),
    ("GRID",          (0,0), (-1,-1), 0.5, colors.grey),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [TBL_ALT, TBL_WHITE]),
    ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
    ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ("RIGHTPADDING",  (0,0), (-1,-1), 6),
    ("TOPPADDING",    (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(snap_tbl)
story.append(Spacer(1, 6))

snap_note = (
    f"Prior close: SPY ${spy_prev:.2f} | QQQ ${qqq_prev:.2f}. "
    f"1-year window: Aug 25, 2025 – Aug 25, 2026. "
    "Source: web data; minor rounding vs adjusted close may apply."
)
story.append(Paragraph(snap_note, NOTE))
story.append(Spacer(1, 6))

# ─── 2. TODAY'S KEY NEWS ─────────────────────────────────────────────────────
story.append(Paragraph("2. Today's Market-Moving News", H2))

news_items = [
    ("<b>Moderna (MRNA) +14% — Cancer Vaccine Phase 3 Milestone:</b> MRNA closed at $159.04, "
     "continuing the momentum from its historic Aug 19 announcement when shares surged ~177% after the "
     "Moderna/Merck mRNA-based melanoma vaccine (combined with Keytruda) met primary Phase 3 endpoints. "
     "Today's 14% gain came on expanded analyst commentary (BofA raised PT to $170) and sector rotation "
     "into biotech. MRNA was the #1 S&amp;P 500 gainer on the day."),

    ("<b>DICK'S Sporting Goods (DKS) −25% — Worst Day in 3 Years on Earnings Crash:</b> "
     "Q2 EPS of $3.53 missed the $3.78 consensus; revenues of $5.59B also trailed $5.65B estimates. "
     "Full-year GAAP EPS guidance slashed from $13.27–14.27 to $10.94–11.94 after Foot Locker integration "
     "posted −3.6% comps. DKS was the #1 S&amp;P 500 loser."),

    ("<b>Memory/Storage Sector Sell-Off — SanDisk (SNDK) −6.5%, Seagate (STX) −6.5%, "
     "Micron (MU) −5.8%, Broadcom (AVGO) −2.6%:</b> "
     "SanDisk beat Q4 FY2026 estimates (non-GAAP EPS $39.25 on $8.97B revenue) but issued Q1 guidance "
     "below the $10.8B consensus. The miss triggered a sector-wide re-rating on memory supply-glut fears. "
     "AVGO fell in sympathy. These chip/storage declines were the largest drag on QQQ."),

    ("<b>Jackson Hole Pre-Positioning — Iran Sanctions Expansion:</b> Treasury Secretary Bessent expanded "
     "sanctions on Iran, cutting off additional economic channels. Risk-off tone in energy and geopolitical "
     "names. Markets also began pre-positioning ahead of the Jackson Hole symposium (Aug 27–29) and "
     "Fed Chair Warsh's first keynote speech as Fed Chair on Friday Aug 29."),

    ("<b>Rates Context — 10Y Treasury 4.71%, 2Y 4.24%:</b> The yield curve remains inverted. "
     "Fed held rates at 3.50–3.75% at the July 29 meeting, with three regional bank presidents dissenting "
     "in favor of a hike. Futures price ~1-in-3 odds of a September hike."),

    ("<b>VIX +4.76% to 15.85:</b> Volatility ticked higher reflecting uncertainty around Wednesday's PCE "
     "print (07:00 AM ET), Nvidia earnings (after close), and Jackson Hole Friday."),
]
for item in news_items:
    story.append(Paragraph(f"• {item}", BODY))
    story.append(Spacer(1, 3))

# ─── 3. NEWS → TODAY'S MOVES ─────────────────────────────────────────────────
story.append(Paragraph("3. News → Today's Moves", H2))

story.append(Paragraph(
    f"<b>SPY {fmt_pct(spy_chg_pct)} | QQQ {fmt_pct(qqq_chg_pct)}</b>  (SPY $763.63 → $767.12 | QQQ $705.16 → $710.60)",
    BODY
))
story.append(Spacer(1, 4))

moves = [
    ("<b>MRNA +14% → SPY/QQQ modestly positive:</b> The healthcare surge (MRNA alone at S&amp;P weight added "
     "~+0.10% to SPY) lifted the broader index. Consumer Staples (+1.7%) and Financials (+1.3%) provided "
     "additional breadth support, giving SPY its green close despite tech headwinds."),

    ("<b>Chip/storage sell-off → QQQ headwind offset:</b> SNDK (−6.5%), STX (−6.5%), MU (−5.8%), and "
     "AVGO (−2.6%) combined for significant QQQ drag given their Nasdaq-100 weights. "
     "QQQ still closed positive (+0.77%) because mega-cap tech (TSLA +3.18%, AMZN +1.9%, AAPL +1.67%) "
     "more than offset the chip weakness — a clear rotation from cyclical semis to large-cap growth."),

    ("<b>DKS −25% → Consumer Discretionary drag on SPY:</b> DKS's collapse knocked "
     "~−0.08% off SPY given its index weight. The Foot Locker integration writedowns signal broader "
     "athletic footwear weakness, pressuring peer names like Nike and Under Armour."),

    ("<b>Jackson Hole / Geopolitical tension:</b> Iran sanctions and Warsh speech anticipation kept "
     "institutional buyers selective. The market's limited downside despite multiple negative catalysts "
     "reflects resilient underlying demand — SPY is only 1.4% below its Aug 13 ATH of $777.88."),
]
for item in moves:
    story.append(Paragraph(f"• {item}", BODY))
    story.append(Spacer(1, 3))

# ─── 4. TOP MOVERS ───────────────────────────────────────────────────────────
story.append(Paragraph("4. Top Movers — Daily, Weekly, Monthly", H2))

# ---- DAILY ----
story.append(Paragraph("Daily (Aug 25, 2026)", H3))

daily_g = [
    ["Ticker", "Name", "% Chg", "Sector / Driver"],
    ["MRNA",  "Moderna",                 "+14.0%", "Healthcare — Cancer vaccine Phase 3 data / analyst upgrades"],
    ["SMCI",  "Super Micro Computer",    "+8.9%",  "Tech — AI server demand tailwind, short covering"],
    ["HOOD",  "Robinhood Markets",        "+7.2%",  "Financials — Retail trading volume surge"],
    ["CDW",   "CDW Corp",                "+6.7%",  "IT Services — Earnings beat, enterprise IT resilience"],
    ["BE",    "Bloom Energy",             "+6.1%",  "Utilities/Clean Energy — Data center power demand"],
    ["NVTS",  "Navitas Semiconductor",   "+6.2%",  "Semis — Acquired Claros (AI data center VPD tech, $232.8M)"],
    ["TSLA",  "Tesla",                   "+3.2%",  "Consumer Disc — Momentum / delivery optimism"],
    ["AMZN",  "Amazon",                  "+1.9%",  "Consumer Disc — AWS strength, AI monetization"],
    ["AAPL",  "Apple",                   "+1.7%",  "Tech — iPhone cycle upgrade anticipation"],
    ["EXPE",  "Expedia",                 "+~3.5%", "Consumer Disc — Travel demand resilience"],
]
daily_l = [
    ["Ticker", "Name", "% Chg", "Sector / Driver"],
    ["DKS",   "DICK'S Sporting Goods",  "−25.3%", "Consumer Disc — Q2 EPS/rev miss, full-year guide cut (Foot Locker)"],
    ["GRRR",  "Gorilla Technology",     "−9.7%",  "Tech — H1 EPS miss of −$0.58 vs +$0.20 consensus"],
    ["REAX",  "Real Brokerage",         "−~89%",  "Financials — Dilutive $450M share repurchase surprise"],
    ["SNDK",  "Sandisk Corp",           "−6.5%",  "Tech/Storage — Q1 revenue guidance below $10.8B consensus"],
    ["STX",   "Seagate Technology",     "−6.5%",  "Tech/Storage — Sympathy sell-off, memory supply-glut fears"],
    ["MU",    "Micron Technology",      "−5.8%",  "Semis — Memory sector de-rating"],
    ["ALB",   "Albemarle",              "−5.2%",  "Materials — Lithium price weakness"],
    ["RBRK",  "Rubrik",                 "−4.9%",  "Tech — Risk-off in growth software"],
    ["AVGO",  "Broadcom",               "−2.6%",  "Semis — SNDK sympathy, AI guidance scrutiny"],
    ["JPM",   "JPMorgan Chase",         "−1.9%",  "Financials — Rate curve pressure, credit-cost concern"],
]

def make_mover_table(data, is_gain):
    hdr_color = GREEN if is_gain else RED
    alt = colors.HexColor("#e8f5e9") if is_gain else colors.HexColor("#ffebee")
    tbl = Table(data, colWidths=[0.6*inch, 1.4*inch, 0.75*inch, 4.15*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), hdr_color),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 8),
        ("ALIGN",        (2,0), (2,-1), "CENTER"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [alt, colors.white]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("LEFTPADDING",  (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ("FONTNAME",     (0,1), (0,-1), "Helvetica-Bold"),
    ]))
    return tbl

story.append(Paragraph("<b>Top 10 Daily Gainers</b>", SMALL))
story.append(make_mover_table(daily_g, True))
story.append(Spacer(1, 5))
story.append(Paragraph("<b>Top 10 Daily Losers</b>", SMALL))
story.append(make_mover_table(daily_l, False))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Sector Trend:</b> Healthcare (MRNA) and select Financials/Utilities surged on rotation. "
    "Consumer Discretionary was split: mega-cap resilience (TSLA, AMZN) vs. specialty retail collapse (DKS). "
    "Memory/Storage (SNDK, STX, MU) was the single worst sub-sector. Tech overall mixed.",
    NOTE
))
story.append(Spacer(1, 6))

# ---- WEEKLY ----
story.append(Paragraph("Weekly (Aug 18–25, 2026)", H3))

weekly_g = [
    ["Ticker", "Name", "Approx %", "Sector / Driver"],
    ["MRNA",  "Moderna",              "+~130%+", "Healthcare — Phase 3 melanoma vaccine data (Aug 19 catalyst)"],
    ["MRK",   "Merck",                "+~8%",    "Healthcare — MRNA vaccine partner beneficiary"],
    ["HOOD",  "Robinhood Markets",    "+~10%",   "Financials — Record retail trading activity"],
    ["SMCI",  "Super Micro Computer", "+~12%",   "Tech — AI server orders, short squeeze"],
    ["COIN",  "Coinbase",             "+~8%",    "Financials — Crypto rally, regulatory clarity"],
    ["BE",    "Bloom Energy",         "+~9%",    "Clean Energy — Data center power contracts"],
    ["NVTS",  "Navitas Semi",         "+~6%",    "Semis — Claros acquisition announced midweek"],
    ["TSLA",  "Tesla",                "+~5%",    "Consumer Disc — Delivery expectations, Q3 optionality"],
    ["AAPL",  "Apple",                "+~3%",    "Tech — Fall iPhone cycle inflows"],
    ["AMZN",  "Amazon",               "+~3%",    "Consumer Disc — AWS AI monetization sentiment"],
]
weekly_l = [
    ["Ticker", "Name", "Approx %", "Sector / Driver"],
    ["SNDK",  "Sandisk Corp",         "−~20%",   "Tech/Storage — Guidance miss; memory supply-glut fears"],
    ["STX",   "Seagate Technology",   "−~10%",   "Tech/Storage — Memory sector contagion"],
    ["MU",    "Micron Technology",    "−~8%",    "Semis — Supply-glut re-rating"],
    ["AVGO",  "Broadcom",             "−~5%",    "Semis — SNDK sympathy, elevated expectations"],
    ["DKS",   "DICK'S Sporting Goods","−~25%",   "Consumer Disc — Earnings collapse on Aug 25"],
    ["ALB",   "Albemarle",            "−~7%",    "Materials — Lithium oversupply / EV demand softness"],
    ["GRRR",  "Gorilla Technology",   "−~12%",   "Tech — Earnings miss (H1 EPS −$0.58 vs +$0.20 est)"],
    ["CIEN",  "Ciena Corp",           "−~5%",    "Tech — Optical networking uncertainty"],
    ["SRE",   "Sempra Energy",        "−~4%",    "Utilities — Rate sensitivity to hawkish Fed signals"],
    ["EIX",   "Edison International", "−~4%",    "Utilities — Same rate headwinds"],
]

story.append(Paragraph("<b>Top 10 Weekly Gainers (Est.)</b>", SMALL))
story.append(make_mover_table(weekly_g, True))
story.append(Spacer(1, 5))
story.append(Paragraph("<b>Top 10 Weekly Losers (Est.)</b>", SMALL))
story.append(make_mover_table(weekly_l, False))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Weekly Sector Trend — Gainers:</b> Healthcare (MRNA/MRK) dominant on vaccine breakthrough. "
    "Fintech/Crypto (HOOD, COIN) outperformed. AI-adjacent (SMCI, NVTS, AMZN AWS) also strong. "
    "<b>Losers:</b> Memory/Storage sub-sector was worst (SNDK, STX, MU supply-glut repricing). "
    "Utilities underperformed on rate sensitivity.",
    NOTE
))
story.append(Spacer(1, 6))

# ---- MONTHLY ----
story.append(Paragraph("Monthly (July 31 – Aug 25, 2026)", H3))

monthly_g = [
    ["Ticker", "Name", "Approx %", "Sector / Driver"],
    ["MRNA",  "Moderna",              "+163%+",  "Healthcare — Cancer vaccine Phase 3 breakthrough (Aug 19)"],
    ["RFAI",  "RF Acquisition Corp II","+423%",  "Special Situations — SPAC activity"],
    ["SMCI",  "Super Micro Computer", "+~20%",   "Tech — AI server demand + short squeeze"],
    ["HOOD",  "Robinhood Markets",    "+~18%",   "Financials — Record retail trading volume"],
    ["COIN",  "Coinbase",             "+~15%",   "Financials — Crypto bull run, regulatory wins"],
    ["NVTS",  "Navitas Semi",         "+~10%",   "Semis — Claros deal, AI power IC demand"],
    ["TSLA",  "Tesla",                "+~9%",    "Consumer Disc — Delivery beat optimism"],
    ["SPY",   "SPDR S&P 500 ETF",     "+~3.1%",  "Broad Market — ATH on Aug 13 ($777.88)"],
    ["AMZN",  "Amazon",               "+~6%",    "Consumer Disc — AWS AI monetization"],
    ["MRK",   "Merck",                "+~9%",    "Healthcare — Keytruda cancer vaccine co-developer"],
]
monthly_l = [
    ["Ticker", "Name", "Approx %", "Sector / Driver"],
    ["SNDK",  "Sandisk Corp",         "−~20%",   "Tech/Storage — Guidance miss, supply-glut fears"],
    ["DKS",   "DICK'S Sporting Goods","−~25%",   "Consumer Disc — Foot Locker integration, earnings miss"],
    ["GRRR",  "Gorilla Technology",   "−~15%",   "Tech — H1 EPS miss, execution concerns"],
    ["ALB",   "Albemarle",            "−~12%",   "Materials — Lithium prices, EV demand softness"],
    ["MU",    "Micron Technology",    "−~8%",    "Semis — SNDK contagion, supply-glut pricing"],
    ["STX",   "Seagate Technology",   "−~9%",    "Tech/Storage — Memory sector re-rating"],
    ["AVGO",  "Broadcom",             "−~5%",    "Semis — AI guidance skepticism"],
    ["SRE",   "Sempra Energy",        "−~6%",    "Utilities — Rate sensitivity"],
    ["MRVL",  "Marvell Technology",   "−~5%",    "Semis — Sector rotation"],
    ["QQQ",   "Invesco QQQ ETF",      "−~2.4%",  "Nasdaq-100 — Tech underperformance vs S&P 500"],
]

story.append(Paragraph("<b>Top 10 Monthly Gainers (Est.)</b>", SMALL))
story.append(make_mover_table(monthly_g, True))
story.append(Spacer(1, 5))
story.append(Paragraph("<b>Top 10 Monthly Losers (Est.)</b>", SMALL))
story.append(make_mover_table(monthly_l, False))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Monthly Sector Trend — Gainers:</b> Healthcare dominated (MRNA historic move). "
    "Fintech/Crypto (HOOD, COIN) strong all month. AI-adjacent tech (SMCI, NVTS) outperformed. "
    "<b>Losers:</b> Memory/Storage is August's worst sector. Materials (lithium names) weak. "
    "QQQ underperforming SPY month-to-date on tech sector weight.",
    NOTE
))
story.append(Spacer(1, 6))

# ─── 5. NEXT-DAY SCENARIOS (Aug 26, 2026) ───────────────────────────────────
story.append(Paragraph("5. Next Trading Day — Aug 26, 2026 Scenarios", H2))
story.append(Paragraph(
    "Three major scheduled catalysts hit Wednesday, Aug 26. Markets arrive highly sensitized "
    "after VIX ticked up to 15.85 today and chips remain in turmoil.",
    BODY
))
story.append(Spacer(1, 4))

scenarios = [
    (
        "A. Nvidia (NVDA) Q2 Earnings — After Close Aug 26",
        [
            ("<b>Consensus:</b> Revenue $92.2B (+97% YoY), EPS $2.09. "
             "Q3 guidance expected $107–108B vs Wall St $104B consensus. "
             "Data-center segment (~$88B of revenue) is the focal point."),
            ("<b>IF Beat + Strong Guide (Q3 guidance ≥$107B, data-center ≥$90B):</b> "
             "QQQ likely +1.5% to +3.0% in after-hours/next-day open. SPY +0.7% to +1.5%. "
             "AI semi names (AVGO, SMCI, NVTS) catch bids. Memory relief rally possible. "
             "Mechanism: NVDA is the bellwether for AI capital spending; a strong guide confirms "
             "hyperscaler CapEx didn't slow — restoring confidence in the entire AI supply chain."),
            ("<b>IF Beat but Weak Guide (Q3 guidance &lt;$104B or data-center deceleration):</b> "
             "QQQ −2% to −4%, SPY −1% to −2%. NVDA stock −8% to −15% after hours. "
             "Memory/Storage names (SNDK, MU) likely accelerate lower. "
             "Mechanism: The market tolerates a beat only if future demand is intact; guidance miss "
             "reads as AI CapEx peaking and collapses the 'AI forever' premium in Nasdaq-100."),
            ("<b>IF Miss + Weak Guide:</b> QQQ −4% to −6%, SPY −2% to −3%. "
             "Circuit breaker risk in thin after-hours liquidity."),
        ]
    ),
    (
        "B. July PCE Inflation — 8:30 AM ET Aug 26",
        [
            ("<b>Consensus:</b> Headline PCE +0.07% MoM (YoY: 3.6%). Core PCE +0.18% MoM (YoY: 3.2%). "
             "June was −0.11% MoM — so any uptick will be notable."),
            ("<b>IF In-Line or Below (Core ≤0.18% MoM):</b> "
             "SPY +0.3% to +0.7%, QQQ +0.5% to +1.0%. Bonds rally (10Y yield falls toward 4.60%). "
             "Dollar weakens. Mechanism: Confirms disinflation trajectory, reduces odds of Sep hike, "
             "and is a tailwind for Warsh's 'hold' optionality at Jackson Hole Friday."),
            ("<b>IF Hot (Core &gt;0.25% MoM or YoY &gt;3.5%):</b> "
             "SPY −0.7% to −1.5%, QQQ −1.0% to −2.0%. 10Y yield jumps toward 4.85%. "
             "Dollar surges. Rate-sensitive sectors (utilities, REITs) sell off hard. "
             "Mechanism: Raises odds of Sep hike to 50%+, directly contradicting the 'pause-then-cut' "
             "narrative and squeezing any Fed pivot trade ahead of Jackson Hole."),
        ]
    ),
    (
        "C. Jackson Hole — Fed Chair Warsh Speech, Friday Aug 29",
        [
            ("<b>Context:</b> Warsh's FIRST Jackson Hole speech as Fed Chair. "
             "Inflation at 3.4% (above 2% target). Fed held at 3.50–3.75% on Jul 29. "
             "3 regional bank presidents dissented FOR a hike — most discord since Sep 2016. "
             "Markets: ~1-in-3 odds of Sep hike in futures."),
            ("<b>IF Hawkish (Warsh signals Sep hike is live, 'inflation remains too high'):</b> "
             "SPY −1.5% to −3.0%, QQQ −2.0% to −4.0% on Friday. 10Y yield +15–25 bps. "
             "Dollar DXY +0.8% to +1.5%. Gold and Treasuries sell off. "
             "Mechanism: Forces a full repricing of the Sep meeting from 'hold' to 'hike', "
             "compressing P/E multiples across growth/tech names already under pressure."),
            ("<b>IF Dovish / Balanced (Warsh signals patience, data-dependent):</b> "
             "SPY +1.0% to +2.0%, QQQ +1.5% to +3.0% on Friday. Rate relief rally. "
             "Mechanism: Removes the Sep hike premium, re-opens the 'soft landing' trade. "
             "Tech / Nasdaq disproportionate beneficiary given duration sensitivity."),
            ("<b>IF Structural / Neutral (Warsh avoids rate guidance, focuses on long-run framework):</b> "
             "Low vol (SPY ±0.5%). Mechanism: Creates ambiguity — bond market tests higher yields, "
             "equities roughly flat. Volatility bleeds into the week after."),
        ]
    ),
    (
        "D. Nvidia Earnings + PCE Combined Risk",
        [
            ("<b>Overlapping catalysts create asymmetric setup:</b> If PCE is hot AND NVDA guides weak, "
             "SPY could gap −3% to −5% on Aug 27. If PCE is tame AND NVDA beats, "
             "SPY gap-up +2% to +4% is plausible — one of the largest single-day moves of 2026. "
             "The key observation: SPY is −1.4% from ATH ($777.88 on Aug 13), meaning positioning is "
             "NOT bearish — any positive surprise re-tests the ATH rapidly."),
        ]
    ),
]

for title, bullets in scenarios:
    story.append(Paragraph(title, H3))
    for b in bullets:
        story.append(Paragraph(f"▸ {b}", BODY))
    story.append(Spacer(1, 4))

# ─── 6. POSSIBLE PURCHASE SUMMARY ───────────────────────────────────────────
story.append(Paragraph("6. Possible Trade Summary (End-of-Day / Next-Day Open)", H2))
story.append(Paragraph(
    "<b>IMPORTANT DISCLAIMER:</b> This is an analytical summary only. No actual trades are placed. "
    "All scenarios are hypothetical, forward-looking, and carry significant risk.",
    ParagraphStyle("disc", parent=NOTE, textColor=RED, fontName="Helvetica-BoldOblique")
))
story.append(Spacer(1, 5))

trades = [
    ["Trade", "Instrument", "Direction", "Rationale", "Key Risk"],
    [
        "1",
        "QQQ (Nasdaq-100 ETF)",
        "WATCH / HOLD",
        "Await NVDA earnings (after close Aug 26). QQQ is 2.4% off monthly lows. "
        "A NVDA beat + strong guide = high-conviction long entry; a miss = avoid entirely. "
        "Jackson Hole Friday provides 2nd catalyst.",
        "NVDA weak guide = QQQ −4%+. PCE upside surprise pre-market Aug 26."
    ],
    [
        "2",
        "MRNA (Moderna)",
        "HOLD / PARTIAL SELL",
        "Stock at $159 after 177% surge from ~$57. Phase 3 data is real and transformative "
        "(BofA PT $170). However, regulatory approval pipeline is multi-year. "
        "Trim position if it approaches $170; re-enter on pullbacks toward $130–140. "
        "Merck (MRK) is a cleaner play on same catalyst with lower volatility.",
        "Regulatory delays. Mkt fatigue after +130% monthly run. Profit-taking spike."
    ],
    [
        "3",
        "SNDK (Sandisk)",
        "AVOID / SHORT WATCH",
        "Guidance miss + memory supply-glut creates fundamental pressure. "
        "Down ~20% in August already but the guidance reset suggests earnings trough "
        "not yet established. Wait for Q1 FY27 data before re-entry. "
        "Fundamentals: $8.97B Q4 revenue (beat) but forward guide below $10.8B consensus.",
        "NVDA beat could lift all semis; SNDK may bounce 5–8% on sector relief rally."
    ],
    [
        "4",
        "SPY (S&P 500 ETF)",
        "BULLISH BIAS — WAIT",
        "SPY at $767.12, only 1.4% from ATH $777.88. If PCE tame + NVDA beats + Warsh "
        "balanced → SPY likely re-tests $777–780 next week. "
        "Risk/reward favors long on any Aug 26 pre-market dip. "
        "Support at $763 (prior close). Next resistance: $778 (ATH).",
        "Hot PCE + NVDA miss = SPY tests $745–750 (July low region)."
    ],
    [
        "5",
        "DKS (DICK'S Sporting Goods)",
        "AVOID",
        "Down 25% today on Foot Locker integration disaster. Full-year guide cut of ~$2.30 "
        "EPS is severe. Athletic footwear channel broadly impaired (peer risk to NKE, FL). "
        "No clear recovery catalyst without Foot Locker comp stabilization.",
        "Any positive footwear data could trigger short-cover bounce 10–15%."
    ],
]

trade_tbl = Table(
    trades,
    colWidths=[0.3*inch, 1.1*inch, 0.85*inch, 3.3*inch, 1.45*inch]
)
trade_tbl.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), TBL_HEADER),
    ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [TBL_ALT, TBL_WHITE]),
    ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
    ("LEFTPADDING",  (0,0), (-1,-1), 5),
    ("RIGHTPADDING", (0,0), (-1,-1), 5),
    ("TOPPADDING",   (0,0), (-1,-1), 4),
    ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ("VALIGN",       (0,0), (-1,-1), "TOP"),
    ("FONTNAME",     (0,1), (0,-1), "Helvetica-Bold"),
    ("FONTNAME",     (2,1), (2,-1), "Helvetica-Bold"),
]))
story.append(trade_tbl)
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Key Decision Point:</b> The highest-leverage moment is 8:30 AM ET Aug 26 (PCE print) and then "
    "after close Aug 26 (NVDA earnings). Initiating meaningful long exposure before these "
    "two data points is speculative. Best risk-adjusted approach: hold current positions, "
    "set levels, and act after PCE and NVDA are known.",
    BODY
))

# ─── FOOTER ──────────────────────────────────────────────────────────────────
story.append(Spacer(1, 12))
story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
story.append(Paragraph(
    f"Generated automatically after NYSE close on {TODAY}. "
    "Data sourced from public web searches (Yahoo Finance search results, CNBC, Benzinga, Trefis, "
    "Eastern Herald, Motley Fool, BioSpace, GuruFocus). Prices are closing approximations; "
    "minor rounding vs exchange-official adjusted closes may apply. "
    "This report is for informational purposes only and does not constitute investment advice.",
    NOTE
))

# ─── BUILD ────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF written to {pdf_path}")
