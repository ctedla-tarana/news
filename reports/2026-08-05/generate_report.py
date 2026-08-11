#!/usr/bin/env python3
"""
US Markets Daily Report — 2026-08-05
Generated automatically after market close ET.
"""

import csv
import os
from datetime import date, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

REPORT_DATE = "2026-08-05"
CSV_PATH = os.path.join(os.path.dirname(__file__), "../../data/prices.csv")
OUT_PATH = os.path.join(os.path.dirname(__file__), "markets-2026-08-05.pdf")


def load_prices():
    rows = []
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "date": row["date"],
                "spy": float(row["SPY_close"]),
                "qqq": float(row["QQQ_close"]),
            })
    rows.sort(key=lambda r: r["date"])
    return rows


def compute_stats(rows, today_str):
    today = next(r for r in rows if r["date"] == today_str)
    prior = rows[rows.index(today) - 1] if rows.index(today) > 0 else today

    spy_today = today["spy"]
    qqq_today = today["qqq"]
    spy_prior = prior["spy"]
    qqq_prior = prior["qqq"]

    spy_pct = (spy_today - spy_prior) / spy_prior * 100
    qqq_pct = (qqq_today - qqq_prior) / qqq_prior * 100

    # 1-year window
    yr_rows = rows  # full dataset ~1yr
    spy_1y_high = max(r["spy"] for r in yr_rows)
    spy_1y_low = min(r["spy"] for r in yr_rows)
    spy_1y_ret = (spy_today - yr_rows[0]["spy"]) / yr_rows[0]["spy"] * 100

    qqq_1y_high = max(r["qqq"] for r in yr_rows)
    qqq_1y_low = min(r["qqq"] for r in yr_rows)
    qqq_1y_ret = (qqq_today - yr_rows[0]["qqq"]) / yr_rows[0]["qqq"] * 100

    return {
        "spy_today": spy_today, "qqq_today": qqq_today,
        "spy_prior": spy_prior, "qqq_prior": qqq_prior,
        "spy_pct": spy_pct, "qqq_pct": qqq_pct,
        "spy_1y_high": spy_1y_high, "spy_1y_low": spy_1y_low, "spy_1y_ret": spy_1y_ret,
        "qqq_1y_high": qqq_1y_high, "qqq_1y_low": qqq_1y_low, "qqq_1y_ret": qqq_1y_ret,
        "start_date": yr_rows[0]["date"], "prior_date": prior["date"],
    }


def pct_color(val):
    if val >= 0:
        return colors.HexColor("#006400")
    return colors.HexColor("#8B0000")


