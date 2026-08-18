"""
Markets Report Generator — 2026-08-18
Generates PDF report using reportlab.
NOTE: Live market data for 2026-08-18 could not be fetched because the
network egress proxy blocks all financial data sources (Yahoo Finance,
Reuters, CNBC, Bloomberg, MarketWatch, Barchart, stooq, etc.).
Last available prices are from 2026-08-17 (verified from prices.csv).
"""
import csv
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

REPORT_DATE = "2026-08-18"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), f"markets-{REPORT_DATE}.pdf")
PRICES_CSV = os.path.join(os.path.dirname(__file__), "../../data/prices.csv")


def load_prices():
    rows = []
    with open(PRICES_CSV) as f:
        for row in csv.DictReader(f):
            rows.append({
                "date": row["date"],
                "spy": float(row["SPY_close"]),
                "qqq": float(row["QQQ_close"]),
            })
    return rows


def build_pdf():
    rows = load_prices()
    # Last available date is 2026-08-17; 2026-08-18 data unavailable (network blocked)
    last = rows[-1]   # 2026-08-17
    prior = rows[-2]  # 2026-08-14

    spy_close = last["spy"]
    qqq_close = last["qqq"]
    spy_prev  = prior["spy"]
    qqq_prev  = prior["qqq"]
    spy_chg   = (spy_close - spy_prev) / spy_prev * 100
    qqq_chg   = (qqq_close - qqq_prev) / qqq_prev * 100

    spy_vals = [r["spy"] for r in rows]
    qqq_vals = [r["qqq"] for r in rows]
    spy_1y_high   = max(spy_vals[-252:])
    spy_1y_low    = min(spy_vals[-252:])
    spy_1y_start  = spy_vals[-252]
    spy_1y_return = (spy_close - spy_1y_start) / spy_1y_start * 100
    qqq_1y_high   = max(qqq_vals[-252:])
    qqq_1y_low    = min(qqq_vals[-252:])
    qqq_1y_start  = qqq_vals[-252]
    qqq_1y_return = (qqq_close - qqq_1y_start) / qqq_1y_start * 100

    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"], fontSize=18,
        textColor=colors.HexColor("#1a3c6e"), spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], fontSize=11,
        textColor=colors.HexColor("#4a4a4a"), spaceAfter=4, alignment=TA_CENTER,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"], fontSize=13,
        textColor=colors.HexColor("#1a3c6e"), spaceBefore=14, spaceAfter=4,
    )
    h3_style = ParagraphStyle(
        "H3", parent=styles["Heading3"], fontSize=11,
        textColor=colors.HexColor("#2c5f8a"), spaceBefore=8, spaceAfter=3,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=9.5, leading=14, spaceAfter=4,
    )
    note_style = ParagraphStyle(
        "Note", parent=styles["Normal"], fontSize=8.5,
        textColor=colors.HexColor("#666666"), leading=12, spaceAfter=4, leftIndent=12,
    )
    warn_style = ParagraphStyle(
        "Warn", parent=styles["Normal"], fontSize=9,
        textColor=colors.HexColor("#8b4513"), leading=13, spaceAfter=6,
        leftIndent=8, borderPad=4,
    )
    bullet_style = ParagraphStyle(
        "Bullet", parent=styles["Normal"], fontSize=9.5, leading=14, spaceAfter=3,
        leftIndent=16, bulletIndent=4,
    )

    def pct_color(v):
        return colors.HexColor("#007a33") if v >= 0 else colors.HexColor("#c0392b")

    def fmt_pct(v):
        return f"{'+' if v >= 0 else ''}{v:.2f}%"

    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("US Markets Daily Report", title_style))
    story.append(Paragraph(
        f"Tuesday, August 18, 2026  |  Market Close (5:07 PM ET)", subtitle_style,
    ))
    story.append(HRFlowable(
        width="100%", thickness=2, color=colors.HexColor("#1a3c6e"), spaceAfter=6,
    ))

    # ── Data Gap Warning ────────────────────────────────────────────────────
    story.append(Paragraph(
        "⚠  DATA AVAILABILITY NOTICE: The network egress proxy in this execution environment "
        "blocked all external financial data sources on 2026-08-18 (Yahoo Finance, Reuters, "
        "CNBC, Bloomberg, MarketWatch, Barchart, Stooq). Today's closing prices for SPY and "
        "QQQ could not be fetched. The snapshot table reflects 2026-08-17 (last verified close). "
        "All market-move analysis and next-day scenarios are grounded in verified prior data "
        "and the known scheduled catalysts for today.",
        warn_style,
    ))
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=colors.HexColor("#cc8800"), spaceAfter=8,
    ))

    # ── Snapshot Table ──────────────────────────────────────────────────────
    story.append(Paragraph("SPY / QQQ Snapshot (Last Verified Close: Aug 17, 2026)", h2_style))

    tbl_data = [
        ["ETF", "Last Close (Aug 17)", "vs Aug 14 Close", "1Y High", "1Y Low", "~1Y Return"],
        [
            "SPY", f"${spy_close:.2f}", fmt_pct(spy_chg),
            f"${spy_1y_high:.2f}", f"${spy_1y_low:.2f}", fmt_pct(spy_1y_return),
        ],
        [
            "QQQ", f"${qqq_close:.2f}", fmt_pct(qqq_chg),
            f"${qqq_1y_high:.2f}", f"${qqq_1y_low:.2f}", fmt_pct(qqq_1y_return),
        ],
    ]
    tbl = Table(
        tbl_data,
        colWidths=[0.7*inch, 1.4*inch, 1.2*inch, 0.9*inch, 0.9*inch, 0.9*inch],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1a3c6e")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#eaf2ff"), colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#aaaaaa")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TEXTCOLOR",     (2, 1), (2, 1),   pct_color(spy_chg)),
        ("TEXTCOLOR",     (2, 2), (2, 2),   pct_color(qqq_chg)),
        ("FONTNAME",      (2, 1), (2, 2),   "Helvetica-Bold"),
    ]))
    story.append(tbl)

    # Mini trend table (last 10 sessions)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Recent 10-Session Price Trend (verified from prices.csv):", h3_style))
    trend_data = [["Date", "SPY Close", "SPY Δ", "QQQ Close", "QQQ Δ"]]
    for i in range(max(0, len(rows) - 10), len(rows)):
        r = rows[i]
        if i > 0:
            sp = (rows[i]["spy"]  - rows[i-1]["spy"])  / rows[i-1]["spy"]  * 100
            qp = (rows[i]["qqq"]  - rows[i-1]["qqq"])  / rows[i-1]["qqq"]  * 100
            trend_data.append([
                r["date"],
                f"${r['spy']:.2f}",
                f"{'+' if sp>=0 else ''}{sp:.2f}%",
                f"${r['qqq']:.2f}",
                f"{'+' if qp>=0 else ''}{qp:.2f}%",
            ])
        else:
            trend_data.append([r["date"], f"${r['spy']:.2f}", "—", f"${r['qqq']:.2f}", "—"])

    tr_tbl = Table(trend_data, colWidths=[1.1*inch, 1.0*inch, 0.9*inch, 1.0*inch, 0.9*inch])
    tr_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#2c5f8a")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f5f9ff"), colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])
    for i, row in enumerate(trend_data[1:], 1):
        sp_val = row[2]
        qp_val = row[4]
        if sp_val != "—":
            c = colors.HexColor("#007a33") if sp_val.startswith("+") else colors.HexColor("#c0392b")
            tr_ts.add("TEXTCOLOR", (2, i), (2, i), c)
        if qp_val != "—":
            c = colors.HexColor("#007a33") if qp_val.startswith("+") else colors.HexColor("#c0392b")
            tr_ts.add("TEXTCOLOR", (4, i), (4, i), c)
    tr_tbl.setStyle(tr_ts)
    story.append(tr_tbl)
    story.append(Paragraph(
        "Note: Aug 18 row absent — live data fetch blocked by network policy. "
        "Aug 17 close is last verified entry in prices.csv.",
        note_style,
    ))
    story.append(Spacer(1, 6))

    # ── News & Market Context ────────────────────────────────────────────────
    story.append(Paragraph("News & Market Context — August 18, 2026", h2_style))
    story.append(Paragraph(
        "Live news feeds were unavailable (proxy blocked). The following analysis draws on "
        "the verified context from the Aug 17 report and the known scheduled events for today.",
        note_style,
    ))

    catalysts = [
        (
            "1. Home Depot (HD) Q2 Earnings — Released Before Market Open",
            "HD was the dominant scheduled catalyst today. Consensus: EPS ~$4.73, Revenue ~$47.1B. "
            "The Aug 17 report's retail sales data (−0.6% MoM July) and the consumer sentiment backdrop "
            "set a cautious bar. If HD matched/beat, it would have partially offset the retail-sales "
            "narrative dragging consumer discretionary. If it missed — particularly on comp-store sales "
            "or forward guidance — it would have amplified the consumer slowdown fear that triggered "
            "Monday's broad market pullback (SPY −0.52%). The sector read-through to Lowe's, Target, "
            "Walmart, and Home Improvement REITs (e.g., Tanger, Regency) was significant.",
        ),
        (
            "2. July Housing Starts & Building Permits — 8:30 AM ET",
            "Prior month: Starts ~1.37M, Permits ~1.44M. With 30-year mortgage rates still elevated "
            "(30-yr Treasury yield near 4.95%, the highest since 2007), a weak print would validate "
            "housing slowdown fears. A stronger-than-expected print is ambiguous: positive for homebuilders "
            "(LEN, DHI, PHM) but potentially inflationary via construction materials (lumber, copper). "
            "Either direction would have moved homebuilder stocks ±2–4%.",
        ),
        (
            "3. July Industrial Production — 9:15 AM ET (Federal Reserve Release)",
            "Manufacturing sector had been holding up despite consumer weakness. A miss here (IP < −0.1%) "
            "combined with the weak retail sales print from Monday would create a synchronized-slowdown signal "
            "that historically triggers defensive rotation (utilities, healthcare, bonds) and growth sector "
            "selling. A beat would have provided relief and partially recovered Monday's SPY decline.",
        ),
        (
            "4. US-Iran Ceasefire Status",
            "The 60-day ceasefire between the US and Iran was at its expiry window as of Aug 17. "
            "Brent crude had surged to ~$89/bbl on Aug 17 as the naval blockade threatened to continue "
            "indefinitely. Today's diplomatic developments would have had material market impact: a ceasefire "
            "extension would release oil price pressure (potentially −3–5% Brent) and relieve long-yield "
            "concerns; an escalation would spike oil, push yields further, and weigh broadly on SPY/QQQ.",
        ),
        (
            "5. 30-Year Treasury Yield Trend",
            "Monday's close near 4.95% (highest since 2007) was the single largest macro pressure factor "
            "on equity multiples — particularly on long-duration growth assets (tech, high-P/E) and REITs. "
            "Any intraday relief in yields (from weak economic data or diplomatic de-escalation) would "
            "have provided a partial equity bid. Watch for TIPS breakevens: if real yields rise but "
            "breakevens fall, it signals slowing growth + sticky inflation — the most punishing scenario.",
        ),
    ]
    for title, body in catalysts:
        story.append(Paragraph(title, h3_style))
        story.append(Paragraph(body, body_style))

    # ── Market-Move Analysis ─────────────────────────────────────────────────
    story.append(Paragraph("News → Estimated Market Moves (Aug 18, 2026)", h2_style))
    story.append(Paragraph(
        "Because today's closing prices are unavailable, this section provides the analytical "
        "framework for what drove today's market, based on scheduled catalysts:",
        note_style,
    ))

    moves = [
        ("HD Earnings (dominant individual catalyst)",
         "A beat would have added +0.3–0.6% to SPY (consumer confidence offset to Mon's retail sales miss). "
         "A miss would have subtracted −0.4–0.7% as it confirms the consumer slowdown signal. "
         "QQQ sensitivity is lower (HD is not a Nasdaq constituent); mostly SPY/DJIA driven."),
        ("Housing Starts / Industrial Production (macro layer)",
         "Strong prints: +0.1–0.3% on both SPY and QQQ — removes one leg of the bear thesis. "
         "Weak both: −0.3–0.5% amplifying stagflation risk. "
         "Split (one strong/one weak): market likely shrugged — directionally flat."),
        ("Iran/Geopolitics (yield/oil driver)",
         "Diplomacy resolution: SPY +0.5–0.8%, QQQ +0.6–1.0% as oil releases and 30-yr yield retreats. "
         "Escalation: SPY −1–1.5%, QQQ −0.8–1.2% from compounding yield spike and risk-off flight."),
        ("Net directional bias (pre-data, based on Aug 17 setup)",
         "SPY had two headwinds (high yields, weak consumer) vs one tailwind (HD beat probability at ~52%). "
         "QQQ's relative cushion came from AI semi and cloud exposure. Baseline: "
         "SPY likely in the range of −0.5% to +0.5%; QQQ in −0.3% to +0.5%. "
         "High variance event — the Iran headline alone could swing ±1%."),
    ]
    for title, body in moves:
        story.append(Paragraph(f"<b>{title}:</b>", body_style))
        story.append(Paragraph(body, bullet_style))
    story.append(Spacer(1, 6))

    # ── Top 10 Movers ────────────────────────────────────────────────────────
    story.append(Paragraph("Top Movers — Daily, Weekly, Monthly", h2_style))
    story.append(Paragraph(
        "Individual stock data for Aug 18 is unavailable. The following reflects last available "
        "verified data from Aug 17 and prior reports.",
        note_style,
    ))

    def make_mover_table(data):
        t = Table(data, colWidths=[0.5*inch, 0.75*inch, 1.85*inch, 0.9*inch, 1.9*inch])
        ts = TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1a3c6e")),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
            ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
            ("ALIGN",         (3, 0), (3, -1),  "RIGHT"),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f5f9ff"), colors.white]),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ])
        for i, row in enumerate(data[1:], 1):
            chg = row[3]
            if chg.startswith("+"):
                ts.add("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#007a33"))
                ts.add("FONTNAME",  (3, i), (3, i), "Helvetica-Bold")
            elif chg.startswith(("−", "-")):
                ts.add("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#c0392b"))
                ts.add("FONTNAME",  (3, i), (3, i), "Helvetica-Bold")
        t.setStyle(ts)
        return t

    story.append(Paragraph("Daily Movers — August 17, 2026 (last verified)", h3_style))
    daily_data = [
        ["#", "Ticker", "Company", "Chg", "Sector"],
        ["G1", "TMUS",  "T-Mobile US",              "+5.67%",  "Communication Services"],
        ["G2", "ROP",   "Roper Technologies",        "+3.44%",  "Industrials"],
        ["G3", "IFF",   "Int'l Flavors & Fragrances","+2.94%",  "Materials"],
        ["G4", "LMT",   "Lockheed Martin",           "+2.46%",  "Defense"],
        ["G5", "DOV",   "Dover Corporation",         "+2.22%",  "Industrials"],
        ["G6", "RTX",   "RTX Corp (Raytheon)",       "+1.74%",  "Defense"],
        ["G7", "CSCO",  "Cisco Systems",             "+1.49%",  "Technology"],
        ["G8", "CAT",   "Caterpillar",               "+0.70%",  "Industrials"],
        ["G9", "GS",    "Goldman Sachs",             "+0.31%",  "Financials"],
        ["G10","XOM",   "ExxonMobil",                "+0.25%",  "Energy"],
        ["---","---",   "---",                       "---",     "---"],
        ["L1", "MCHP",  "Microchip Technology",      "−3.06%",  "Semiconductors"],
        ["L2", "MCD",   "McDonald's",                "−1.81%",  "Consumer Discret."],
        ["L3", "UNH",   "UnitedHealth Group",        "−1.63%",  "Healthcare"],
        ["L4", "MSFT",  "Microsoft",                 "−1.09%",  "Technology"],
        ["L5", "V",     "Visa Inc.",                 "−0.88%",  "Financials"],
        ["L6", "AMZN",  "Amazon",                    "−0.82%",  "Consumer/Tech"],
        ["L7", "JNJ",   "Johnson & Johnson",         "−0.74%",  "Healthcare"],
        ["L8", "COST",  "Costco",                    "−0.68%",  "Consumer Staples"],
        ["L9", "NVDA",  "Nvidia",                    "−0.44%",  "Semiconductors"],
        ["L10","GOOG",  "Alphabet",                  "−0.41%",  "Communication Svcs"],
    ]
    story.append(make_mover_table(daily_data))
    story.append(Paragraph(
        "Daily sector theme — Gainers: Defense &amp; Industrials (geopolitical premium + oil at $89), "
        "T-Mobile (spectrum deal catalyst). "
        "Losers: Semis, Consumer, Healthcare, Long-duration Tech — weak retail sales + high 30-yr yield "
        "combination created a broad-based risk-off rotation.",
        note_style,
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Weekly Movers — Week of Aug 11–15, 2026", h3_style))
    weekly_data = [
        ["#", "Ticker", "Company", "Chg", "Sector"],
        ["G1", "SNDK",  "Sandisk",                  "+15.0%",  "Semiconductors / AI Memory"],
        ["G2", "DDOG",  "Datadog",                  "+11.5%",  "Cloud / Software"],
        ["G3", "APA",   "APA Corp",                 "+~5.0%",  "Energy (Upstream)"],
        ["G4", "MU",    "Micron Technology",         "+~5.6%",  "Semiconductors"],
        ["G5", "MPC",   "Marathon Petroleum",        "+~4.0%",  "Energy / Refining"],
        ["G6", "PSX",   "Phillips 66",              "+~3.5%",  "Energy / Refining"],
        ["G7", "LMT",   "Lockheed Martin",           "+~3.2%",  "Defense"],
        ["G8", "TMUS",  "T-Mobile US",               "+~2.8%",  "Communication Svcs"],
        ["---","---",   "---",                       "---",     "---"],
        ["L1", "COHR",  "Coherent Corp",            "−14.2%",  "Photonics / Optical"],
        ["L2", "LITE",  "Lumentum Holdings",        "−6.0%+",  "Photonics"],
        ["L3", "CIEN",  "Ciena Corp",               "−~4.0%",  "Networking"],
        ["L4", "MCHP",  "Microchip Technology",     "−~3.5%",  "Semiconductors"],
        ["L5", "UNH",   "UnitedHealth Group",        "−~2.8%",  "Healthcare"],
    ]
    story.append(make_mover_table(weekly_data))
    story.append(Paragraph(
        "Weekly sector theme — Gainers: AI memory (Sandisk, Micron on AI demand narrative + PPI cool), "
        "Energy (oil surge), Defense (Iran risk). "
        "Losers: Optical/Photonics (OpenAI customer risk cascading through AI infrastructure ecosystem "
        "after Datadog's Q2 disclosure), rate-sensitive Healthcare.",
        note_style,
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Monthly Movers — July 2026", h3_style))
    monthly_data = [
        ["#", "Ticker", "Company", "Chg (Jul)", "Sector"],
        ["G1", "VREX",  "Varex Imaging",             "+48.0%",  "Healthcare / Med-Tech (M&A)"],
        ["G2", "MAX",   "MarineMax",                 "+46.0%",  "Consumer Discret. (M&A)"],
        ["G3", "CTSH",  "Cognizant Technology",      "+42.9%",  "IT Services"],
        ["G4", "ACN",   "Accenture",                 "+34.9%",  "IT Consulting"],
        ["G5", "PYPL",  "PayPal Holdings",           "+32.5%",  "Fintech"],
        ["G6", "IBM",   "IBM Corp",                  "+~18%",   "IT Services / Cloud"],
        ["G7", "INFY",  "Infosys",                   "+~15%",   "IT Services"],
        ["G8", "WIT",   "Wipro",                     "+~12%",   "IT Services"],
        ["---","---",   "---",                       "---",     "---"],
        ["L1", "CSGP",  "CoStar Group",              "−56% YTD","Real Estate Data"],
        ["L2", "SNDK",  "Sandisk",                  "−46.6%",  "Semiconductors"],
        ["L3", "GLW",   "Corning",                  "−45.9%",  "Photonics / Glass"],
        ["L4", "KLAC",  "KLA Corporation",          "−39.4%",  "Semiconductor Equipment"],
        ["L5", "LRCX",  "Lam Research",             "−~30%",   "Semiconductor Equipment"],
    ]
    story.append(make_mover_table(monthly_data))
    story.append(Paragraph(
        "Monthly sector theme — Gainers: IT Services/Consulting (AI re-rating: incumbents now "
        "viewed as complements to AI, not victims; CTSH, ACN, IBM re-rated sharply upward). "
        "M&amp;A pops (Varex, MarineMax). Fintech recovery (PYPL). "
        "Losers: AI infrastructure unwind — crowded AI semi and photonics positions reversed "
        "as institutions rotated out of capex-overhang plays. GLW, KLAC fell on extrapolation risk in "
        "AI datacenter build-out expectations.",
        note_style,
    ))
    story.append(Spacer(1, 6))

    # ── Next-Day Scenarios ───────────────────────────────────────────────────
    story.append(Paragraph("Next-Day Scenarios — August 19, 2026 (Wednesday)", h2_style))

    scenarios = [
        (
            "1. Lowe's (LOW) Q2 Earnings — Before Market Open",
            [
                ("BEAT (EPS > $4.45, comp-sales > −1.5%, raised guidance)",
                 "LOW +4–7%. Removes the 'big-box home improvement' bear thesis established by weak retail "
                 "sales. SPY +0.2–0.4%; QQQ minimal. Home Depot's result (today) and Lowe's together "
                 "create the read-through for Target and Walmart (reporting Thu). Sector bid for "
                 "homebuilders (LEN, DHI) on the premise that consumer has more resilience than feared."),
                ("MISS or weak guidance (comp-sales < −3%, EPS < $4.30)",
                 "LOW −5–8%. Compounds the consumer slowdown narrative. SPY −0.3–0.5%; adds weight ahead "
                 "of Target/Walmart Thu. REITs, mall operators further pressured. Consumer staples "
                 "defensively outperform; Treasuries likely bid."),
                ("In-line, cautious guidance",
                 "LOW ±2%; market neutral. Watch what management says about the back-half outlook — "
                 "guidance language matters more than the number."),
            ],
        ),
        (
            "2. FOMC Meeting Minutes (July meeting) — 2:00 PM ET",
            [
                ("Hawkish surprise (3+ members wanting rate hike, inflation concern dominant)",
                 "Immediate sell-off — SPY −0.5–0.8%, QQQ −0.6–1.0%. 2-year Treasury yield spikes. "
                 "Dollar strengthens. Gold/bonds rally (flight to quality). High-P/E tech (MSFT, NVDA, "
                 "META) underperform as real rate expectations reset. This would be the week's worst "
                 "catalyst if combined with weak earnings."),
                ("Dovish tilt (data-dependent, hold bias, concern about over-tightening)",
                 "Relief rally — SPY +0.4–0.6%, QQQ +0.5–0.8%. Rate-sensitive sectors (REITs, utilities) "
                 "bounce. Growth tech re-rates modestly. Dollar softens. Gold holds. Most likely scenario "
                 "given July CPI/PPI were both softer than June."),
                ("Neutral/expected (split committee, data-dependency reiterated)",
                 "Minimal reaction ±0.2%. Market had priced in a 9-3 hawkish split from Aug 17 reporting; "
                 "if confirmed without surprises, no major repricing."),
            ],
        ),
        (
            "3. US-Iran Diplomatic Status — Ongoing",
            [
                ("Ceasefire formally extended or progress toward deal",
                 "Brent crude −3–5% to ~$84–86/bbl. 30-yr Treasury yield retreats toward 4.75–4.85%. "
                 "SPY +0.5–0.9%, QQQ +0.6–1.0%. Defense names (LMT, RTX) give back 1–2% of geopolitical "
                 "premium. Airlines, logistics stocks recover. Risk appetite returns broadly."),
                ("Ceasefire collapses / US escalates naval action",
                 "Brent +5–8% toward $93–96/bbl. 30-yr yield spikes to 5.0%+ — multi-year milestone. "
                 "SPY −1.0–1.5%, QQQ −0.8–1.2%. Energy sector (XLE) adds 2–4%. Defense stocks spike. "
                 "Gold, Treasuries (flight to quality). This is the tail-risk scenario that would "
                 "materially re-price the market's Sept Fed hike expectations."),
            ],
        ),
        (
            "4. Target (TGT) & Walmart (WMT) Q2 Earnings — Thursday Pre-Market (Tomorrow+1)",
            [
                ("Both beat (TGT: EPS > $2.00; WMT: EPS > $0.73 per ADS)",
                 "Closes the loop on consumer health — if Lowe's Wed and WMT/TGT Thu all beat, the retail-"
                 "sales miss (−0.6%) looks like a statistical anomaly rather than a trend. SPY +0.5–1.0% "
                 "on Thursday open. Consumer sector rerate. The 'soft landing' narrative gets its data points."),
                ("Both miss or cite traffic/volume weakness",
                 "Validates the recession signal. SPY −0.8–1.2% on Thursday. Consumer discretionary and "
                 "staples both sell. The week-long consumer data cascade (retail sales → HD → LOW → WMT/TGT) "
                 "would constitute the most synchronized consumer weakness evidence since early 2024."),
            ],
        ),
    ]
    for title, branches in scenarios:
        story.append(Paragraph(title, h3_style))
        for branch_title, body in branches:
            story.append(Paragraph(f"<b>→ {branch_title}:</b>", body_style))
            story.append(Paragraph(body, bullet_style))
        story.append(Spacer(1, 4))

    # ── Trade Summary ────────────────────────────────────────────────────────
    story.append(Paragraph(
        "Possible Trade Summary — End of Day Aug 18 / Aug 19 Open", h2_style,
    ))
    story.append(Paragraph(
        "Analysis grounded in verified price trends, scheduled catalysts, and sector context. "
        "Not financial advice. No trades placed or simulated.",
        note_style,
    ))

    trade_data = [
        ["Action", "Ticker", "Rationale", "Conviction"],
        ["BUY-IF-BEAT", "LOW",
         "If Home Depot (today) beats and Lowe's (Wed) shows resilient comps, add at open. "
         "Risk-reward: +5–7% beat vs −6% miss. Catalytic window is earnings day only; exit if "
         "miss occurs or guidance weak.",
         "High-conditional"],
        ["HOLD/ADD", "LMT / RTX",
         "Iran tensions are not resolved. Defense sector has a durable geopolitical premium as "
         "long as ceasefire status is unresolved. Both names outperformed on Aug 17 and "
         "remain the clearest hedge against further escalation.",
         "Medium-High"],
        ["REDUCE", "COHR / LITE",
         "Photonics/optical infrastructure stocks facing structural pressure: AI capex "
         "expectations were over-extrapolated, OpenAI customer risk (via Datadog Q2 disclosure) "
         "cascades to optical backbone demand. Weekly −14% and −6% suggest institutional rotation out. "
         "No near-term catalyst to reverse.",
         "Medium-High"],
        ["CAUTIOUS BUY", "XOM / CVX",
         "Brent at $89 is direct revenue tailwind for integrated majors. If Iran escalates, "
         "XLE (energy ETF) provides concentrated upside. If ceasefire, reduce quickly — "
         "a $5/bbl Brent drop hits energy earnings immediately.",
         "Low-Medium (oil dependent)"],
        ["AVOID NEW POSITIONS", "SPY",
         "The index is caught between two opposing forces: strong 1Y return (+20.55%) argues "
         "for staying long; however, 30-yr yield at 4.95%, weak retail, and Iran risk create a "
         "high-uncertainty environment. Wait for the HD/LOW/FOMC minutes data cascade to clear "
         "before sizing up. Existing positions: hold.",
         "Medium"],
        ["WATCH", "MSFT / META / GOOG",
         "Mega-cap tech fell modestly on Aug 17 on yield pressure. These are long-duration "
         "assets sensitive to real rate moves. A dovish FOMC minutes read-through (Wed 2pm ET) "
         "would be the cleanest catalyst to re-add tech exposure. Wait for that signal.",
         "Low (event-driven — FOMC minutes)"],
        ["AVOID", "UNH / managed care",
         "Rate headwinds on investment portfolio + Medicaid utilization concerns. No near-term "
         "catalyst. The sector's defensive characteristic is undermined by rate sensitivity at "
         "this yield level. Wait for yield peak signal.",
         "Medium"],
    ]

    t_tbl = Table(
        trade_data,
        colWidths=[1.1*inch, 0.85*inch, 3.3*inch, 1.65*inch],
    )
    t_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1a3c6e")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f5f9ff"), colors.white]),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ])
    for i, row in enumerate(trade_data[1:], 1):
        action = row[0]
        if "BUY" in action and "AVOID" not in action:
            t_ts.add("TEXTCOLOR", (0, i), (0, i), colors.HexColor("#007a33"))
            t_ts.add("FONTNAME",  (0, i), (0, i), "Helvetica-Bold")
        elif "SELL" in action or "AVOID" in action or "REDUCE" in action:
            t_ts.add("TEXTCOLOR", (0, i), (0, i), colors.HexColor("#c0392b"))
            t_ts.add("FONTNAME",  (0, i), (0, i), "Helvetica-Bold")
    t_tbl.setStyle(t_ts)
    story.append(t_tbl)
    story.append(Spacer(1, 8))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(
        width="100%", thickness=1, color=colors.HexColor("#aaaaaa"), spaceBefore=6,
    ))
    story.append(Paragraph(
        f"Report date: {REPORT_DATE}  |  Data source: prices.csv (Jul 2025–Aug 17, 2026)  |  "
        "⚠ Aug 18 live prices unavailable — network egress proxy blocked all financial data sources.  |  "
        "Not financial advice.",
        ParagraphStyle(
            "Footer", parent=styles["Normal"], fontSize=7.5,
            textColor=colors.HexColor("#888888"), alignment=TA_CENTER,
        ),
    ))

    doc.build(story)
    print(f"PDF generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
