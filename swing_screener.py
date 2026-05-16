"""
大市值波段交易篩選器
Mega-Cap Swing Trade Screener
市值 $1000億+ | 四大篩選條件
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import time

# ── CSS ──────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

    :root {
        --bg:        #f5f2ed;
        --card:      #faf8f4;
        --accent:    #5c7f6e;
        --accent2:   #8aaf9b;
        --gold:      #b8932a;
        --red:       #c0443a;
        --text:      #2c2c2c;
        --muted:     #8a8680;
        --border:    #ddd9d2;
        --shadow:    rgba(92,127,110,0.12);
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg) !important;
        font-family: 'Noto Sans TC', sans-serif;
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background-color: #edeae4 !important;
        border-right: 1px solid var(--border);
    }

    /* Header */
    .app-header {
        background: linear-gradient(135deg, #2c3e32 0%, #3d5c4a 60%, #5c7f6e 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .app-header::before {
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 160px; height: 160px;
        border-radius: 50%;
        background: rgba(255,255,255,0.05);
    }
    .app-header h1 {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.5rem;
        font-weight: 600;
        color: #f5f2ed;
        margin: 0 0 4px 0;
        letter-spacing: 0.02em;
    }
    .app-header p {
        font-size: 0.8rem;
        color: rgba(245,242,237,0.65);
        margin: 0;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* Filter cards */
    .filter-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }
    .filter-card-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--accent);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    /* Stock result card */
    .stock-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 14px;
        transition: border-color 0.2s, box-shadow 0.2s;
        position: relative;
    }
    .stock-card:hover {
        border-color: var(--accent2);
        box-shadow: 0 4px 20px var(--shadow);
    }
    .stock-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }
    .stock-ticker {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text);
        line-height: 1;
    }
    .stock-name {
        font-size: 0.78rem;
        color: var(--muted);
        margin-top: 3px;
    }
    .stock-price {
        text-align: right;
    }
    .price-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.2rem;
        font-weight: 500;
        color: var(--text);
    }
    .price-change-pos {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        color: var(--accent);
        font-weight: 500;
    }
    .price-change-neg {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        color: var(--red);
        font-weight: 500;
    }

    /* Signal badges */
    .signals-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 12px;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 500;
        font-family: 'IBM Plex Mono', monospace;
        border: 1px solid;
    }
    .badge-accumulation {
        background: rgba(92,127,110,0.1);
        border-color: var(--accent);
        color: var(--accent);
    }
    .badge-ma200 {
        background: rgba(184,147,42,0.1);
        border-color: var(--gold);
        color: var(--gold);
    }
    .badge-higher-low {
        background: rgba(138,175,155,0.15);
        border-color: var(--accent2);
        color: #3d6b58;
    }
    .badge-news {
        background: rgba(192,68,58,0.1);
        border-color: var(--red);
        color: var(--red);
    }

    /* Market cap / score strip */
    .stock-meta {
        display: flex;
        gap: 18px;
        padding-top: 12px;
        border-top: 1px solid var(--border);
        flex-wrap: wrap;
    }
    .meta-item {
        display: flex;
        flex-direction: column;
    }
    .meta-label {
        font-size: 0.65rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-family: 'IBM Plex Mono', monospace;
    }
    .meta-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text);
    }

    /* Score bar */
    .score-bar-wrap {
        margin-top: 4px;
    }
    .score-bar-bg {
        background: var(--border);
        border-radius: 4px;
        height: 5px;
        width: 100px;
        overflow: hidden;
    }
    .score-bar-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, var(--accent2), var(--accent));
    }

    /* Section divider */
    .section-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        color: var(--muted);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 20px 0 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border);
    }

    /* Status pill */
    .status-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
    }
    .status-running {
        background: rgba(92,127,110,0.15);
        color: var(--accent);
    }
    .status-done {
        background: rgba(184,147,42,0.12);
        color: var(--gold);
    }

    /* Buttons */
    .stButton > button {
        background: var(--accent) !important;
        color: #f5f2ed !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 8px 22px !important;
        letter-spacing: 0.04em !important;
        transition: background 0.2s !important;
    }
    .stButton > button:hover {
        background: #4a6b5c !important;
    }

    /* Checkbox */
    .stCheckbox label {
        font-size: 0.82rem !important;
        color: var(--text) !important;
        font-family: 'Noto Sans TC', sans-serif !important;
    }

    /* Slider */
    .stSlider label {
        font-size: 0.8rem !important;
        font-family: 'IBM Plex Mono', monospace !important;
        color: var(--muted) !important;
    }

    /* Progress */
    .stProgress > div > div {
        background: var(--accent) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.8rem !important;
    }

    /* No results */
    .no-results {
        text-align: center;
        padding: 48px 24px;
        color: var(--muted);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ── Universe ──────────────────────────────────────────────────────────────────

MEGA_CAP_UNIVERSE = [
    # US Tech
    "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","TSM","ORCL",
    "ASML","SAP","CSCO","ADBE","AMD","QCOM","TXN","INTC","IBM","AMAT",
    # US Finance
    "BRK-B","JPM","V","MA","BAC","WFC","GS","MS","C","AXP","BLK","SCHW",
    # US Healthcare
    "LLY","JNJ","UNH","ABBV","MRK","TMO","ABT","DHR","PFE","AMGN",
    # US Consumer
    "WMT","COST","HD","MCD","KO","PEP","NKE","SBUX","PM","MO",
    # US Energy / Industrials
    "XOM","CVX","COP","SLB","CAT","HON","RTX","BA","UPS","DE",
    # US Telecom / Utilities
    "VZ","T","NEE","DUK","SO",
    # ETFs (large, liquid)
    "SPY","QQQ","IWM","XLF","XLE","XLK","GLD","SLV",
]


# ── Data fetch ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def fetch_ticker_data(ticker: str):
    """Returns (hist DataFrame, market_cap_billions float) — both pickle-safe."""
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="1y", interval="1d", timeout=10)
        if hist.empty or len(hist) < 60:
            return None, 0.0
        # Extract market_cap immediately so we only return pickle-safe types
        market_cap_b = 0.0
        try:
            fi = tk.fast_info
            mc = getattr(fi, "market_cap", None)
            if mc and mc > 0:
                market_cap_b = mc / 1e9
        except Exception:
            pass
        return hist, market_cap_b
    except Exception:
        return None, 0.0


def get_market_cap(market_cap_b: float) -> float:
    """Pass-through — market_cap already extracted in fetch_ticker_data."""
    return market_cap_b


# ── Signal logic ─────────────────────────────────────────────────────────────

def signal_accumulation(hist: pd.DataFrame) -> tuple[bool, str]:
    """
    Accumulation: OBV trending up + recent volume > 20-day avg
    """
    try:
        close = hist["Close"]
        volume = hist["Volume"]
        # OBV
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        obv_ma = obv.rolling(20).mean()
        obv_rising = obv.iloc[-1] > obv_ma.iloc[-1] and obv.iloc[-1] > obv.iloc[-20]

        # Volume surge: recent 5-day avg vs 20-day avg
        vol_5  = volume.iloc[-5:].mean()
        vol_20 = volume.iloc[-20:].mean()
        vol_surge = vol_5 > vol_20 * 1.15

        # Price above 50-day EMA
        ema50 = close.ewm(span=50, adjust=False).mean()
        price_above_ema = close.iloc[-1] > ema50.iloc[-1]

        score = sum([obv_rising, vol_surge, price_above_ema])
        ok = score >= 2
        detail = f"OBV↑:{obv_rising} | Vol+:{vol_surge} | EMA50↑:{price_above_ema}"
        return ok, detail
    except Exception:
        return False, "計算錯誤"


def signal_ma200_test(hist: pd.DataFrame) -> tuple[bool, str]:
    """
    Testing 200 MA: price within ±3% of 200-day SMA, bouncing up from it.
    """
    try:
        close = hist["Close"]
        if len(close) < 200:
            return False, "數據不足"
        ma200 = close.rolling(200).mean()
        price = close.iloc[-1]
        ma = ma200.iloc[-1]
        pct_from_ma = (price - ma) / ma * 100

        near_ma = abs(pct_from_ma) <= 3.5
        # Recent 5-day bounce: price was below or at MA and is now above/at
        was_below = close.iloc[-6:-1].min() <= ma200.iloc[-6:-1].max() * 1.01
        bouncing = close.iloc[-1] > close.iloc[-3]

        ok = near_ma and (was_below or abs(pct_from_ma) <= 1.5)
        detail = f"距200MA: {pct_from_ma:+.1f}% | 測試中:{near_ma} | 反彈:{bouncing}"
        return ok, detail
    except Exception:
        return False, "計算錯誤"


def signal_higher_low(hist: pd.DataFrame) -> tuple[bool, str]:
    """
    Higher low pattern: recent swing lows are ascending.
    """
    try:
        low = hist["Low"]
        close = hist["Close"]
        # Find local lows (simple: rolling 10-day minimum, compare last 3 occurrences)
        rolling_min = low.rolling(10, center=True).min()
        local_lows = low[low == rolling_min].dropna()

        if len(local_lows) < 3:
            return False, "擺動低點不足"

        last3 = local_lows.iloc[-3:]
        hl = last3.iloc[-1] > last3.iloc[-2] > last3.iloc[-3]

        # Also check: 50-day EMA slope positive
        ema50 = close.ewm(span=50, adjust=False).mean()
        ema_rising = ema50.iloc[-1] > ema50.iloc[-10]

        ok = hl and ema_rising
        vals = [f"{v:.2f}" for v in last3.values]
        detail = f"低點序列: {' < '.join(vals) if not hl else ' → '.join(vals)} | EMA50↑:{ema_rising}"
        return ok, detail
    except Exception:
        return False, "計算錯誤"


def signal_news(ticker: str) -> tuple[bool, str]:
    """
    News signal: check yfinance news count as a proxy.
    """
    try:
        tk = yf.Ticker(ticker)
        news = tk.news
        if not news:
            return False, "無最新新聞"
        recent_news = [n for n in news if (time.time() - n.get("providerPublishTime", 0)) < 86400 * 7]
        count = len(recent_news)
        ok = count >= 2
        first_title = recent_news[0].get("title", "")[:60] if recent_news else ""
        detail = f"7日內新聞: {count}則 | {first_title}..."
        return ok, detail
    except Exception:
        return False, "新聞抓取失敗"


# ── Main scan ─────────────────────────────────────────────────────────────────

def run_scan(
    min_market_cap_b: float,
    use_accumulation: bool,
    use_ma200: bool,
    use_higher_low: bool,
    use_news: bool,
    min_signals: int,
    progress_bar,
    status_text,
):
    results = []
    total = len(MEGA_CAP_UNIVERSE)

    for i, ticker in enumerate(MEGA_CAP_UNIVERSE):
        progress_bar.progress((i + 1) / total)
        status_text.markdown(
            f'<span class="status-pill status-running">掃描中 {i+1}/{total} — {ticker}</span>',
            unsafe_allow_html=True,
        )

        hist, mc_b = fetch_ticker_data(ticker)
        if hist is None:
            continue
        if mc_b < min_market_cap_b:
            continue

        price = hist["Close"].iloc[-1]
        prev  = hist["Close"].iloc[-2]
        chg_pct = (price - prev) / prev * 100

        signals = {}
        signal_count = 0

        if use_accumulation:
            ok, detail = signal_accumulation(hist)
            signals["accumulation"] = (ok, detail)
            if ok: signal_count += 1

        if use_ma200:
            ok, detail = signal_ma200_test(hist)
            signals["ma200"] = (ok, detail)
            if ok: signal_count += 1

        if use_higher_low:
            ok, detail = signal_higher_low(hist)
            signals["higher_low"] = (ok, detail)
            if ok: signal_count += 1

        if use_news:
            ok, detail = signal_news(ticker)
            signals["news"] = (ok, detail)
            if ok: signal_count += 1

        enabled_count = sum([use_accumulation, use_ma200, use_higher_low, use_news])
        if enabled_count == 0:
            continue

        if signal_count < min_signals:
            continue

        # Volume ratio
        vol_ratio = hist["Volume"].iloc[-5:].mean() / hist["Volume"].iloc[-20:].mean()

        results.append({
            "ticker":       ticker,
            "name":         tk_name(ticker),
            "price":        price,
            "chg_pct":      chg_pct,
            "market_cap_b": mc_b,
            "signal_count": signal_count,
            "enabled_count":enabled_count,
            "signals":      signals,
            "vol_ratio":    vol_ratio,
        })

    results.sort(key=lambda x: (-x["signal_count"], -x["market_cap_b"]))
    return results


# Ticker → company name cache (lightweight)
_NAME_MAP = {
    "AAPL":"Apple","MSFT":"Microsoft","NVDA":"NVIDIA","GOOGL":"Alphabet",
    "AMZN":"Amazon","META":"Meta","TSLA":"Tesla","AVGO":"Broadcom",
    "TSM":"TSMC","ORCL":"Oracle","ASML":"ASML","SAP":"SAP","CSCO":"Cisco",
    "ADBE":"Adobe","AMD":"AMD","QCOM":"Qualcomm","TXN":"Texas Instruments",
    "INTC":"Intel","IBM":"IBM","AMAT":"Applied Materials",
    "BRK-B":"Berkshire","JPM":"JPMorgan","V":"Visa","MA":"Mastercard",
    "BAC":"Bank of America","WFC":"Wells Fargo","GS":"Goldman Sachs",
    "MS":"Morgan Stanley","C":"Citigroup","AXP":"Amex","BLK":"BlackRock",
    "SCHW":"Schwab","LLY":"Eli Lilly","JNJ":"J&J","UNH":"UnitedHealth",
    "ABBV":"AbbVie","MRK":"Merck","TMO":"Thermo Fisher","ABT":"Abbott",
    "DHR":"Danaher","PFE":"Pfizer","AMGN":"Amgen",
    "WMT":"Walmart","COST":"Costco","HD":"Home Depot","MCD":"McDonald's",
    "KO":"Coca-Cola","PEP":"PepsiCo","NKE":"Nike","SBUX":"Starbucks",
    "PM":"Philip Morris","MO":"Altria",
    "XOM":"ExxonMobil","CVX":"Chevron","COP":"ConocoPhillips","SLB":"SLB",
    "CAT":"Caterpillar","HON":"Honeywell","RTX":"RTX","BA":"Boeing",
    "UPS":"UPS","DE":"Deere",
    "VZ":"Verizon","T":"AT&T","NEE":"NextEra","DUK":"Duke Energy","SO":"Southern",
    "SPY":"S&P500 ETF","QQQ":"Nasdaq ETF","IWM":"Russell ETF",
    "XLF":"金融ETF","XLE":"能源ETF","XLK":"科技ETF","GLD":"黃金ETF","SLV":"白銀ETF",
}

def tk_name(ticker: str) -> str:
    return _NAME_MAP.get(ticker, ticker)


# ── Render result card ────────────────────────────────────────────────────────

def render_stock_card(r: dict):
    ticker       = r["ticker"]
    name         = r["name"]
    price        = r["price"]
    chg_pct      = r["chg_pct"]
    mc_b         = r["market_cap_b"]
    signal_count = r["signal_count"]
    enabled      = r["enabled_count"]
    signals      = r["signals"]
    vol_ratio    = r["vol_ratio"]

    chg_class = "price-change-pos" if chg_pct >= 0 else "price-change-neg"
    chg_arrow = "▲" if chg_pct >= 0 else "▼"

    # Build badge HTML
    badges_html = ""
    badge_map = {
        "accumulation": ("badge-accumulation", "📈 累積中"),
        "ma200":        ("badge-ma200",        "〰 測試200MA"),
        "higher_low":   ("badge-higher-low",   "🔺 更高低點"),
        "news":         ("badge-news",          "📰 重大新聞"),
    }
    for key, (css, label) in badge_map.items():
        if key in signals and signals[key][0]:
            badges_html += f'<span class="badge {css}">{label}</span>'

    score_pct = int(signal_count / max(enabled, 1) * 100)

    mc_str = f"${mc_b:,.0f}B" if mc_b < 10000 else f"${mc_b/1000:,.1f}T"

    card_html = f"""
    <div class="stock-card">
      <div class="stock-card-header">
        <div>
          <div class="stock-ticker">{ticker}</div>
          <div class="stock-name">{name}</div>
        </div>
        <div class="stock-price">
          <div class="price-value">${price:,.2f}</div>
          <div class="{chg_class}">{chg_arrow} {abs(chg_pct):.2f}%</div>
        </div>
      </div>
      <div class="signals-row">{badges_html}</div>
      <div class="stock-meta">
        <div class="meta-item">
          <span class="meta-label">市值</span>
          <span class="meta-value">{mc_str}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">信號得分</span>
          <span class="meta-value">{signal_count}/{enabled}</span>
          <div class="score-bar-wrap">
            <div class="score-bar-bg">
              <div class="score-bar-fill" style="width:{score_pct}%"></div>
            </div>
          </div>
        </div>
        <div class="meta-item">
          <span class="meta-label">成交量比率</span>
          <span class="meta-value">{vol_ratio:.2f}x</span>
        </div>
      </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # Signal detail expander
    with st.expander(f"📋 {ticker} 信號詳情"):
        label_map = {
            "accumulation": "📈 累積信號",
            "ma200":        "〰 200MA測試",
            "higher_low":   "🔺 更高低點",
            "news":         "📰 重大新聞",
        }
        for key, lbl in label_map.items():
            if key in signals:
                ok, detail = signals[key]
                icon = "✅" if ok else "❌"
                st.markdown(f"**{icon} {lbl}**")
                st.caption(detail)