def build_pdf(stats):
    doc = SimpleDocTemplate(
        OUT_PATH,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title2", parent=styles["Title"],
        fontSize=20, leading=26, textColor=colors.HexColor("#1a1a2e"), spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#444466"), spaceAfter=14, alignment=TA_CENTER
    )
    h1_style = ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=14, leading=18, textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=14, spaceAfter=6, borderPad=2
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=12, leading=16, textColor=colors.HexColor("#2a2a5e"),
        spaceBefore=10, spaceAfter=4
    )
    body_style = ParagraphStyle(
        "Body2", parent=styles["Normal"],
        fontSize=9.5, leading=14, spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        "Bullet", parent=styles["Normal"],
        fontSize=9.5, leading=14, leftIndent=16, spaceAfter=4,
        bulletIndent=6, bulletFontSize=9.5
    )
    note_style = ParagraphStyle(
        "Note", parent=styles["Normal"],
        fontSize=8.5, leading=12, textColor=colors.HexColor("#666666"), spaceAfter=6
    )

    story = []

    # ── HEADER ──────────────────────────────────────────────────────────────
    story.append(Paragraph("US Markets Daily Report", title_style))
    story.append(Paragraph(f"Wednesday, August 5, 2026  |  After Market Close (4:00 PM ET)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e"), spaceAfter=14))

    # ── SPY / QQQ SNAPSHOT ───────────────────────────────────────────────────
    story.append(Paragraph("1. SPY / QQQ Snapshot", h1_style))

    def fmt_pct(v):
        sign = "+" if v >= 0 else ""
        return f"{sign}{v:.2f}%"

    spy_arrow = "▲" if stats["spy_pct"] >= 0 else "▼"
    qqq_arrow = "▲" if stats["qqq_pct"] >= 0 else "▼"

    snap_data = [
        ["", "SPY (S&P 500 ETF)", "QQQ (Nasdaq-100 ETF)"],
        ["Today's Close", f"${stats['spy_today']:.2f}", f"${stats['qqq_today']:.2f}"],
        ["Prior Close", f"${stats['spy_prior']:.2f}  ({stats['prior_date']})", f"${stats['qqq_prior']:.2f}  ({stats['prior_date']})"],
        ["Day Change", f"{spy_arrow} {fmt_pct(stats['spy_pct'])}", f"{qqq_arrow} {fmt_pct(stats['qqq_pct'])}"],
        ["1-Yr High", f"${stats['spy_1y_high']:.2f}", f"${stats['qqq_1y_high']:.2f}"],
        ["1-Yr Low", f"${stats['spy_1y_low']:.2f}", f"${stats['qqq_1y_low']:.2f}"],
        [f"1-Yr Return\n(since {stats['start_date']})", fmt_pct(stats["spy_1y_ret"]), fmt_pct(stats["qqq_1y_ret"])],
    ]

    snap_table = Table(snap_data, colWidths=[1.5 * inch, 2.8 * inch, 2.8 * inch])
    spy_pct_row = 3
    qqq_pct_row = 3
    snap_ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f4ff"), colors.white]),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
    # Color day-change cells
    spy_chg_color = colors.HexColor("#d4edda") if stats["spy_pct"] >= 0 else colors.HexColor("#f8d7da")
    qqq_chg_color = colors.HexColor("#d4edda") if stats["qqq_pct"] >= 0 else colors.HexColor("#f8d7da")
    spy_txt_color = colors.HexColor("#155724") if stats["spy_pct"] >= 0 else colors.HexColor("#721c24")
    qqq_txt_color = colors.HexColor("#155724") if stats["qqq_pct"] >= 0 else colors.HexColor("#721c24")
    snap_ts.add("BACKGROUND", (1, 3), (1, 3), spy_chg_color)
    snap_ts.add("BACKGROUND", (2, 3), (2, 3), qqq_chg_color)
    snap_ts.add("TEXTCOLOR", (1, 3), (1, 3), spy_txt_color)
    snap_ts.add("TEXTCOLOR", (2, 3), (2, 3), qqq_txt_color)
    snap_ts.add("FONTNAME", (1, 3), (2, 3), "Helvetica-Bold")
    snap_table.setStyle(snap_ts)
    story.append(snap_table)
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"Note: 1-year stats computed from prices.csv spanning {stats['start_date']} to {REPORT_DATE} (~265 trading days). "
        "Dow Jones Industrials closed at a new all-time high. Mixed session: S&P 500 and Nasdaq snapped 4-day winning streaks.",
        note_style
    ))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"), spaceBefore=10, spaceAfter=10))

    # ── TODAY'S NEWS & MARKET DRIVERS ────────────────────────────────────────
    story.append(Paragraph("2. Today's Key News & Market Drivers", h1_style))

    news_items = [
        (
            "SpaceX (SPCX) Earnings Disappoint Despite Revenue Beat  →  SPCX ▼ ~8%",
            "SpaceX Q2 revenue of $7.8B crushed the $6.81B consensus (+92% YoY) and net loss narrowed to $541M from $1B. "
            "BUT: Q2 AI capex of $15.8B nearly doubled Q1's $7.7B and far exceeded analyst models, raising fears of "
            "margin destruction. Investors sold first, asked questions later. This dragged Nasdaq-100 and suppressed QQQ."
        ),
        (
            "AMD (AMD) Q2 Double Beat — Still Sold Off  →  AMD ▼ 7.04%",
            "AMD posted record revenue of $11.5B (+50% YoY) and adjusted EPS of $1.66 (+246% YoY), both well above "
            "consensus. Data Center sales of $6.7B were +107% YoY. Market reaction was 'sell the news': guidance was "
            "in-line but not euphoric, and investors rotated out after the run-up into earnings. AMD's weight in QQQ "
            "amplified the drag on the ETF."
        ),
        (
            "Iran / Strait of Hormuz Diplomacy  →  Oil ▼ 5.7%, Dow ▲ new record",
            "Treasury Sec. Bessent said 'we are in talks with the Iranians' with 'a chance we may have a deal today "
            "or tomorrow to open the Strait.' President Trump added Hormuz would reopen 'very soon' or Iran would be "
            "'hit very hard.' WTI crude fell to $75.77. The prospect of reopened oil lanes boosted industrials "
            "(XLI +1.9%), consumer discretionary (XLY +1.8%), and communication services (XLC +2.9%), pushing the Dow "
            "to a fresh record. However tech-heavy Nasdaq was weighed down by SpaceX/AMD."
        ),
        (
            "Palantir (PLTR) Post-Earnings Continuation  →  PLTR ▲ (continued from Aug 4 +29.5%)",
            "After Palantir's Aug 3 blowout (Q2 revenue $1.935B, +93% YoY; US commercial +149%; Rule-of-40 score 155%), "
            "PLTR surged 29.5% on Aug 4. Momentum carried into Aug 5, making it the top S&P 500 gainer. "
            "Full-year revenue guidance raised to $8.15-8.16B (+82% YoY). Short squeeze of ~$3B added fuel."
        ),
        (
            "Aptiv (APTV) Guidance Cut  →  APTV ▼ 16.6%, 52-week low",
            "Aptiv slashed 2026 sales guidance by $300M, cut adjusted EPS midpoint 3.4%, trimmed FCF midpoint 10%, "
            "blaming prolonged weakness in China EV market and delays from European luxury OEM customers. Shares hit $47.72."
        ),
        (
            "NRG Energy (NRG) EPS Miss  →  NRG ▼ to 52-week low",
            "NRG's $7.90-$9.90 full-year EPS guidance missed market expectations despite an 11% revenue beat in Q2. "
            "Investors focused on the softer earnings outlook amid elevated power-market uncertainty."
        ),
        (
            "Chipotle (CMG) Salmonella Outbreak  →  CMG ▼ sharply",
            "CMG removed jalapeños from certain locations under investigation by public health regulators for a Salmonella "
            "outbreak in Minnesota (110 cases, 75 traced to Chipotle). Investor concern over brand damage and comp traffic."
        ),
    ]

    for headline, detail in news_items:
        story.append(Paragraph(f"<b>{headline}</b>", bullet_style))
        story.append(Paragraph(detail, ParagraphStyle("detail", parent=body_style, leftIndent=16)))
        story.append(Spacer(1, 4))

    # Summary sentence
    story.append(Paragraph(
        "<b>Net effect on SPY/QQQ:</b> SPY fell a modest <b>-0.24%</b> to $769.76 — tech/mega-cap drag "
        "(SpaceX, AMD, APTV) partially offset by gains in industrials, comm services, and discretionary on "
        "geopolitical optimism. QQQ fell <b>-0.35%</b> to $723.85 — more exposed to the tech disappointments "
        "via SpaceX and AMD's large weights. Breadth was still broadly positive (NYSE advancers/decliners ~2.8:1).",
        body_style
    ))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"), spaceBefore=10, spaceAfter=10))

    # ── TOP MOVERS ────────────────────────────────────────────────────────────
    story.append(Paragraph("3. Top 10 Movers — Daily, Weekly, Monthly", h1_style))

    # DAILY
    story.append(Paragraph("Daily Movers (August 5, 2026)", h2_style))
    daily_data = [
        ["Rank", "Ticker", "Company", "% Change", "Catalyst"],
        ["▲ 1", "PLTR", "Palantir Technologies", "+~5-7%*", "Post-earnings momentum; $3B short squeeze"],
        ["▲ 2", "ZBRA", "Zebra Technologies", "+~4-6%*", "Strong Q2 earnings; analyst price target hikes"],
        ["▲ 3", "IT", "Gartner", "+16.3%*†", "Strong revenue growth; raised guidance"],
        ["▲ 4", "INDU stocks", "Industrials (CAT, XLI)", "+1.9% sector", "Iran deal hopes; oil decline benefiting supply chains"],
        ["▲ 5", "XLC names", "Comm Services stocks", "+2.9% sector", "Geopolitical optimism; Hormuz reopening narrative"],
        ["▼ 1", "APTV", "Aptiv PLC", "-16.6%", "Guidance cut $300M; China/EU OEM weakness"],
        ["▼ 2", "NRG", "NRG Energy", "~-10%*", "Q2 EPS miss; weak 2026 guidance; 52-wk low"],
        ["▼ 3", "CMG", "Chipotle Mexican Grill", "~-8%*", "Salmonella outbreak investigation; jalapeño removal"],
        ["▼ 4", "SPCX", "SpaceX", "-8%+", "Earnings: AI CapEx $15.8B >> estimates; margin fears"],
        ["▼ 5", "AMD", "Advanced Micro Devices", "-7.04%", "Earnings beat but 'sell the news'; in-line guidance"],
    ]

    daily_table = Table(daily_data, colWidths=[0.5*inch, 0.65*inch, 1.8*inch, 0.9*inch, 2.7*inch])
    daily_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (3, 0), (3, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0fff0"), colors.white,
                                               colors.HexColor("#f0fff0"), colors.white,
                                               colors.HexColor("#f0fff0"),
                                               colors.HexColor("#fff0f0"), colors.white,
                                               colors.HexColor("#fff0f0"), colors.white,
                                               colors.HexColor("#fff0f0")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TEXTCOLOR", (3, 1), (3, 5), colors.HexColor("#155724")),
        ("TEXTCOLOR", (3, 6), (3, 10), colors.HexColor("#721c24")),
        ("FONTNAME", (3, 1), (3, -1), "Helvetica-Bold"),
    ]))
    story.append(daily_table)
    story.append(Paragraph(
        "* Approximate; Trefis/Benzinga sources. † IT (Gartner) 1-month return cited; exact daily % from Trefis movers report. "
        "Sector gains from XLI/XLC ETF moves. SpaceX (SPCX) is publicly traded on Nasdaq.",
        note_style
    ))
    story.append(Paragraph(
        "<b>Daily Sector Trend:</b> Winners concentrated in industrials and comm services (Iran/Hormuz "
        "reopening trade). Losers dominated by tech (earnings disappointment) and consumer (food safety).",
        body_style
    ))
    story.append(Spacer(1, 8))

    # WEEKLY
    story.append(Paragraph("Weekly Movers (Jul 29 – Aug 5, 2026)", h2_style))
    story.append(Paragraph(
        "SPY: $729.38 → $769.76  (+5.5% for the week)  |  QQQ: $663.74 → $723.85  (+9.1% for the week)",
        ParagraphStyle("wksum", parent=body_style, fontName="Helvetica-Bold")
    ))
    weekly_data = [
        ["Rank", "Ticker", "Company", "~Wk %", "Driver"],
        ["▲ 1", "PLTR", "Palantir Technologies", "+~35%+", "Q2 blowout: revenue +93%, Rule-of-40 = 155%; AI thesis vindicated"],
        ["▲ 2", "MRVL", "Marvell Technology", "+~13%", "AI chip demand surge; posted Aug 4 with broader semis rally"],
        ["▲ 3", "INTC", "Intel", "+~11%", "Semis recovery week; AI infrastructure spending optimism"],
        ["▲ 4", "ZBRA", "Zebra Technologies", "+~10%*", "Strong earnings; warehouse automation demand"],
        ["▲ 5", "IT", "Gartner", "+~10%*", "Tech consulting demand; raised guidance"],
        ["▼ 1", "APTV", "Aptiv PLC", "-16.6%+", "China EV weakness; European OEM delays; guidance slash"],
        ["▼ 2", "SPCX", "SpaceX", "-8%+", "Earnings reaction; excessive AI CapEx concerns"],
        ["▼ 3", "AMD", "Advanced Micro Devices", "-7%", "Sell-the-news post-earnings despite record revenue"],
        ["▼ 4", "NRG", "NRG Energy", "~-10%*", "Q2 EPS miss; weak guidance; utility sector headwind"],
        ["▼ 5", "CMG", "Chipotle", "~-8%*", "Salmonella outbreak; brand/traffic risk"],
    ]
    weekly_table = Table(weekly_data, colWidths=[0.5*inch, 0.65*inch, 1.8*inch, 0.9*inch, 2.7*inch])
    weekly_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a2a5e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0fff0"), colors.white,
                                               colors.HexColor("#f0fff0"), colors.white,
                                               colors.HexColor("#f0fff0"),
                                               colors.HexColor("#fff0f0"), colors.white,
                                               colors.HexColor("#fff0f0"), colors.white,
                                               colors.HexColor("#fff0f0")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TEXTCOLOR", (3, 1), (3, 5), colors.HexColor("#155724")),
        ("TEXTCOLOR", (3, 6), (3, 10), colors.HexColor("#721c24")),
        ("FONTNAME", (3, 1), (3, -1), "Helvetica-Bold"),
    ]))
    story.append(weekly_table)
    story.append(Paragraph(
        "* Approximate from available sources. Weekly data from prices.csv. The strong weekly performance in SPY/QQQ driven by the "
        "early-August AI/tech earnings wave (Palantir, Broadcom, Micron). Semiconductors led the charge Mon-Tue before mixed Wed.",
        note_style
    ))
    story.append(Paragraph(
        "<b>Weekly Sector Trend:</b> <b>AI semiconductors and data infrastructure</b> dominated (PLTR, MRVL, INTC, MU, AVGO). "
        "Losers were isolated to individual earnings misses/guidance cuts — no broad sector selloff.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # MONTHLY
    story.append(Paragraph("Monthly Movers (July 2026)", h2_style))
    monthly_data = [
        ["Rank", "Ticker", "Company", "July %", "Driver"],
        ["▲ 1", "CTSH", "Cognizant Tech Solutions", "+42.9%", "AI-driven IT services demand; contract wins"],
        ["▲ 2", "ACN", "Accenture", "+34.9%", "Digital transformation spend; strong Q3 guidance"],
        ["▲ 3", "PYPL", "PayPal", "+32.5%", "Fintech recovery; new AI-checkout features; buybacks"],
        ["▲ 4", "WDAY", "Workday", "+~28%*", "HCM/ERP cloud demand; AI copilot adoption"],
        ["▲ 5", "WTW", "Willis Towers Watson", "+~24%*", "Insurance/consulting; resilient demand"],
        ["▼ 1", "SNDK", "Sandisk", "-46.6%", "NAND flash oversupply; pricing collapse"],
        ["▼ 2", "GLW", "Corning", "-45.9%", "Display glass demand collapse; telecom cuts"],
        ["▼ 3", "KLAC", "KLA Corp", "-39.4%", "Semiconductor equipment cycle peak concerns"],
        ["▼ 4", "MRVL", "Marvell Technology", "-37.0%", "AI capex overhang; valuation compression (note: recovered in Aug)"],
        ["▼ 5", "CSGP", "CoStar Group", "-~25%*", "CRE market weakness; high valuation multiple contraction"],
    ]
    monthly_table = Table(monthly_data, colWidths=[0.5*inch, 0.65*inch, 1.8*inch, 0.9*inch, 2.7*inch])
    monthly_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a5e2a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0fff0"), colors.white,
                                               colors.HexColor("#f0fff0"), colors.white,
                                               colors.HexColor("#f0fff0"),
                                               colors.HexColor("#fff0f0"), colors.white,
                                               colors.HexColor("#fff0f0"), colors.white,
                                               colors.HexColor("#fff0f0")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TEXTCOLOR", (3, 1), (3, 5), colors.HexColor("#155724")),
        ("TEXTCOLOR", (3, 6), (3, 10), colors.HexColor("#721c24")),
        ("FONTNAME", (3, 1), (3, -1), "Helvetica-Bold"),
    ]))
    story.append(monthly_table)
    story.append(Paragraph(
        "* Approximate. Sources: STL.News, MoneyDigest, US News, FinanceCharts. July 2026 data.",
        note_style
    ))
    story.append(Paragraph(
        "<b>Monthly Sector Trend:</b> <b>IT services and consulting surged</b> (ACN, CTSH, WDAY, WTW) on AI enterprise adoption. "
        "<b>Semiconductors equipment and memory had a brutal July</b> (KLAC, SNDK, MRVL) on valuation reset and "
        "fear of AI capex normalization. Marvell notably reversed in early August, demonstrating sector volatility.",
        body_style
    ))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"), spaceBefore=10, spaceAfter=10))

    # ── NEXT-DAY SCENARIOS ─────────────────────────────────────────────────
    story.append(Paragraph("4. Next-Day Scenarios — Thursday, August 6, 2026", h1_style))

    story.append(Paragraph(
        "Tomorrow's calendar: <b>Major earnings day</b> (577 companies reporting) headlined by "
        "<b>McDonald's (MCD), Datadog (DDOG), Celsius Holdings (CELH), ACM Research (ACMR), Unity (U)</b>. "
        "Background: Iran deal watch continues. Jobs Report (BLS) on <b>Friday Aug 7</b> at 8:30 AM ET looms large. "
        "No scheduled Fed speakers. Jobless claims data (weekly) due Thursday.",
        body_style
    ))

    scenarios = [
        {
            "title": "Catalyst 1: McDonald's (MCD) Earnings — Consumer Health Barometer",
            "bull": (
                "IF MCD beats on revenue + comps (same-store sales > +2%) and reaffirms or raises guidance → "
                "<b>Consumer discretionary (XLY) opens higher</b>, signals resilient lower-/middle-income "
                "spending despite elevated rates. SPY could add 0.2-0.4% at open. Fast-casual/restaurant peers "
                "(YUM, DRI, CMG recovery) rally. Mechanism: MCD is a global macro read; a beat signals "
                "consumer hasn't buckled."
            ),
            "bear": (
                "IF MCD misses comps or warns on traffic (US same-store sales negative) → "
                "<b>Consumer spending fear reignites</b>. XLY sells off 0.5-1%, ripples into retail stocks. "
                "Market could interpret this as rate-pressure demand destruction, pressuring SPY -0.3% to -0.5%. "
                "Chipotle's Salmonella trouble plus an MCD miss compounds consumer sector pain."
            ),
        },
        {
            "title": "Catalyst 2: Datadog (DDOG) Earnings — Cloud/AI Spend Signal",
            "bull": (
                "IF DDOG beats ARR/revenue (consensus ~$850M Q2) and raises FY guidance → "
                "<b>Confirms enterprises are not cutting cloud/observability budgets</b>. Sends a positive "
                "signal for cloud infrastructure (NET, SNOW, MDB, ESTC) and AI tool adoption. QQQ could "
                "rally 0.4-0.8% on open. After AMD/SpaceX disappointments, a clean cloud beat is exactly "
                "what Nasdaq needs to reverse Wednesday's 4-day-rally break."
            ),
            "bear": (
                "IF DDOG misses or guides below on RPO/net new ARR → "
                "<b>Third consecutive 'sell the news' earnings signal</b>, deepening fear that AI spending "
                "is not translating to software revenue at the pace expected. Cloud/SaaS names (CRM, WDAY, NOW) "
                "sell off sympathetically. QQQ drops further 0.5-1%. Validates thesis that hyperscaler capex "
                "doesn't lift software layer. Mechanism: DDOG's NTM P/S >25x — even a slight miss triggers "
                "multiple compression across the group."
            ),
        },
        {
            "title": "Catalyst 3: Iran / Strait of Hormuz Resolution (Ongoing)",
            "bull": (
                "IF a deal is formally announced overnight or pre-market (Bessent has said 'today or tomorrow') → "
                "<b>Oil crashes another 5-8%</b> (WTI toward $70-71). Airlines (UAL, DAL, AAL) surge 3-5% on "
                "fuel cost relief. Industrials and consumer discretionary continue higher. Dow extends record. "
                "But tech remains a net loser if the rotation OUT of safety/tech into cyclicals accelerates. "
                "SPY: +0.5-1.0%. QQQ: flat to +0.2% (cyclical rotation dampens tech gains)."
            ),
            "bear": (
                "IF Iran rejects terms or Trump escalates (military threat) → "
                "<b>Oil spikes back above $80</b> (safe-haven premium + supply-disruption risk). "
                "Airlines/transports sell off. Industrials give back yesterday's gains. Broader risk-off "
                "hits SPY -0.5% to -0.8%. Gold, defense stocks (LMT, RTX, NOC) bid higher. "
                "Mechanism: Strait handles ~20% of global oil flow — any credible disruption threat reprices risk."
            ),
        },
        {
            "title": "Catalyst 4: Weekly Jobless Claims (Thursday 8:30 AM ET) — Pre-Friday NFP Warm-Up",
            "bull": (
                "IF claims come in low (below 220K) → "
                "<b>Labor market still tight</b>. Mixed for markets: equity bulls read it as 'no recession,' "
                "but rate hawks read it as 'Fed stays higher for longer.' Net effect: SPY slightly positive "
                "(0.1-0.2%) as growth signal dominates. Bonds sell off slightly (yields +2-4 bps)."
            ),
            "bear": (
                "IF claims spike (above 260K) → "
                "<b>Sudden labor market deterioration signal</b>. Bond rally (yields -5-10 bps) would normally "
                "help equities, but a sharp claims miss could trigger recession fears ahead of Friday's NFP. "
                "SPY could dip -0.3% to -0.6%. This sets a cautious tone for the Jobs Report on Friday "
                "and could make investors defensive into the weekend. Mechanism: elevated claims = "
                "forward corporate earnings risk."
            ),
        },
    ]

    for s in scenarios:
        story.append(Paragraph(f"<b>{s['title']}</b>", h2_style))
        story.append(Paragraph(f"<b>Bull Case:</b> {s['bull']}", bullet_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(f"<b>Bear Case:</b> {s['bear']}", bullet_style))
        story.append(Spacer(1, 8))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"), spaceBefore=10, spaceAfter=10))

    # ── TRADE SUMMARY ─────────────────────────────────────────────────────────
    story.append(Paragraph("5. Possible Purchase Summary — Trade Ideas (EOD Aug 5 / Open Aug 6)", h1_style))

    story.append(Paragraph(
        "<i>Disclaimer: This is analytical research output only. No actual trades are placed or recommended "
        "by this system. All ideas are hypothetical and for informational purposes only. Consult a licensed "
        "financial advisor before acting on any analysis.</i>",
        ParagraphStyle("disclaimer", parent=note_style, textColor=colors.HexColor("#8B0000"))
    ))
    story.append(Spacer(1, 6))

    trade_data = [
        ["Action", "Ticker", "Thesis", "Key Risk", "Trigger"],
        [
            "BUY", "PLTR",
            "AI monetization leader; Rule-of-40 = 155%; US govt + "
            "commercial revenue both inflecting. Pullback from $162 "
            "peak on broader Nasdaq drag = entry opportunity. "
            "Q2: Revenue +93% YoY, guided FY to $8.15B.",
            "High valuation (P/S >50x); profit-taking after 29% pop; "
            "market-wide Nasdaq risk-off.",
            "Buy on dips toward $140-145; stop ~$128."
        ],
        [
            "BUY", "XLI",
            "Iran deal macro trade: Strait of Hormuz reopening "
            "benefits industrials (lower input costs, better supply "
            "chains). CAT, HON, GE all in XLI. Dow record = "
            "confirmation. ETF avoids single-stock earnings risk.",
            "Iran deal collapses or is delayed; oil spikes back. "
            "If Nasdaq selloff spreads to value, XLI could give back gains.",
            "Hold existing; add on confirmation of Hormuz deal. "
            "Target: prior highs +2-3%."
        ],
        [
            "BUY", "DDOG",
            "If DDOG beats tonight (earnings after-close Aug 5 or "
            "pre-open Aug 6): cloud observability still in secular "
            "growth. After AMD/SPCX sell-the-news, a clean DDOG beat "
            "resets Nasdaq direction. High NRR (>120%), ARR compounding.",
            "If DDOG misses or guides light — stock falls 15-25% "
            "(high multiple). Do NOT buy pre-earnings unless already "
            "in position.",
            "BUY ONLY on confirmed beat after-hours. Wait for "
            "earnings release before sizing."
        ],
        [
            "SELL/AVOID", "AMD",
            "Sold off 7% despite record beat. Pattern = sell-the-news. "
            "AI GPU competition from NVDA persists. Data center growth "
            "may be cannibalizing gross margin. Near-term momentum broken.",
            "AMD recovers if next catalyst (data center deal) announced.",
            "Avoid initiating; existing longs consider trimming "
            "into any bounce to $170-180."
        ],
        [
            "SELL/AVOID", "CMG",
            "Salmonella outbreak is real brand/traffic risk. "
            "Investors flee on food safety concerns. Traffic comps "
            "could take 1-2 quarters to recover. Expensive valuation "
            "gives no margin of safety on a miss.",
            "Outbreak is contained quickly and PR damage minimal.",
            "Avoid. Watch for confirmation of CDC resolution "
            "before re-entry. Support ~$48-50."
        ],
        [
            "WATCH", "MCD",
            "Pre-open Thursday. If earnings beat on same-store sales "
            "comps, MCD is a buy: defensive growth, dividend, and "
            "consumer resilience confirmation. $2.85 quarterly dividend "
            "(2.2% yield). Global diversification vs CMG.",
            "Consumer spending softens further; international comps "
            "hurt by strong USD.",
            "BUY if MCD beats comps + guides flat/up. "
            "Entry near $295-305 post-earnings open."
        ],
    ]

    trade_table = Table(trade_data, colWidths=[0.65*inch, 0.6*inch, 2.1*inch, 1.6*inch, 1.6*inch])
    trade_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0fff0"), colors.HexColor("#f0fff0"),
                                               colors.HexColor("#f0fff0"),
                                               colors.HexColor("#fff0f0"), colors.HexColor("#fff0f0"),
                                               colors.HexColor("#fffdf0")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("FONTNAME", (0, 1), (0, 3), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 1), (0, 3), colors.HexColor("#155724")),
        ("FONTNAME", (0, 4), (0, 5), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 4), (0, 5), colors.HexColor("#721c24")),
        ("FONTNAME", (0, 6), (0, 6), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 6), (0, 6), colors.HexColor("#856404")),
    ]))
    story.append(trade_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Key macro overlay:</b> With Jobs Report on Friday Aug 7, keep position sizes conservative "
        "into the weekend. A surprise NFP miss (especially with rising claims tomorrow) could trigger "
        "rapid re-pricing. Focus on AI/data infrastructure longs (PLTR, DDOG on confirm) and "
        "cyclical ETFs (XLI) over single high-multiple tech names heading into a binary macro event.",
        body_style
    ))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"), spaceBefore=12, spaceAfter=8))

    # Footer
    story.append(Paragraph(
        "Sources: TheStreet, Yahoo Finance, Benzinga, Baystreet, CNBC, TechTimes, 247WallSt, Spokesman-Review, "
        "Investrade, STL.News, MoneyDigest, US News, Trefis. Data: prices.csv (repo: ctedla-tarana/news). "
        "Generated automatically at 5 PM ET via Claude Code markets routine.",
        note_style
    ))
    story.append(Paragraph(
        f"Report generated: {REPORT_DATE}  |  Next report: 2026-08-06 (post-close)",
        ParagraphStyle("footer2", parent=note_style, alignment=TA_RIGHT)
    ))

    doc.build(story)
    print(f"PDF written to: {OUT_PATH}")


if __name__ == "__main__":
    rows = load_prices()
    stats = compute_stats(rows, REPORT_DATE)
    print(f"SPY: {stats['spy_today']} ({stats['spy_pct']:+.2f}%)  QQQ: {stats['qqq_today']} ({stats['qqq_pct']:+.2f}%)")
    print(f"SPY 1-yr: high={stats['spy_1y_high']}, low={stats['spy_1y_low']}, ret={stats['spy_1y_ret']:+.1f}%")
    print(f"QQQ 1-yr: high={stats['qqq_1y_high']}, low={stats['qqq_1y_low']}, ret={stats['qqq_1y_ret']:+.1f}%")
    build_pdf(stats)
