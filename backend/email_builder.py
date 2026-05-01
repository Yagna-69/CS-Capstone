"""
Email template builder for FXTrade trade/transfer confirmations.

Design tokens match the app exactly:
  bg-primary   #000000
  bg-secondary #0a0a0a
  bg-card      #121212
  border       #1e1e1e
  primary      #FFD700
  primary-dark #FFA500
  success      #22c55e  (green-500)
  danger       #ff4444
  text-muted   #6b7280  (gray-500)
  text-dim     #374151  (gray-700)

Generates fully self-contained HTML — inline SVG sparkline, no external assets.
"""

from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# SVG sparkline  (matches the mini-chart style used in the wishlist widget)
# ---------------------------------------------------------------------------

def _sparkline_svg(closes: list[float], width: int = 464, height: int = 110) -> str:
    if len(closes) < 2:
        return ""

    mn  = min(closes)
    mx  = max(closes)
    rng = mx - mn or 1

    px_l, px_r, py_t, py_b = 0, 0, 8, 8
    w = width  - px_l - px_r
    h = height - py_t - py_b

    def px(i):  return px_l + (i / (len(closes) - 1)) * w
    def py(v):  return py_t + (1 - (v - mn) / rng) * h

    pts   = [(px(i), py(c)) for i, c in enumerate(closes)]
    up    = closes[-1] >= closes[0]
    color = "#FFD700" if up else "#ff4444"

    line_d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    fill_d = line_d + f" L {pts[-1][0]:.2f},{py_t+h:.2f} L {pts[0][0]:.2f},{py_t+h:.2f} Z"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" style="display:block;width:100%;border-radius:8px;background:#0d0d0d">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="{color}" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0.01"/>
    </linearGradient>
  </defs>
  <path d="{fill_d}" fill="url(#g)" stroke="none"/>
  <path d="{line_d}" fill="none" stroke="{color}" stroke-width="1.8"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


# ---------------------------------------------------------------------------
# Shared HTML primitives
# ---------------------------------------------------------------------------

_OUTER = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>FXTrade</title>
</head>
<body style="margin:0;padding:0;background:#000000;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
             -webkit-font-smoothing:antialiased">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
         style="background:#000000;padding:40px 16px">
    <tr><td align="center">
      <!-- card -->
      <table role="presentation" width="100%"
             style="max-width:520px;background:#0a0a0a;border-radius:16px;
                    border:1px solid #1e1e1e;overflow:hidden">
        {CONTENT}
        {FOOTER}
      </table>
    </td></tr>
  </table>