# ── App ───────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="大市值波段篩選器",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()

    # Header
    st.markdown("""
    <div class="app-header">
      <h1>📊 MEGA-CAP SWING SCREENER</h1>
      <p>大市值波段交易篩選器 · 市值 $1000億+ · 四大信號系統</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown('<div class="filter-card"><div class="filter-card-title">⚙ 基本設定</div>', unsafe_allow_html=True)
        min_cap = st.slider("最低市值 (十億美元)", 50, 500, 100, step=50,
                            help="100 = $1000億")
        min_signals = st.slider("最少符合信號數", 1, 4, 2)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="filter-card"><div class="filter-card-title">🎯 篩選條件</div>', unsafe_allow_html=True)
        use_accumulation = st.checkbox("📈 正在累積", value=True, help="OBV上升 + 成交量放大 + 價格在EMA50以上")
        use_ma200        = st.checkbox("〰 測試200日均線", value=True, help="股價在200MA ±3.5%範圍內")
        use_higher_low   = st.checkbox("🔺 形成更高低點", value=True, help="近期擺動低點持續走高")
        use_news         = st.checkbox("📰 重大新聞", value=False, help="7日內有2則以上新聞報導")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(
            '<p style="font-family:IBM Plex Mono;font-size:0.68rem;color:#8a8680;">'
            '數據來源: Yahoo Finance<br>'
            '更新: 每5分鐘快取<br>'
            '⚠ 僅供參考，非投資建議</p>',
            unsafe_allow_html=True
        )

    # ── Scan button ──
    col1, col2 = st.columns([2, 5])
    with col1:
        run = st.button("🔍 開始掃描", use_container_width=True)

    if run or st.session_state.get("scan_results"):
        if run:
            # Clear old results
            st.session_state["scan_results"] = None

            enabled_count = sum([use_accumulation, use_ma200, use_higher_low, use_news])
            if enabled_count == 0:
                st.warning("請至少選擇一個篩選條件")
                return

            progress_bar = st.progress(0)
            status_text  = st.empty()

            with st.spinner(""):
                results = run_scan(
                    min_market_cap_b=min_cap,
                    use_accumulation=use_accumulation,
                    use_ma200=use_ma200,
                    use_higher_low=use_higher_low,
                    use_news=use_news,
                    min_signals=min_signals,
                    progress_bar=progress_bar,
                    status_text=status_text,
                )

            progress_bar.empty()
            status_text.markdown(
                f'<span class="status-pill status-done">✓ 掃描完成 — 找到 {len(results)} 支股票</span>',
                unsafe_allow_html=True,
            )
            st.session_state["scan_results"] = results
            st.session_state["scan_settings"] = {
                "min_cap": min_cap,
                "use_accumulation": use_accumulation,
                "use_ma200": use_ma200,
                "use_higher_low": use_higher_low,
                "use_news": use_news,
                "min_signals": min_signals,
            }

        results = st.session_state.get("scan_results", [])

        if not results:
            st.markdown(
                '<div class="no-results">😶 沒有符合條件的股票<br>'
                '<span style="font-size:0.75rem">嘗試降低最少信號數或市值門檻</span></div>',
                unsafe_allow_html=True,
            )
            return

        # ── Summary stats ──
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("篩選結果", f"{len(results)} 支")
        with m2:
            full_match = sum(1 for r in results if r["signal_count"] == r["enabled_count"])
            st.metric("全信號命中", f"{full_match} 支")
        with m3:
            avg_mc = np.mean([r["market_cap_b"] for r in results])
            st.metric("平均市值", f"${avg_mc:,.0f}B")
        with m4:
            avg_vol = np.mean([r["vol_ratio"] for r in results])
            st.metric("平均成交量比", f"{avg_vol:.2f}x")

        st.markdown("")

        # ── Group by signal count ──
        max_sig = max(r["signal_count"] for r in results)
        for sig_n in range(max_sig, 0, -1):
            group = [r for r in results if r["signal_count"] == sig_n]
            if not group:
                continue
            enabled = group[0]["enabled_count"]
            st.markdown(
                f'<div class="section-label">★ {sig_n}/{enabled} 信號命中 — {len(group)} 支</div>',
                unsafe_allow_html=True,
            )
            for r in group:
                render_stock_card(r)

        # ── Export CSV ──
        st.markdown("---")
        export_data = []
        for r in results:
            row = {
                "Ticker": r["ticker"],
                "名稱": r["name"],
                "價格": round(r["price"], 2),
                "日變化%": round(r["chg_pct"], 2),
                "市值(B)": round(r["market_cap_b"], 1),
                "信號數": r["signal_count"],
                "成交量比": round(r["vol_ratio"], 2),
                "累積信號": r["signals"].get("accumulation", (False, ""))[0],
                "200MA測試": r["signals"].get("ma200", (False, ""))[0],
                "更高低點": r["signals"].get("higher_low", (False, ""))[0],
                "重大新聞": r["signals"].get("news", (False, ""))[0],
            }
            export_data.append(row)
        df_export = pd.DataFrame(export_data)
        csv = df_export.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇ 下載 CSV",
            data=csv,
            file_name=f"swing_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
    else:
        st.markdown(
            '<div class="no-results" style="padding:60px 24px">'
            '👆 選擇篩選條件後點擊「開始掃描」</div>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
