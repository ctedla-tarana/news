"""
Markets Report Generator - 2026-08-17
Generates PDF report using reportlab
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

REPORT_DATE = "2026-08-17"
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
    today = rows[-1]
    prior = rows[-2]

    spy_close = today["spy"]
    qqq_close = today["qqq"]
    spy_prev  = prior["spy"]
    qqq_prev  = prior["qqq"]
    spy_chg   = (spy_close - spy_prev) / spy_prev * 100
    qqq_chg   = (qqq_close - qqq_prev) / qqq_prev * 100

    spy_vals = [r["spy"] for r in rows]
    qqq_vals = [r["qqq"] for r in rows]
    spy_1y_high   = max(spy_vals)
    spy_1y_low    = min(spy_vals)
    spy_1y_return = (spy_close - rows[0]["spy"]) / rows[0]["spy"] * 100
    qqq_1y_high   = max(qqq_vals)
    qqq_1y_low    = min(qqq_vals)
    qqq_1y_return = (qqq_close - rows[0]["qqq"]) / rows[0]["qqq"] * 100

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
        "Title", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#1a3c6e"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], fontSize=11, textColor=colors.HexColor("#4a4a4a"),
        spaceAfter=4, alignment=TA_CENTER,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"], fontSize=13, textColor=colors.HexColor("#1a3c6e"),
        spaceBefore=14, spaceAfter=4,
    )
    h3_style = ParagraphStyle(
        "H3", parent=styles["Heading3"], fontSize=11, textColor=colors.HexColor("#2c5f8a"),
        spaceBefore=8, spaceAfter=3,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=9.5, leading=14, spaceAfter=4,
    )
    note_style = ParagraphStyle(
        "Note", parent=styles["Normal"], fontSize=8.5, textColor=colors.HexColor("#666666"),
        leading=12, spaceAfter=4, leftIndent=12,
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

    # ── Header ─────────────────────────────────────────────────────────────
    story.append(Paragraph("US Markets Daily Report", title_style))
    story.append(Paragraph(f"Monday, August 17, 2026  |  Market Close", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3c6e"), spaceAfter=10))

    # ── Snapshot Table ─────────────────────────────────────────────────────
    story.append(Paragraph("SPY / QQQ Snapshot", h2_style))

    tbl_data = [
        ["ETF", "Today's Close*", "vs Prev Close", "1Y High", "1Y Low", "~1Y Return"],
        [
            "SPY", f"${spy_close:.2f}", fmt_pct(spy_chg),
            f"${spy_1y_high:.2f}", f"${spy_1y_low:.2f}", fmt_pct(spy_1y_return),
        ],
        [
            "QQQ", f"${qqq_close:.2f}", fmt_pct(qqq_chg),
            f"${qqq_1y_high:.2f}", f"${qqq_1y_low:.2f}", fmt_pct(qqq_1y_return),
        ],
    ]
    tbl = Table(tbl_data, colWidths=[0.7*inch, 1.1*inch, 1.1*inch, 1.0*inch, 1.0*inch, 1.0*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c6e")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#eaf2ff"), colors.white]),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#aaaaaa")),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TEXTCOLOR",  (2, 1), (2, 1), pct_color(spy_chg)),
        ("TEXTCOLOR",  (2, 2), (2, 2), pct_color(qqq_chg)),
        ("FONTNAME",   (2, 1), (2, 2), "Helvetica-Bold"),
    ]))
    story.append(tbl)
    story.append(Paragraph(
        "* SPY and QQQ close prices estimated from official index levels (S&amp;P 500: 7,745.06; Nasdaq Composite: 26,644.91) "
        "as direct ETF feed was unavailable; prior-day prices from verified session data.",
        note_style,
    ))
    story.append(Spacer(1, 6))

    # ── Market Overview ────────────────────────────────────────────────────
    story.append(Paragraph("Market Overview — August 17, 2026", h2_style))
    overview_items = [
        ("S&P 500", "7,745.06", "−0.52%", "Third consecutive weekly gain capped last Friday; today erased early gains."),
        ("Dow Jones", "53,459.78", "−0.51% (−272.63 pts)", "Broad weakness; defensive names and financials dragged."),
        ("Nasdaq Composite", "26,644.91", "−0.32%", "Tech resilience cushioned the index; only 151/500 S&amp;P stocks advanced."),
        ("30-Year Treasury Yield", "~4.95%", "Highest since 2007", "Rising yields pressured rate-sensitive sectors."),
        ("Brent Crude", "~$89/bbl", "+", "US-Iran tensions flared as 60-day ceasefire expiry loomed."),
    ]
    ov_data = [["Index / Asset", "Level", "Change", "Note"]] + [list(r) for r in overview_items]
    ov_tbl = Table(ov_data, colWidths=[1.5*inch, 1.1*inch, 1.4*inch, 2.9*inch])
    ov_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5f8a")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
        ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f9ff"), colors.white]),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(ov_tbl)
    story.append(Spacer(1, 8))

    # ── News → Today's Moves ───────────────────────────────────────────────
    story.append(Paragraph("News → Today's Market Moves", h2_style))

    catalysts = [
        (
            "1. US-Iran Tensions & Oil Surge (Dominant Negative)",
            "The 60-day US-Iran ceasefire window neared expiry with the US signalling its naval blockade of Iranian "
            "ports could continue 'indefinitely.' Brent crude jumped to ~$89/bbl, driving the 30-year Treasury yield "
            "to its highest level since 2007. Rising long rates compress equity multiples directly — the SPY's "
            "−0.52% move was largely explained here. Energy stocks (XOM, CVX) bucked the trend with modest gains "
            "as oil is their revenue tailwind. Defense names (LMT +2.46%, RTX +1.74%) outperformed on elevated "
            "geopolitical premium.",
        ),
        (
            "2. Weak Retail Sales (Negative for Consumer/Retail)",
            "July retail sales fell a surprising −0.6% MoM (consensus: −0.2%). Excluding autos, sales fell −0.3% "
            "(vs +0.2% expected). The control group — the GDP-input measure — fell −0.4%, the worst print since "
            "January 2025. This spooked the market ahead of a heavy retail earnings week (Home Depot Tue, Lowe's "
            "Wed, Target/Walmart Thu). Consumer discretionary and staples lagged; McDonald's (−1.81%) and broader "
            "consumer names sold off on recession-demand fears.",
        ),
        (
            "3. Persistent Rate Anxiety (Negative Across Sectors)",
            "Softer July CPI/PPI earlier in the week had trimmed September hike odds to 30%, but today's "
            "inflationary oil backdrop and weak consumer data kept the Fed's path uncertain. The July FOMC "
            "minutes (released Wednesday) had a 9-3 hawkish split — three members wanted a hike. UnitedHealth "
            "(−1.63%) and rate-sensitive sectors (utilities, REITs) underperformed. Microsoft (−1.09%) was "
            "emblematic of the 'long-duration asset' pressure when real yields spike.",
        ),
        (
            "4. Tech & Telecom Pockets of Strength (Partial Offset)",
            "T-Mobile (TMUS +5.67%) surged on strong subscriber data and a potential spectrum deal. "
            "Roper Technologies (ROP +3.44%) and IFF (+2.94%) recovered on idiosyncratic catalysts. "
            "The chip complex held in — Sandisk and Micron's AI-demand narrative remains intact — limiting "
            "QQQ's decline to a more modest −0.32% vs SPY's −0.52%.",
        ),
    ]
    for title, body in catalysts:
        story.append(Paragraph(title, h3_style))
        story.append(Paragraph(body, body_style))

    # ── Top 10 Movers ─────────────────────────────────────────────────────
    story.append(Paragraph("Top Movers — Daily, Weekly, Monthly", h2_style))

    story.append(Paragraph("Daily Movers (August 17, 2026)", h3_style))
    daily_data = [
        ["Rank", "Ticker", "Company", "Change", "Sector"],
        ["G1", "TMUS",   "T-Mobile US",              "+5.67%",  "Communication Svcs"],
        ["G2", "ROP",    "Roper Technologies",        "+3.44%",  "Industrials"],
        ["G3", "IFF",    "Int'l Flavors & Frag.",     "+2.94%",  "Materials"],
        ["G4", "LMT",    "Lockheed Martin",           "+2.46%",  "Defense/Industrials"],
        ["G5", "DOV",    "Dover Corporation",         "+2.22%",  "Industrials"],
        ["G6", "RTX",    "RTX Corp (Raytheon)",       "+1.74%",  "Defense/Industrials"],
        ["G7", "CSCO",   "Cisco Systems",             "+1.49%",  "Technology"],
        ["G8", "CAT",    "Caterpillar",               "+0.70%",  "Industrials"],
        ["G9", "GS",     "Goldman Sachs",             "+0.31%",  "Financials"],
        ["---", "---",   "---",                       "---",     "---"],
        ["L1", "MCHP",   "Microchip Technology",      "−3.06%",  "Semiconductors"],
        ["L2", "MCD",    "McDonald's",                "−1.81%",  "Consumer Discret."],
        ["L3", "UNH",    "UnitedHealth Group",        "−1.63%",  "Healthcare"],
        ["L4", "MSFT",   "Microsoft",                 "−1.09%",  "Technology"],
    ]
    def daily_tbl_style(d):
        ts = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c6e")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
            ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
            ("ALIGN",      (3, 0), (3, -1), "RIGHT"),
            ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f9ff"), colors.white]),
            ("TOPPADDING",  (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ])
        for i, row in enumerate(d[1:], 1):
            chg = row[3]
            if chg.startswith("+"):
                ts.add("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#007a33"))
                ts.add("FONTNAME",  (3, i), (3, i), "Helvetica-Bold")
            elif chg.startswith("−") or chg.startswith("-"):
                ts.add("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#c0392b"))
                ts.add("FONTNAME",  (3, i), (3, i), "Helvetica-Bold")
        return ts

    d_tbl = Table(daily_data, colWidths=[0.5*inch, 0.7*inch, 1.8*inch, 0.9*inch, 2.0*inch])
    d_tbl.setStyle(daily_tbl_style(daily_data))
    story.append(d_tbl)
    story.append(Paragraph(
        "Sector theme — Daily Gainers: Defense &amp; Industrials dominated (geopolitical premium + oil). "
        "T-Mobile was an outlier on its own catalyst. Losers: Consumer/Healthcare/Long-duration tech retreated "
        "on weak retail sales and high real yields.",
        note_style,
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Weekly Movers (Week of Aug 11–14, 2026)", h3_style))
    weekly_data = [
        ["Rank", "Ticker", "Company", "Change", "Sector"],
        ["G1", "DDOG",   "Datadog",                  "+11.5%",  "Cloud/Software"],
        ["G2", "APA",    "APA Corp",                 "+~5%",    "Energy"],
        ["G3", "MPC",    "Marathon Petroleum",        "+~4%",    "Energy/Refining"],
        ["G4", "SNDK",   "Sandisk",                  "+15%†",   "Semiconductors/AI"],
        ["G5", "MU",     "Micron Technology",         "+~5.6%",  "Semiconductors"],
        ["---", "---",   "---",                       "---",     "---"],
        ["L1", "COHR",   "Coherent Corp",             "−14.2%",  "Photonics"],
        ["L2", "LITE",   "Lumentum Holdings",         "−6%+",    "Photonics"],
        ["L3", "CIEN",   "Ciena",                     "−~4%",    "Networking"],
        ["L4", "DDOG",   "Datadog (prior wk)",        "−19%",    "Cloud/Software (Q2 headwind)"],
    ]
    w_tbl = Table(weekly_data, colWidths=[0.5*inch, 0.7*inch, 1.8*inch, 0.9*inch, 2.0*inch])
    w_tbl.setStyle(daily_tbl_style(weekly_data))
    story.append(w_tbl)
    story.append(Paragraph(
        "† Sandisk +15% on Aug 13 driven by PPI-cool euphoria and AI memory demand narrative. "
        "Weekly sector trend — Gainers: AI-adjacent memory chips, energy. Losers: Optical/photonics (AI infrastructure selloff on OpenAI customer risk disclosed by DDOG). "
        "DDOG itself was a paradox — surged weekly but was the prior week's largest loser after its Q2 call.",
        note_style,
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Monthly Movers (July 2026)", h3_style))
    monthly_data = [
        ["Rank", "Ticker", "Company", "Chg (Jul)", "Sector"],
        ["G1", "CTSH",   "Cognizant Technology",     "+42.9%",  "IT Services"],
        ["G2", "ACN",    "Accenture",                "+34.9%",  "IT Consulting"],
        ["G3", "PYPL",   "PayPal Holdings",           "+32.5%",  "Fintech"],
        ["G4", "MarineMax", "MarineMax",              "+46%",    "Consumer Discretionary (M&A)"],
        ["G5", "VREX",   "Varex Imaging",             "+48%",    "Healthcare (M&A)"],
        ["---", "---",   "---",                       "---",     "---"],
        ["L1", "SNDK",   "Sandisk",                  "−46.6%",  "Semiconductors (unwind)"],
        ["L2", "GLW",    "Corning",                  "−45.9%",  "Photonics/Glass"],
        ["L3", "KLAC",   "KLA Corporation",          "−39.4%",  "Semiconductor Equipment"],
        ["L4", "CSGP",   "CoStar Group",             "−56% YTD","Real Estate Data"],
    ]
    m_tbl = Table(monthly_data, colWidths=[0.5*inch, 0.8*inch, 1.7*inch, 0.9*inch, 2.0*inch])
    m_tbl.setStyle(daily_tbl_style(monthly_data))
    story.append(m_tbl)
    story.append(Paragraph(
        "Monthly sector trend — Gainers: IT Services/Consulting (AI-disruption trade reversal; incumbents re-rated as complements, not victims). "
        "M&amp;A-driven pops (MarineMax, Varex). Losers: AI infrastructure unwind — crowded AI semi/photonics positions reversed as "
        "institutional capital rotated. GLW and KLAC fell on the same thesis: AI capex expectations were over-extrapolated.",
        note_style,
    ))
    story.append(Spacer(1, 6))

    # ── Next-Day Scenarios ─────────────────────────────────────────────────
    story.append(Paragraph("Next-Day Scenarios — August 18, 2026", h2_style))

    scenarios = [
        (
            "1. Home Depot (HD) Q2 Earnings — Before Market Open",
            [
                ("BEAT (EPS > $4.75, Rev > $47.1B, raised guidance)",
                 "HD +4–7%; builder/home-improvement sector lifts. SPY likely +0.3–0.6% as consumer confidence "
                 "narrative flips — even weak housing hasn't killed pro-contractor demand. QQQ modest benefit. "
                 "Lowe's pre-earnings move also typically +2–3% in sympathy."),
                ("MISS or soft guidance (EPS < $4.65, weak comp-store sales)",
                 "HD −5–8%; drags consumer discretionary broadly. SPY −0.4–0.7% on recession demand fears "
                 "intensifying after already-weak retail sales data. Lowe's and Target/Walmart futures pressure "
                 "too. Could also push risk-off buying of Treasuries, briefly capping yield rise."),
                ("In-line, muted guidance",
                 "HD ±1–2%; sector-neutral. SPY trades on other catalysts (oil, yields)."),
            ],
        ),
        (
            "2. Housing Starts + Building Permits (July) — 8:30 AM ET",
            [
                ("Strong (starts > 1.38M, permits > 1.45M)",
                 "Modest positive for homebuilders (LEN, DHI +1–3%). Signals resilient construction despite "
                 "high mortgage rates. SPY +0.1–0.3%. Could be partially offset if interpreted as inflationary "
                 "(more rate pressure)."),
                ("Weak (starts < 1.25M, permits declining)",
                 "Homebuilders sell off −2–4%. SPY −0.2–0.4%. Amplifies 'housing market in recession' narrative. "
                 "Could ironically relieve rate pressure briefly, giving Nasdaq a relative lift."),
            ],
        ),
        (
            "3. Industrial Production (July) — 9:15 AM ET",
            [
                ("Beats (IP > +0.3% MoM)",
                 "Moderate positive for industrials (CAT, GE, MMM +0.5–1%). Signals manufacturing resilience. "
                 "SPY +0.1–0.2%. Cuts recession probability priced in after weak retail sales."),
                ("Misses (IP < −0.1% MoM)",
                 "Adds to stagflation narrative (weak demand + high oil/yields). SPY −0.2–0.5%. Industrials "
                 "and materials underperform."),
            ],
        ),
        (
            "4. Geopolitics — US-Iran Ceasefire Status",
            [
                ("Ceasefire extended or diplomatic progress",
                 "Oil falls sharply (−3–5% Brent). 30-year yield relief. SPY +0.5–0.8%, QQQ +0.6–1%. "
                 "Defense stocks (LMT, RTX) give back some gains. Broad market re-rating positive."),
                ("Ceasefire collapses / escalation",
                 "Oil spikes (potentially +5–8%). 30-year yield surges further. SPY −1–1.5%. "
                 "Energy sector outperforms; rest of market broadly lower. Fed credibility risks if oil "
                 "embeds inflation expectations again."),
            ],
        ),
    ]
    for title, branches in scenarios:
        story.append(Paragraph(title, h3_style))
        for branch_title, body in branches:
            story.append(Paragraph(f"<b>→ {branch_title}:</b>", body_style))
            story.append(Paragraph(body, bullet_style))
        story.append(Spacer(1, 4))

    # ── Possible Purchase Summary ──────────────────────────────────────────
    story.append(Paragraph("Possible Trade Summary — End of Day / Next-Day Open", h2_style))

    trade_data = [
        ["Action", "Ticker", "Rationale", "Conviction"],
        ["WATCH/BUY", "TMUS", "Telecom catalyst momentum (+5.67% today); spectrum deal potential; defensive growth in risk-off tape.", "Medium"],
        ["BUY-IF-BEAT", "HD", "If Q2 beats consensus ($4.73 EPS / $47B rev), stock reclaims $345+ on recovering spring demand narrative. Risk-reward asymmetric pre-open.", "High-conditional"],
        ["AVOID/SELL", "COHR/LITE", "Photonics sector structurally pressured by OpenAI customer risk cascading through AI infra ecosystem (DDOG's disclosure). Weekly and monthly losers.", "Medium-High"],
        ["HOLD/AVOID SELL", "SPY", "Neutral: 30-yr yield pressure and Iran risk are headwinds, but 3 consecutive weekly gains and strong 1Y return (+24.6%) argue against panic selling. Wait for Home Depot read-through.", "Medium"],
        ["CAUTIOUS BUY", "LMT/RTX", "Iran tensions provide durable geopolitical premium. If ceasefire expires without deal, both see further institutional defense rotations.", "Medium"],
        ["AVOID", "MCD/UNH", "Consumer sentiment falling + weak retail sales = near-term pressure on MCD. UNH faces rate headwinds on investment portfolio. Neither catalysts near.", "Medium"],
        ["WATCH", "XOM/CVX", "Oil at $89 Brent is energy-sector tailwind. If Iran tensions persist, energy outperforms further. Consider adding on dips toward energy sector ETF (XLE).", "Low-Medium"],
    ]
    t_tbl = Table(trade_data, colWidths=[1.1*inch, 0.85*inch, 3.6*inch, 1.35*inch])
    t_ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c6e")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
        ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f9ff"), colors.white]),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
    ])
    for i, row in enumerate(trade_data[1:], 1):
        action = row[0]
        if "BUY" in action and "AVOID" not in action:
            t_ts.add("TEXTCOLOR", (0, i), (0, i), colors.HexColor("#007a33"))
            t_ts.add("FONTNAME",  (0, i), (0, i), "Helvetica-Bold")
        elif "SELL" in action or "AVOID" in action:
            t_ts.add("TEXTCOLOR", (0, i), (0, i), colors.HexColor("#c0392b"))
            t_ts.add("FONTNAME",  (0, i), (0, i), "Helvetica-Bold")
    t_tbl.setStyle(t_ts)
    story.append(t_tbl)
    story.append(Paragraph(
        "DISCLAIMER: This is a research and analysis summary only. Not financial advice. No trades are placed or recommended as instructions. "
        "Prices are estimated from index levels; verify before acting.",
        note_style,
    ))
    story.append(Spacer(1, 8))

    # ── Footer ─────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#aaaaaa"), spaceBefore=6))
    story.append(Paragraph(
        f"Report generated: {REPORT_DATE} | Data: prices.csv (Jul 2025–Aug 2026) | "
        "Sources: Yahoo Finance search, TheStreet, TipRanks, CNBC, Bloomberg, Benzinga, FXEmpire.",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7.5,
                       textColor=colors.HexColor("#888888"), alignment=TA_CENTER),
    ))

    doc.build(story)
    print(f"PDF generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