</body>
</html>"""

_FOOTER = """
        <!-- footer -->
        <tr>
          <td style="padding:16px 28px 24px;border-top:1px solid #1e1e1e">
            <p style="margin:0;font-size:11px;color:#374151;line-height:1.7">
              This is an automated confirmation from FXTrade.&nbsp;
              If you did not initiate this action, please change your password immediately.
            </p>
          </td>
        </tr>"""

def _header(badge_text: str, badge_color: str = "#FFD700") -> str:
    return f"""
        <!-- header -->
        <tr>
          <td style="padding:22px 28px 20px;
                     background:linear-gradient(135deg,#111100 0%,#0a0a0a 100%);
                     border-bottom:1px solid #1e1e1e">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <!-- wordmark -->
                  <span style="font-size:24px;font-weight:900;color:#FFD700;
                               letter-spacing:-1px;line-height:1">FXTrade</span>
                </td>
                <td align="right" style="vertical-align:middle">
                  <span style="display:inline-block;
                               background:{badge_color}18;
                               border:1px solid {badge_color}55;
                               color:{badge_color};
                               font-size:11px;font-weight:700;
                               padding:4px 12px;border-radius:999px;
                               letter-spacing:0.8px;text-transform:uppercase">
                    ✓&nbsp;{badge_text}
                  </span>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

def _divider() -> str:
    return """<tr><td style="padding:0 28px">
      <div style="height:1px;background:#1e1e1e"></div></td></tr>"""

def _row(label: str, value: str, value_color: str = "#e5e7eb",
         border: bool = True) -> str:
    border_style = "border-bottom:1px solid #1a1a1a" if border else ""
    return f"""
              <tr>
                <td style="padding:9px 0;color:#6b7280;font-size:13px;{border_style}">{label}</td>
                <td style="padding:9px 0;text-align:right;font-size:13px;
                           font-family:'SF Mono','Fira Code',monospace;
                           color:{value_color};font-weight:600;{border_style}">{value}</td>
              </tr>"""


# ---------------------------------------------------------------------------
# Trade confirmation
# ---------------------------------------------------------------------------

def build_trade_email(
    *,
    from_cur: str,
    to_cur: str,
    sent_amount: float,
    received_amount: float,
    rate: float,
    now: datetime,
    sparkline_closes: list[float],
) -> tuple[str, str]:

    up      = (sparkline_closes[-1] >= sparkline_closes[0]) if len(sparkline_closes) >= 2 else True
    arrow   = "▲" if up else "▼"
    color   = "#FFD700" if up else "#ff4444"
    pct_str = ""
    if len(sparkline_closes) >= 2:
        chg     = ((sparkline_closes[-1] - sparkline_closes[0]) / sparkline_closes[0]) * 100
        pct_str = f"{'+' if chg >= 0 else ''}{chg:.2f}%"

    svg         = _sparkline_svg(sparkline_closes)
    chart_label = f"""
        <tr>
          <td style="padding:20px 28px 6px">
            <p style="margin:0;font-size:11px;color:#4b5563;letter-spacing:0.8px;text-transform:uppercase">
              {from_cur}/{to_cur} &middot; 30-day
              &nbsp;<span style="color:{color};font-weight:700">{arrow} {pct_str}</span>
            </p>
          </td>
        </tr>""" if svg else ""

    chart_row = f"""
        <tr>
          <td style="padding:4px 28px 4px">
            <div style="border-radius:10px;overflow:hidden;border:1px solid #1e1e1e">{svg}</div>
          </td>
        </tr>""" if svg else ""

    # Pair hero
    hero = f"""
        <tr>
          <td style="padding:24px 28px 4px">
            <p style="margin:0;font-size:30px;font-weight:800;color:#ffffff;letter-spacing:-1px;line-height:1">
              {from_cur}<span style="color:#FFD700">/</span>{to_cur}
            </p>
            <p style="margin:5px 0 0;font-size:12px;color:#4b5563;letter-spacing:0.3px">
              {now.strftime("%A, %d %B %Y &middot; %H:%M UTC")}
            </p>
          </td>
        </tr>"""

    rows = (
        _row("Sold",           f"{sent_amount:,.8g} {from_cur}")
        + _row("Received",     f"{received_amount:,.8g} {to_cur}",  "#FFD700")
        + _row("Rate",         f"1 {from_cur} = {rate:.6f} {to_cur}")
        + _row("Fee",          "0%",                                "#22c55e")
        + _row("Status",       "Filled",                            "#22c55e", border=False)
    )

    details = f"""
        <tr>
          <td style="padding:4px 28px 20px">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              {rows}
            </table>
          </td>
        </tr>"""

    content = (
        _header("Executed")
        + hero
        + chart_label
        + chart_row
        + _divider()
        + details
    )

    subject = f"FXTrade: Trade confirmed — {sent_amount:,.8g} {from_cur} → {received_amount:,.8g} {to_cur}"
    html    = _OUTER.replace("{CONTENT}", content).replace("{FOOTER}", _FOOTER)
    return subject, html


# ---------------------------------------------------------------------------
# Transfer confirmation
# ---------------------------------------------------------------------------

def build_transfer_email(
    *,
    currency: str,
    amount: float,
    to_email: str,
    now: datetime,
) -> tuple[str, str]:

    hero = f"""
        <tr>
          <td style="padding:24px 28px 4px">
            <p style="margin:0;font-size:30px;font-weight:800;color:#FFD700;letter-spacing:-1px;line-height:1">
              {amount:,.8g}&nbsp;<span style="color:#ffffff">{currency}</span>
            </p>
            <p style="margin:5px 0 0;font-size:12px;color:#4b5563;letter-spacing:0.3px">
              {now.strftime("%A, %d %B %Y &middot; %H:%M UTC")}
            </p>
          </td>
        </tr>"""

    rows = (
        _row("Amount",    f"{amount:,.8g} {currency}", "#FFD700")
        + _row("To",      to_email,                    "#e5e7eb")
        + _row("Fee",     "0%",                        "#22c55e")
        + _row("Status",  "Delivered",                 "#22c55e", border=False)
    )

    details = f"""
        <tr>
          <td style="padding:4px 28px 20px">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              {rows}
            </table>
          </td>
        </tr>"""

    content = _header("Sent") + hero + _divider() + details
    subject = f"FXTrade: Transfer confirmed — {amount:,.8g} {currency} sent to {to_email}"
    html    = _OUTER.replace("{CONTENT}", content).replace("{FOOTER}", _FOOTER)
    return subject, html
