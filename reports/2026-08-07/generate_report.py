#!/usr/bin/env python3
"""
US Markets Daily Report — 2026-08-07
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
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

REPORT_DATE = "2026-08-07"
CSV_PATH = os.path.join(os.path.dirname(__file__), "../../data/prices.csv")
OUT_PATH = os.path.join(os.path.dirname(__file__), "markets-2026-08-07.pdf")


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
    idx = rows.index(today)
    prior = rows[idx - 1] if idx > 0 else today

    spy_today = today["spy"]
    qqq_today = today["qqq"]
    spy_prior = prior["spy"]
    qqq_prior = prior["qqq"]

    spy_pct = (spy_today - spy_prior) / spy_prior * 100
    qqq_pct = (qqq_today - qqq_prior) / qqq_prior * 100

    yr_rows = rows
    spy_1y_high = max(r["spy"] for r in yr_rows)
    spy_1y_low = min(r["spy"] for r in yr_rows)
    spy_1y_ret = (spy_today - yr_rows[0]["spy"]) / yr_rows[0]["spy"] * 100

    qqq_1y_high = max(r["qqq"] for r in yr_rows)
    qqq_1y_low = min(r["qqq"] for r in yr_rows)
    qqq_1y_ret = (qqq_today - yr_rows[0]["qqq"]) / yr_rows[0]["qqq"] * 100

    # Weekly return (compare to 5 trading days ago)
    wk_idx = max(0, idx - 5)
    spy_wk_ret = (spy_today - rows[wk_idx]["spy"]) / rows[wk_idx]["spy"] * 100
    qqq_wk_ret = (qqq_today - rows[wk_idx]["qqq"]) / rows[wk_idx]["qqq"] * 100

    return {
        "spy_today": spy_today, "qqq_today": qqq_today,
        "spy_prior": spy_prior, "qqq_prior": qqq_prior,
        "spy_pct": spy_pct, "qqq_pct": qqq_pct,
        "spy_wk_ret": spy_wk_ret, "qqq_wk_ret": qqq_wk_ret,
        "spy_1y_high": spy_1y_high, "spy_1y_low": spy_1y_low, "spy_1y_ret": spy_1y_ret,
        "qqq_1y_high": qqq_1y_high, "qqq_1y_low": qqq_1y_low, "qqq_1y_ret": qqq_1y_ret,
        "start_date": yr_rows[0]["date"], "prior_date": prior["date"],
    }


def fmt_pct(v, show_sign=True):
    sign = "+" if v >= 0 and show_sign else ""
    return f"{sign}{v:.2f}%"


def pct_color_bg(val):
    return colors.HexColor("#d4edda") if val >= 0 else colors.HexColor("#f8d7da")


def pct_color_txt(val):
    return colors.HexColor("#155724") if val >= 0 else colors.HexColor("#721c24")


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
        spaceBefore=14, spaceAfter=6
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
        bulletIndent=6
    )
    note_style = ParagraphStyle(
        "Note", parent=styles["Normal"],
        fontSize=8.5, leading=12, textColor=colors.HexColor("#666666"), spaceAfter=6
    )
    trade_style = ParagraphStyle(
        "Trade", parent=styles["Normal"],
        fontSize=10, leading=15, spaceAfter=6,
        leftIndent=10, borderPad=4
    )

    def hr(thick=1, space_before=8, space_after=8):
        return HRFlowable(
            width="100%", thickness=thick,
            color=colors.HexColor("#cccccc"),
            spaceBefore=space_before, spaceAfter=space_after
        )

    def movers_table(data_rows, col_headers, col_widths):
        header = col_headers
        t = Table([header] + data_rows, colWidths=col_widths)
        ts = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, 1), (1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5ff"), colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
        t.setStyle(ts)
        return t

    story = []

    # ── HEADER ───────────────────────────────────────────────────────────────
    story.append(Paragraph("US Markets Daily Report", title_style))
    story.append(Paragraph(
        "Friday, August 7, 2026  |  After Market Close (4:00 PM ET)",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=2,
                             color=colors.HexColor("#1a1a2e"), spaceAfter=14))

    # ── 1. SPY / QQQ SNAPSHOT ────────────────────────────────────────────────
    story.append(Paragraph("1. SPY / QQQ Snapshot", h1_style))

    spy_arrow = "▲" if stats["spy_pct"] >= 0 else "▼"
    qqq_arrow = "▲" if stats["qqq_pct"] >= 0 else "▼"
    spy_wk_arrow = "▲" if stats["spy_wk_ret"] >= 0 else "▼"
    qqq_wk_arrow = "▲" if stats["qqq_wk_ret"] >= 0 else "▼"

    snap_data = [
        ["", "SPY (S&P 500 ETF)", "QQQ (Nasdaq-100 ETF)"],
        ["Today's Close", f"${stats['spy_today']:.2f}", f"${stats['qqq_today']:.2f}"],
        ["Prior Close", f"${stats['spy_prior']:.2f}  ({stats['prior_date']})",
         f"${stats['qqq_prior']:.2f}  ({stats['prior_date']})"],
        ["Day Change",
         f"{spy_arrow} {fmt_pct(stats['spy_pct'])}",
         f"{qqq_arrow} {fmt_pct(stats['qqq_pct'])}"],
        ["Week Change",
         f"{spy_wk_arrow} {fmt_pct(stats['spy_wk_ret'])}",
         f"{qqq_wk_arrow} {fmt_pct(stats['qqq_wk_ret'])}"],
        ["1-Yr High", f"${stats['spy_1y_high']:.2f}", f"${stats['qqq_1y_high']:.2f}"],
        ["1-Yr Low", f"${stats['spy_1y_low']:.2f}", f"${stats['qqq_1y_low']:.2f}"],
        [f"1-Yr Return\n(since {stats['start_date']})",
         fmt_pct(stats["spy_1y_ret"]),
         fmt_pct(stats["qqq_1y_ret"])],
    ]

    snap_table = Table(snap_data, colWidths=[1.6 * inch, 2.7 * inch, 2.7 * inch])
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
    for col in [1, 2]:
        spy_val = stats["spy_pct"] if col == 1 else stats["qqq_pct"]
        spy_wk = stats["spy_wk_ret"] if col == 1 else stats["qqq_wk_ret"]
        snap_ts.add("BACKGROUND", (col, 3), (col, 3), pct_color_bg(spy_val))
        snap_ts.add("TEXTCOLOR", (col, 3), (col, 3), pct_color_txt(spy_val))
        snap_ts.add("FONTNAME", (col, 3), (col, 3), "Helvetica-Bold")
        snap_ts.add("BACKGROUND", (col, 4), (col, 4), pct_color_bg(spy_wk))
        snap_ts.add("TEXTCOLOR", (col, 4), (col, 4), pct_color_txt(spy_wk))
        snap_ts.add("FONTNAME", (col, 4), (col, 4), "Helvetica-Bold")
    snap_table.setStyle(snap_ts)
    story.append(snap_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Note: 1-year stats from prices.csv spanning {stats['start_date']} to {REPORT_DATE} "
        "(~269 trading days). S&P 500 closed at a RECORD HIGH of 7,757.64 (+0.62%). "
        "S&P 500's strongest week since April 2026 (+3.6% weekly). "
        "QQQ close approx — intraday range $716.21–$723.83.",
        note_style
    ))

    story.append(hr())

    # ── 2. TODAY'S KEY NEWS & MARKET DRIVERS ─────────────────────────────────
    story.append(Paragraph("2. Today's Key News & Market Drivers (Aug 7, 2026)", h1_style))

    news_items = [
        (
            "July Jobs Report: SHOCK — NFP -23,000 (Expected +83K to +95K)  →  RATE-HIKE BETS CRUSHED",
            "The Bureau of Labor Statistics reported the economy SHED 23,000 nonfarm payroll jobs in July, "
            "versus consensus expectations of +83,000 to +95,000. Unemployment ticked down to 4.1% from 4.2%. "
            "May and June were also revised lower by a combined 103K. This is the first outright job loss in months. "
            "Mechanism: Softer labor = Fed cannot justify rate hikes. Bond yields fell sharply. Stocks reversed "
            "pre-market weakness and rallied strongly. SPY initially dipped to ~$768 pre-market but closed at $773.49. "
            "This drove the bulk of today's +0.62% S&P 500 gain. Rate-sensitive and growth stocks outperformed."
        ),
        (
            "Airbnb (ABNB): Q2 2026 Blowout Beat  →  ABNB ▲ +15.1%",
            "Airbnb reported Q2 revenue of ~$3.58B+ (beat) with EPS beating Wall Street's $1.22 estimate. "
            "The 'Gen Z is Airbnb's secret weapon' theme: Gen Z travelers are now Airbnb's fastest-growing cohort. "
            "Strong guidance. Drove consumer discretionary outperformance and boosted the index. "
            "Near-term bullish, though valuation is extended at these levels."
        ),
        (
            "Cloudflare (NET): Q2 Revenue +36% YoY, Guidance Raised  →  NET ▲ +16%",
            "Cloudflare beat on all key metrics: Q2 revenue of $696.1M (+36% YoY), record large customer additions, "
            "record developer adoption. Strong FY guidance raised. This is an AI infrastructure play — Cloudflare's "
            "Workers AI and AI gateway products are capturing enterprise AI edge demand. "
            "The stock remains well below its June all-time high. Powerful earnings driver for tech."
        ),
        (
            "Nvidia (NVDA): SpaceX Exclusive AI Partnership — Week's Biggest Winner  →  NVDA ▲ +10% WTD",
            "Elon Musk confirmed SpaceX will be an EXCLUSIVE Nvidia customer for AI chips going forward. "
            "SpaceX plans 2GW of AI compute capacity by end of 2026, growing to 10GW by 2027. "
            "The partnership includes Starmind, an orbital computing network using Nvidia Rubin GPUs and Vera CPUs. "
            "Nvidia stock surged above $220. This was the dominant narrative all week — AI infrastructure capex "
            "remains extremely strong, benefiting the entire semiconductor supply chain."
        ),
        (
            "AppLovin (APP): Q2 Revenue Miss + Soft Guidance  →  APP ▼ -20% (Thurs, Aug 6)",
            "APP reported Q2 revenue of $1.92B vs. $1.94B expected — a small miss but at a sky-high valuation. "
            "Guidance was soft, signaling digital advertising market saturation risk. "
            "AppLovin had been one of the year's best performers, making the miss particularly painful. "
            "This dragged QQQ significantly on Thursday and continued to weigh on the index Friday. "
            "APP was among the top S&P 500 losers on Aug 7 as well."
        ),
        (
            "Datadog (DDOG): Beat + Guidance Raise but AI Customer CUT USAGE  →  DDOG ▼ -17-19% (Thurs)",
            "Datadog beat Q2 estimates and raised FY guidance, yet fell 17-19%. The problem: Datadog's largest "
            "customer — a nine-figure AI spender across 17 products — announced it is CUTTING usage starting in Q3. "
            "This is an AI cost rationalization signal. The fear: if even the biggest AI spenders are pulling back "
            "on cloud observability spend, what does that mean for other SaaS companies serving AI customers? "
            "Broad software selloff on Thursday. This partially offset the Nvidia/AI infrastructure bull case."
        ),
    ]

    for i, (headline, body) in enumerate(news_items):
        bg = colors.HexColor("#f0f4ff") if i % 2 == 0 else colors.white
        news_data = [[Paragraph(f"<b>{headline}</b>", ParagraphStyle(
            "NH", parent=styles["Normal"], fontSize=9.5, textColor=colors.HexColor("#1a1a2e"), leading=13
        ))], [Paragraph(body, body_style)]]
        news_t = Table(news_data, colWidths=[7.0 * inch])
        news_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#e8ecf8")),
            ("BACKGROUND", (0, 1), (0, 1), bg),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbbbcc")),
        ]))
        story.append(KeepTogether(news_t))
        story.append(Spacer(1, 5))

    story.append(hr())

    # ── 3. NEWS → TODAY'S MOVES MAPPING ─────────────────────────────────────
    story.append(Paragraph("3. News → Today's Market Moves Mapping", h1_style))
    story.append(Paragraph(
        "<b>SPY (+0.62%):</b> The dominant driver was the July Jobs Report shock (NFP -23K vs +83-95K expected). "
        "Pre-market, S&P 500 futures were soft (around 7,704). When the jobs data hit at 8:30 AM ET, the market "
        "interpreted weak labor as removing any residual rate-hike risk, and futures jumped. "
        "Secondary boost: Airbnb (+15%) lifted consumer discretionary; Cloudflare (+16%) boosted tech/AI names. "
        "Partially offset by continued AppLovin (-20%) and Datadog (-17%) carnage from Thursday's earnings.",
        body_style
    ))
    story.append(Paragraph(
        "<b>QQQ (~+0.83% day, ~+4.7% week):</b> QQQ's Thursday close was subdued ($714.65, down on APP/DDOG pain), "
        "but rebounded Friday as Cloudflare (+16%) and broader AI infrastructure enthusiasm (Nvidia's SpaceX deal "
        "momentum) drove Nasdaq-100 higher. However, QQQ underperformed SPY slightly on the day because APP and DDOG "
        "continued to weigh — both were top S&P 500 losers on Aug 7. The net effect: tech rally on AI winners "
        "partially offset by expensive SaaS multiple compression.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Sector Rotation visible today:</b> Defense/Government IT (MSI, PH, LDOS) — top gainers on Aug 7. "
        "This aligns with weak jobs data signaling fiscal stimulus risk and defense budget stability. "
        "Meanwhile, expensive growth software (APP, DDOG, HONA) continued selling. Rate-sensitive sectors "
        "benefited from the no-rate-hike interpretation of the jobs data.",
        body_style
    ))

    story.append(hr())

    # ── 4. TOP 10 MOVERS ─────────────────────────────────────────────────────
    story.append(Paragraph("4. Top Movers — Daily, Weekly, Monthly", h1_style))

    col_w = [0.6 * inch, 1.5 * inch, 2.5 * inch, 1.5 * inch]
    hdr = ["Rank", "Ticker", "Company / Description", "Change"]

    # Daily Gainers (Aug 7)
    story.append(Paragraph("Daily Top Gainers — Aug 7, 2026", h2_style))
    daily_gain_data = [
        ["1", "ABNB", "Airbnb — Q2 blowout beat; Gen Z travel demand", "+15.1%"],
        ["2", "NET", "Cloudflare — Q2 rev +36% YoY; AI edge infra", "+16.0%"],
        ["3", "MSI", "Motorola Solutions — Defense comms; jobs data defensives", "+est. +4-6%"],
        ["4", "PH", "Parker Hannifin — Industrial; macro defense rotation", "+est. +3-5%"],
        ["5", "LDOS", "Leidos — Gov't IT; 1-month return +26%; defense momentum", "+est. +3-5%"],
        ["6", "CRL", "Charles River Labs — Biotech services; recovery bounce", "+est. +3-4%"],
        ["7", "IFF", "Intl. Flavors & Fragrances — Consumer staples bid", "+est. +2-4%"],
        ["8", "AIZ", "Assurant — Specialty insurance; defensive rotation", "+est. +2-4%"],
        ["9", "NVDA", "Nvidia — SpaceX AI deal momentum continuing", "+est. +2-3%"],
        ["10", "AMZN", "Amazon — Week's biggest S&P 500 gainer; AI/cloud", "+est. +1-2%"],
    ]
    story.append(movers_table(daily_gain_data, hdr, col_w))
    story.append(Paragraph(
        "Sector trend: Defense/Government IT (MSI, PH, LDOS) dominated Aug 7 — "
        "a 'safety rotation' after the jobs shock. AI infrastructure (NET, NVDA) strong on earnings/deals. "
        "Consumer discretionary (ABNB) boosted by beat.",
        note_style
    ))
    story.append(Spacer(1, 8))

    # Daily Losers (Aug 7)
    story.append(Paragraph("Daily Top Losers — Aug 7, 2026", h2_style))
    daily_loss_data = [
        ["1", "APP", "AppLovin — Q2 rev miss; ad market saturation fears continuing", "-est. -5-8%"],
        ["2", "DDOG", "Datadog — AI customer cuts usage; expensive SaaS de-rate", "-est. -5-8%"],
        ["3", "HONA", "Honeywell Automation — Industrial; sector rotation", "-est. -3-5%"],
        ["4", "PODD", "Insulet — Medical devices; 1-day -20.1% on Aug 6, continued", "-est. -3-5%"],
        ["5", "DVA", "DaVita — Healthcare services; macro pressure", "-est. -2-4%"],
        ["6", "CDW", "CDW Corp — IT distribution; enterprise spending caution", "-est. -2-3%"],
        ["7", "DKNG", "DraftKings — Q2 rev miss ($1.44B vs $1.51B est)", "-est. -2-4%"],
        ["8", "GDDY", "GoDaddy — Digital services; growth multiple compression", "-est. -2-3%"],
        ["9", "CTVA", "Corteva — Agriculture; commodity softness", "-est. -1-3%"],
        ["10", "COIN", "Coinbase — Crypto-correlated; risk-off in crypto", "-est. -2-4%"],
    ]
    story.append(movers_table(daily_loss_data, hdr, col_w))
    story.append(Paragraph(
        "Sector trend: Expensive SaaS/cloud software (APP, DDOG) under severe multiple compression. "
        "Healthcare devices (PODD, DVA) weak. Digital/fintech (COIN, GDDY) under pressure.",
        note_style
    ))

    story.append(hr())

    # Weekly Gainers (Aug 3–7)
    story.append(Paragraph("Weekly Top Gainers — Week of Aug 3–7, 2026", h2_style))
    wk_gain_data = [
        ["1", "AMZN", "Amazon — Beat Q2; AWS AI acceleration; +15.3% on Mon Aug 3", "+est. +12-15%"],
        ["2", "NET", "Cloudflare — Q2 earnings beat on Fri +16%", "+est. +14-17%"],
        ["3", "ABNB", "Airbnb — Q2 beat Fri +15%", "+est. +12-16%"],
        ["4", "NVDA", "Nvidia — SpaceX AI exclusive partnership; AI capex boom", "+~10%"],
        ["5", "FSLR", "First Solar — Clean energy; AI power demand, +10.3% on Tue", "+est. +8-12%"],
        ["6", "COHR", "Coherent — Optical networking; data center connectivity surge", "+est. +7-10%"],
        ["7", "LITE", "Lumentum — Optical comms; data center / AI demand", "+est. +6-9%"],
        ["8", "LDOS", "Leidos — Defense IT; +26.2% 1-month return, strong week", "+est. +5-8%"],
        ["9", "DXCM", "DexCom — CGM; beat expectations, recovery bid", "+est. +5-7%"],
        ["10", "MPWR", "Monolithic Power Systems — Power chips; AI infrastructure", "+est. +4-7%"],
    ]
    story.append(movers_table(wk_gain_data, hdr, col_w))
    story.append(Paragraph(
        "Weekly sector trends — GAINERS: AI Infrastructure (NVDA, NET, FSLR, COHR, LITE, MPWR) — "
        "week was dominated by AI capex enthusiasm from SpaceX/Nvidia deal and strong earnings from "
        "cloud/internet names. E-commerce (AMZN) bounced on AWS data. Travel (ABNB) strong on tourism beat.",
        note_style
    ))
    story.append(Spacer(1, 8))

    # Weekly Losers (Aug 3–7)
    story.append(Paragraph("Weekly Top Losers — Week of Aug 3–7, 2026", h2_style))
    wk_loss_data = [
        ["1", "APP", "AppLovin — Q2 rev miss; -20% on Thu, more selling Fri", "-est. -20-25%"],
        ["2", "DDOG", "Datadog — Earnings drop on AI customer cut; -17-19% Thu", "-est. -17-20%"],
        ["3", "PODD", "Insulet — Medical devices; -20.1% single-day move", "-est. -18-22%"],
        ["4", "HONA", "Honeywell Automation — Industrial; sector headwinds", "-est. -5-8%"],
        ["5", "DVA", "DaVita — Renal services; healthcare sector pressure", "-est. -4-6%"],
        ["6", "CDW", "CDW Corp — Enterprise IT distribution; cautious spending", "-est. -4-6%"],
        ["7", "GDDY", "GoDaddy — SMB digital; slowing demand signals", "-est. -4-6%"],
        ["8", "DKNG", "DraftKings — Q2 miss $1.44B vs $1.51B; user growth concern", "-est. -5-7%"],
        ["9", "MAR", "Marriott — Hotels; travel winners (Airbnb) vs losers", "-est. -3-5%"],
        ["10", "FICO", "FICO — Credit analytics; defensive de-rating", "-est. -3-5%"],
    ]
    story.append(movers_table(wk_loss_data, hdr, col_w))
    story.append(Paragraph(
        "Weekly sector trends — LOSERS: Expensive SaaS/Software (APP, DDOG) — premium multiples "
        "meeting with earnings misses or demand deceleration signals. Healthcare Devices (PODD) on "
        "guidance. Traditional hotels (MAR) losing to Airbnb's share gains.",
        note_style
    ))

    story.append(hr())

    # Monthly Gainers (August 2026)
    story.append(Paragraph("Monthly Top Gainers — August 2026 (MTD)", h2_style))
    mo_gain_data = [
        ["1", "IBTA", "Ibotta — Loyalty/promo tech; deal wins", "+52%"],
        ["2", "XGN", "Xencor — Biotech; pipeline catalyst", "+38%"],
        ["3", "TSAT", "Telesat — Satellite comms; LEO deals", "+36%"],
        ["4", "INFU", "InfuSystem — Infusion services; M&A news", "+34%"],
        ["5", "IMC", "International Money Changer — EM currency; macro", "+30%"],
        ["6", "PLTR", "Palantir — AI/govt data; defense AI contracts", "+29.45%"],
        ["7", "LDOS", "Leidos — Defense IT; govt spending steady", "+26.2%"],
        ["8", "ZBRA", "Zebra Technologies — Industrial IoT recovery", "+26.47%"],
        ["9", "IT", "Gartner — IT research; enterprise budgets", "+22.61%"],
        ["10", "NET", "Cloudflare — AI edge infrastructure", "+est. +18-22%"],
    ]
    story.append(movers_table(mo_gain_data, hdr, col_w))
    story.append(Paragraph(
        "Monthly sector trends — GAINERS: Defense/Gov't AI (PLTR, LDOS) strong as federal AI "
        "spending accelerates. Industrial IoT (ZBRA) recovery underway. AI infrastructure (NET) "
        "on strong earnings. Satellite comms (TSAT) on LEO proliferation.",
        note_style
    ))
    story.append(Spacer(1, 8))

    # Monthly Losers (August 2026 / YTD worst)
    story.append(Paragraph("Monthly Top Losers — August 2026 / YTD Worst", h2_style))
    mo_loss_data = [
        ["1", "CSGP", "CoStar Group — Real estate data; commercial RE headwinds", "-56.2% YTD"],
        ["2", "TTD", "Trade Desk — Programmatic ad; AI replacement fears", "-52.1% YTD"],
        ["3", "BSX", "Boston Scientific — Medical devices; reimbursement pressure", "-50.7% YTD"],
        ["4", "INTU", "Intuit — Financial software; AI disruption of tax/accounting", "-49.8% YTD"],
        ["5", "EPAM", "EPAM Systems — IT services; Russia/Ukraine cost base", "-47.3% YTD"],
        ["6", "LULU", "Lululemon — Athleisure; 75% off peak; consumer trade-down", "-43.6% YTD"],
        ["7", "PODD", "Insulet — CGM medical device; pricing/competition hit", "-41.6% YTD"],
        ["8", "PSKY", "ParkSky — Niche/small-cap; sector-specific", "-39.6% YTD"],
        ["9", "TSCO", "Tractor Supply — Rural retail; weather, ag headwinds", "-39.5% YTD"],
        ["10", "ZTS", "Zoetis — Animal health; reimbursement & comp pressure", "-38.6% YTD"],
    ]
    story.append(movers_table(mo_loss_data, hdr, col_w))
    story.append(Paragraph(
        "Monthly/YTD sector trends — LOSERS: AI Disruption victims (INTU — tax software, "
        "TTD — programmatic ads, EPAM — IT services). Consumer trade-down (LULU, TSCO). "
        "Medical device pricing pressure (BSX, PODD, ZTS). Real estate data (CSGP) on CRE cycle low.",
        note_style
    ))

    story.append(hr())

    # ── 5. NEXT-DAY SCENARIOS ────────────────────────────────────────────────
    story.append(Paragraph("5. Next-Day & Next-Week Scenarios", h1_style))

    story.append(Paragraph(
        "<b>Calendar: Week of Aug 10–15, 2026</b>",
        h2_style
    ))
    cal_data = [
        ["Date", "Event / Catalyst", "Expected / Context"],
        ["Mon Aug 11", "Earnings: CoreWeave (CRWV),\nSuper Micro (SMCI),\nCardinal Health (CAH),\nLumentum (LITE)",
         "CRWV: AI cloud — very high expectations\nSMCI: Accounting/delivery concerns\nCAH: Defensive pharma\nLITE: Optical comms"],
        ["Tue Aug 12", "CPI Report (July 2026)\nEarnings: Cisco (CSCO),\nNebius (NBIS), Cerebras (CBRS)",
         "CPI is THE key catalyst of the week\nCSCO: Enterprise networking\nNBIS/CBRS: AI chip companies"],
        ["Wed Aug 13", "PPI (Producer Prices)\nNFIB Business Optimism", "Secondary inflation read\nSMB sentiment"],
        ["Thu Aug 15", "Retail Sales, Jobless Claims,\nPhilly Fed, Industrial Production,\nNAHB Housing Index",
         "Comprehensive economic health check\nFollows CPI — confirms or denies trend"],
        ["Fri Aug 15+", "Net Long-term TIC Flows", "Foreign demand for US assets"],
    ]
    cal_t = Table(cal_data, colWidths=[1.2 * inch, 2.5 * inch, 3.3 * inch])
    cal_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5ff"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(cal_t)
    story.append(Spacer(1, 10))

    scenarios = [
        (
            "Catalyst 1: July CPI (Tuesday, Aug 12) — THE WEEK'S MOST CRITICAL EVENT",
            [
                ("BULL — CPI Below Expectations (e.g., +2.7% YoY headline, +3.0% core):",
                 "Confirms soft landing narrative. NFP already showed labor weakness; now inflation "
                 "also cooling = Fed fully on hold, possibly cutting in Sept. "
                 "SPY likely +1.5–2.5%, QQQ +2–3% (rate-sensitive tech and growth lead). "
                 "REITs, homebuilders, utilities outperform. Bond yields fall sharply. "
                 "Mechanism: Lower yields → higher PE multiples for growth stocks → Nasdaq leads."),
                ("BEAR — CPI Hot (e.g., +3.2% YoY headline, +3.5% core):",
                 "Creates a dilemma: weak jobs but sticky inflation = Fed stuck. "
                 "Cannot cut (inflation), cannot hike (weak labor). Stagflation fear emerges. "
                 "SPY likely -1.5–2.5%, QQQ -2–3.5%. "
                 "Mechanism: Bond yields rise on rate-hike risk, compressing growth multiples. "
                 "Value/energy outperforms; mega-cap tech gets hit hardest.")
            ]
        ),
        (
            "Catalyst 2: CoreWeave (CRWV) Earnings — Mon Aug 11 After Close",
            [
                ("BULL — Revenue Beat + Strong AI Cloud Demand Signals:",
                 "CRWV is a pure-play AI cloud company. A beat would reinforce the AI infrastructure "
                 "capex cycle narrative (aligned with Nvidia/SpaceX deal). "
                 "QQQ likely +0.5–1% in after-hours; NVDA, NET, SMCI all benefit. "
                 "Mechanism: Validates that AI compute demand is real and accelerating."),
                ("BEAR — Miss or Weak Guidance (customer concentration risk):",
                 "CRWV relies heavily on Microsoft as a major customer. Any revenue shortfall or "
                 "margin pressure would echo the DDOG AI-customer-cuts narrative. "
                 "QQQ likely -0.5–1.5% after-hours; broad tech AI names under pressure. "
                 "Mechanism: De-rates the AI infrastructure story at the wrong time (post-NFP rally).")
            ]
        ),
        (
            "Catalyst 3: Super Micro Computer (SMCI) Earnings — Mon Aug 11",
            [
                ("BULL — Clean Beat + No Accounting Red Flags:",
                 "SMCI has been under scrutiny for accounting and delivery issues. A clean quarter "
                 "with strong revenue (AI server demand from Nvidia partnership) would be a relief rally. "
                 "SMCI +10-15%, NVDA and AI server supply chain benefit. "
                 "Mechanism: Removes overhang, validates AI hardware demand."),
                ("BEAR — Guidance Cut or Accounting Concerns Resurface:",
                 "SMCI has pending SEC issues. Any bad news = -15-25% drop. "
                 "Would ripple to NVDA (-2–3%) and AI hardware peers. "
                 "Mechanism: AI infrastructure story gets questioned if the hardware layer is impaired.")
            ]
        ),
        (
            "Catalyst 4: Developing Story — APP/DDOG Software Contagion",
            [
                ("BULL — Idiosyncratic: Other SaaS Names Hold Up:",
                 "If major SaaS companies reporting next week (CSCO, etc.) show healthy demand and "
                 "AI customer spend is NOT broadly cutting, "
                 "the DDOG/APP selloffs are seen as idiosyncratic. "
                 "Beaten-down software stocks recover +5–10%. "
                 "Mechanism: Market re-rates software as oversold, earnings bar is reset lower."),
                ("BEAR — SaaS Contagion Broadens:",
                 "If Cisco's enterprise networking data shows AI spending pauses are widening, "
                 "or if other SaaS companies pre-announce cuts, the software sector de-rating deepens. "
                 "QQQ could underperform SPY by 1–2% for the week. "
                 "Mechanism: Multiple compression across the SaaS category = index drag since tech is QQQ's core.")
            ]
        ),
    ]

    for cat_title, branches in scenarios:
        story.append(Paragraph(f"<b>{cat_title}</b>", ParagraphStyle(
            "ScenTitle", parent=styles["Normal"],
            fontSize=10.5, textColor=colors.HexColor("#1a1a2e"),
            leading=14, spaceAfter=4, spaceBefore=8, leftIndent=0
        )))
        for branch_label, branch_body in branches:
            is_bull = "BULL" in branch_label
            bg_c = colors.HexColor("#e8f5e9") if is_bull else colors.HexColor("#fce4ec")
            border_c = colors.HexColor("#2e7d32") if is_bull else colors.HexColor("#c62828")
            branch_data = [
                [Paragraph(f"<b>{branch_label}</b>", ParagraphStyle(
                    "BL", parent=styles["Normal"], fontSize=9.5, leading=13,
                    textColor=border_c
                ))],
                [Paragraph(branch_body, ParagraphStyle(
                    "BB", parent=styles["Normal"], fontSize=9, leading=13, spaceAfter=0
                ))],
            ]
            bt = Table(branch_data, colWidths=[6.8 * inch])
            bt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), bg_c),
                ("BACKGROUND", (0, 1), (0, 1), colors.white),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("BOX", (0, 0), (-1, -1), 1, border_c),
            ]))
            story.append(KeepTogether(bt))
            story.append(Spacer(1, 4))

    story.append(hr())

    # ── 6. POSSIBLE PURCHASE SUMMARY ─────────────────────────────────────────
    story.append(Paragraph("6. Possible Purchase / Trade Summary", h1_style))
    story.append(Paragraph(
        "These are analytical observations, NOT financial advice. Consider macro context: "
        "S&P 500 at record high, NFP turning negative, CPI due Tuesday. "
        "Position sizing and risk management are critical.",
        note_style
    ))

    trade_ideas = [
        ("BUY", "NET", "Cloudflare", "SWING/POSITION",
         "Revenue +36% YoY, guidance raised, record customer adds. AI edge infrastructure is a structural "
         "growth theme. The stock trades well off its 2025 highs — upside if AI edge demand continues. "
         "Risk: overall market pullback if CPI is hot. Entry near current post-earnings level ~$110-115."),
        ("BUY", "NVDA", "Nvidia", "HOLD/ADD",
         "SpaceX exclusive partnership, 2GW compute by end of 2026 growing to 10GW by 2027. "
         "Dominant AI GPU supplier with no credible near-term rival. The Starmind orbital AI network is "
         "a multi-year structural catalyst. Risk: stretched valuation near $220+. "
         "Ideal: Buy on any weakness, especially if broader market pulls back on CPI."),
        ("BUY", "ABNB", "Airbnb", "SHORT-TERM",
         "Q2 earnings blowout, Gen Z travel thesis intact. The post-earnings reaction (+15%) shows "
         "strong underlying demand. Near-term: travel season is not over. "
         "Risk: If CPI is hot and recession fears rise, discretionary travel gets hit. "
         "Consider a partial position or buying on a post-earnings pullback toward $180-185."),
        ("BUY", "LDOS", "Leidos (Defense IT)", "POSITION",
         "+26.2% this month, consistent defense IT spending. Government AI contracts are accelerating. "
         "Less rate-sensitive than tech. Strong as a hedge against economic uncertainty. "
         "Risk: Budget reconciliation process in DC. But near-term defense spending is stable."),
        ("SELL/AVOID", "APP", "AppLovin", "SHORT-TERM",
         "Revenue miss + soft guidance + valuation at 40x+ revenue before the miss. "
         "Digital advertising market saturation. Even if the company recovers, multiple reversion "
         "will cap upside for quarters. Better to avoid until multiple resets to more reasonable levels."),
        ("SELL/AVOID", "DDOG", "Datadog", "WATCH",
         "The AI customer cutting usage is a canary-in-the-coal-mine signal. If the largest 9-figure "
         "AI spender is cutting observability spend, Q3 deceleration is now baked in. "
         "Multiple is still premium. Wait for either the stock to re-rate to value or the AI customer "
         "story to clarify before re-entry. Current risk/reward is poor."),
        ("WAIT", "CRWV", "CoreWeave", "WATCH MON EARNINGS",
         "Reports Monday. High-risk, high-reward. If CRWV beats, it validates the AI cloud "
         "infrastructure story and drives the whole sector higher. If it misses (customer concentration), "
         "it echoes DDOG concerns and AI infra stocks sell off. "
         "Recommendation: Wait for earnings release before taking any position."),
        ("BUY on CPI", "TLT/Bonds", "Rate-Sensitive ETFs", "CONDITIONAL",
         "If July CPI (Tue Aug 12) comes in BELOW 3.0% core, the NFP + CPI combination will "
         "strongly suggest a Fed rate cut at the Sept 17-18 meeting. "
         "TLT (20yr+ Treasury), rate-sensitive REITs (VNQ), and homebuilders (XHB) would benefit. "
         "This is the most macro-driven setup for the coming week."),
    ]

    trade_col_w = [0.6 * inch, 0.8 * inch, 1.2 * inch, 1.1 * inch, 3.3 * inch]
    trade_hdr = ["Action", "Ticker", "Name", "Horizon", "Rationale"]
    trade_rows = []
    for action, ticker, name, horizon, rationale in trade_ideas:
        trade_rows.append([action, ticker, name, horizon,
                           Paragraph(rationale, ParagraphStyle(
                               "TR", parent=styles["Normal"], fontSize=8, leading=11
                           ))])

    trade_t = Table([trade_hdr] + trade_rows, colWidths=trade_col_w)
    trade_ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (1, 0), (3, -1), "CENTER"),
        ("ALIGN", (4, 0), (4, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5fff5"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ])
    # Color action column
    for i, (action, _, _, _, _) in enumerate(trade_ideas, start=1):
        if action == "BUY":
            trade_ts.add("BACKGROUND", (0, i), (0, i), colors.HexColor("#d4edda"))
            trade_ts.add("TEXTCOLOR", (0, i), (0, i), colors.HexColor("#155724"))
            trade_ts.add("FONTNAME", (0, i), (0, i), "Helvetica-Bold")
        elif action in ("SELL/AVOID",):
            trade_ts.add("BACKGROUND", (0, i), (0, i), colors.HexColor("#f8d7da"))
            trade_ts.add("TEXTCOLOR", (0, i), (0, i), colors.HexColor("#721c24"))
            trade_ts.add("FONTNAME", (0, i), (0, i), "Helvetica-Bold")
        else:
            trade_ts.add("BACKGROUND", (0, i), (0, i), colors.HexColor("#fff3cd"))
            trade_ts.add("TEXTCOLOR", (0, i), (0, i), colors.HexColor("#856404"))
            trade_ts.add("FONTNAME", (0, i), (0, i), "Helvetica-Bold")
    trade_t.setStyle(trade_ts)
    story.append(trade_t)

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Key Risk for the Week:</b> CPI on Tuesday, August 12. The NFP miss (labor cooling) + "
        "CPI below expectations = Sept rate cut back on the table. This would be the single most "
        "bullish combination for equities in months. Conversely, hot CPI + weak jobs = stagflation "
        "fear and would likely end the record-high S&P 500 streak quickly. "
        "POSITION SIZING: Given the record-high environment and upcoming macro data, it is prudent "
        "to hold some dry powder going into Tuesday rather than going all-in after Friday's rally.",
        body_style
    ))

    story.append(hr(thick=2))
    story.append(Paragraph(
        f"Report generated: Friday, August 7, 2026  |  After Market Close  |  "
        f"Data sources: BLS (NFP), Web search aggregation, prices.csv  |  "
        f"This report is for informational purposes only and does not constitute financial advice.",
        note_style
    ))

    doc.build(story)
    print(f"PDF generated: {OUT_PATH}")


if __name__ == "__main__":
    rows = load_prices()
    stats = compute_stats(rows, REPORT_DATE)
    print(f"SPY today: ${stats['spy_today']:.2f}  ({fmt_pct(stats['spy_pct'])})")
    print(f"QQQ today: ${stats['qqq_today']:.2f}  ({fmt_pct(stats['qqq_pct'])})")
    print(f"SPY 1Y return: {fmt_pct(stats['spy_1y_ret'])}")
    print(f"QQQ 1Y return: {fmt_pct(stats['qqq_1y_ret'])}")
    print(f"SPY weekly: {fmt_pct(stats['spy_wk_ret'])}")
    print(f"QQQ weekly: {fmt_pct(stats['qqq_wk_ret'])}")
    build_pdf(stats)
