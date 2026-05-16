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
    .badge-fundamental {
        background: linear-gradient(90deg, rgba(192,68,58,0.12), rgba(184,147,42,0.12));
        border-color: #c0443a;
        color: #8a2020;
        font-weight: 600;
    }
    .badge-vol-expansion {
        background: linear-gradient(90deg, rgba(92,127,110,0.15), rgba(138,175,155,0.15));
        border-color: #5c7f6e;
        color: #2c5a48;
        font-weight: 600;
    }
    .badge-trend-accel {
        background: linear-gradient(90deg, rgba(184,147,42,0.15), rgba(200,160,50,0.10));
        border-color: #b8932a;
        color: #7a5a00;
        font-weight: 600;
    }
    .badge-base {
        background: rgba(92,127,110,0.08);
        border-color: #7a9e8e;
        color: #4a7a68;
    }
    .badge-breakout {
        background: rgba(184,147,42,0.12);
        border-color: #c8a030;
        color: #8a6010;
    }
    .badge-catalyst {
        background: rgba(120,80,160,0.1);
        border-color: #9060c0;
        color: #6040a0;
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
# 三大核心條件：業績質變 | 資金狂入 | 技術突破
# Framework: ChatGPT × Minervini × O'Neil

# ─────────────────────────────────────────────
# 條件一：業績／故事出現「質變」
# ─────────────────────────────────────────────

def signal_fundamental_shift(ticker: str, hist: pd.DataFrame) -> tuple[bool, str]:
    """
    業績質變 (Fundamental Shift):
    代理指標（yfinance 無法即時財報，用技術代理）：
    1. 強於大盤 Relative Strength: 近60日跑贏 SPY
    2. 利空不跌: 近20日下跌日收盤 > 前一日收盤（反彈力強）
    3. 跳空缺口印記: 近30日曾出現 Gap-Up >= 2% (財報/重大消息)
    4. 股價創52週新高（市場開始重新估值）
    """
    try:
        close  = hist["Close"]
        high   = hist["High"]
        opens  = hist["Open"]

        # 1. Relative Strength vs SPY (60-day return)
        rs_ok = False
        try:
            spy = yf.Ticker("SPY").history(period="90d", interval="1d")["Close"]
            if not spy.empty and len(spy) >= 60:
                stock_ret = (close.iloc[-1] / close.iloc[-60] - 1) * 100
                spy_ret   = (spy.iloc[-1]  / spy.iloc[-60]  - 1) * 100
                rs_ok = stock_ret > spy_ret + 5   # outperform by 5%+
        except Exception:
            pass

        # 2. 利空不跌 (down days but closes off lows — resilience)
        down_days = close.diff().iloc[-20:] < 0
        if down_days.sum() > 0:
            down_idx = close.diff().iloc[-20:][down_days].index
            resilience_count = 0
            for idx in down_idx:
                loc = close.index.get_loc(idx)
                if loc > 0:
                    if close.iloc[loc] > close.iloc[loc - 1] * 0.995:  # barely down
                        resilience_count += 1
            no_panic_selling = resilience_count >= down_days.sum() * 0.5
        else:
            no_panic_selling = True

        # 3. Earnings gap-up proxy: gap >= 2% in last 30 days
        gap_up = False
        gap_pct = 0.0
        prev_close = close.shift(1)
        for j in range(-30, -1):
            try:
                g = (opens.iloc[j] - prev_close.iloc[j]) / prev_close.iloc[j] * 100
                if g >= 2.0:
                    gap_up = True
                    gap_pct = max(gap_pct, g)
            except Exception:
                pass

        # 4. 52-week high — market re-rating
        wk52_high = close.iloc[-252:].max() if len(close) >= 252 else close.max()
        near_52wk_high = close.iloc[-1] >= wk52_high * 0.95

        score = sum([rs_ok, no_panic_selling, gap_up, near_52wk_high])
        ok = score >= 2

        detail = (f"強於大盤:{rs_ok} | 利空不跌:{no_panic_selling} | "
                  f"跳空{gap_pct:.1f}%:{gap_up} | 近52週高:{near_52wk_high} | 得分:{score}/4")
        return ok, detail
    except Exception as e:
        return False, f"計算錯誤: {e}"


# ─────────────────────────────────────────────
# 條件二：資金瘋狂流入（Volume Expansion）
# ─────────────────────────────────────────────

def signal_volume_expansion(hist: pd.DataFrame) -> tuple[bool, str]:
    """
    資金狂入 (Volume Expansion / Institutional Accumulation):
    1. RVOL (Relative Volume): 近5日均量 vs 60日均量 >= 1.5x
    2. OBV 持續走高（機構悄悄建倉痕跡）
    3. 突破時放量: 近10日最大成交量 >= 60日均量 x 2 且當日收漲
    4. 量價齊升：上漲日平均量 > 下跌日平均量 x 1.3
    """
    try:
        close  = hist["Close"]
        volume = hist["Volume"]

        # 1. RVOL
        vol_5    = volume.iloc[-5:].mean()
        vol_60   = volume.iloc[-60:].mean()
        rvol     = vol_5 / vol_60 if vol_60 > 0 else 0
        rvol_ok  = rvol >= 1.5

        # 2. OBV trend (rising over last 30 days)
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        obv_ok = obv.iloc[-1] > obv.iloc[-30] and obv.iloc[-1] > obv.rolling(20).mean().iloc[-1]

        # 3. Breakout volume: max vol in last 10 days vs 60d avg, on an up day
        recent_10 = volume.iloc[-10:]
        recent_10_close = close.iloc[-10:]
        best_vol_idx = recent_10.idxmax()
        best_vol = recent_10.max()
        best_vol_loc = close.index.get_loc(best_vol_idx)
        up_on_best_vol = close.iloc[best_vol_loc] > close.iloc[best_vol_loc - 1]
        breakout_vol_ok = (best_vol >= vol_60 * 2.0) and up_on_best_vol

        # 4. Up-day volume vs down-day volume
        changes = close.diff().iloc[-30:]
        vol_30  = volume.iloc[-30:]
        up_vol   = vol_30[changes > 0].mean()
        down_vol = vol_30[changes < 0].mean()
        vol_bias_ok = (up_vol / down_vol >= 1.3) if (down_vol and down_vol > 0) else True

        score = sum([rvol_ok, obv_ok, breakout_vol_ok, vol_bias_ok])
        ok = score >= 2

        detail = (f"RVOL {rvol:.2f}x:{rvol_ok} | OBV↑:{obv_ok} | "
                  f"突破量{best_vol/vol_60:.1f}x:{breakout_vol_ok} | 量價齊升:{vol_bias_ok} | 得分:{score}/4")
        return ok, detail
    except Exception as e:
        return False, f"計算錯誤: {e}"


# ─────────────────────────────────────────────
# 條件三：技術面進入「趨勢加速」
# ─────────────────────────────────────────────

def signal_trend_acceleration(hist: pd.DataFrame) -> tuple[bool, str]:
    """
    技術突破加速 (Trend Acceleration / Base Breakout):
    1. EMA 多頭排列: EMA10 > EMA21 > EMA50 > EMA200
    2. Higher High + Higher Low (近期擺動點遞升)
    3. 盤整後突破 (VCP/Base Breakout): ATR收窄後近5日突破
    4. MACD 維持強勢: MACD線 > Signal線 且 Histogram > 0
    """
    try:
        close  = hist["Close"]
        high   = hist["High"]
        low    = hist["Low"]
        volume = hist["Volume"]

        # 1. EMA 多頭排列
        ema10  = close.ewm(span=10,  adjust=False).mean()
        ema21  = close.ewm(span=21,  adjust=False).mean()
        ema50  = close.ewm(span=50,  adjust=False).mean()
        ema200 = close.ewm(span=200, adjust=False).mean()
        ema_stack = (ema10.iloc[-1] > ema21.iloc[-1] > ema50.iloc[-1] > ema200.iloc[-1])

        # 2. Higher High + Higher Low
        roll = low.rolling(10, center=True).min()
        local_lows = low[low == roll].dropna()
        roll_h = high.rolling(10, center=True).max()
        local_highs = high[high == roll_h].dropna()
        hh = len(local_highs) >= 2 and local_highs.iloc[-1] > local_highs.iloc[-2]
        hl = len(local_lows)  >= 2 and local_lows.iloc[-1]  > local_lows.iloc[-2]
        hh_hl = hh and hl

        # 3. VCP Breakout: ATR contraction then price breaks
        prev_close = close.shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low  - prev_close).abs(),
        ], axis=1).max(axis=1)
        atr = tr.ewm(span=14, adjust=False).mean()
        atr_contracting = atr.iloc[-5:].mean() < atr.iloc[-20:-5].mean() * 0.85
        base_high = close.iloc[-25:-5].max()
        price_broke_out = close.iloc[-1] > base_high
        vcp_ok = atr_contracting and price_broke_out

        # 4. MACD (12/26/9)
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_line   = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram   = macd_line - signal_line
        macd_ok = (macd_line.iloc[-1] > signal_line.iloc[-1]) and (histogram.iloc[-1] > 0)

        score = sum([ema_stack, hh_hl, vcp_ok, macd_ok])
        ok = score >= 2

        detail = (f"EMA多頭:{ema_stack} | HH+HL:{hh_hl} | "
                  f"VCP突破:{vcp_ok} | MACD強:{macd_ok} | 得分:{score}/4")
        return ok, detail
    except Exception as e:
        return False, f"計算錯誤: {e}"


# ─────────────────────────────────────────────
# 舊信號保留（可選擇性開啟）
# ─────────────────────────────────────────────

def signal_accumulation(hist: pd.DataFrame) -> tuple[bool, str]:
    try:
        close = hist["Close"]
        volume = hist["Volume"]
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        obv_ma = obv.rolling(20).mean()
        obv_rising = obv.iloc[-1] > obv_ma.iloc[-1] and obv.iloc[-1] > obv.iloc[-20]
        vol_5  = volume.iloc[-5:].mean()
        vol_20 = volume.iloc[-20:].mean()
        vol_surge = vol_5 > vol_20 * 1.15
        ema50 = close.ewm(span=50, adjust=False).mean()
        price_above_ema = close.iloc[-1] > ema50.iloc[-1]
        score = sum([obv_rising, vol_surge, price_above_ema])
        ok = score >= 2
        detail = f"OBV↑:{obv_rising} | Vol+:{vol_surge} | EMA50↑:{price_above_ema}"
        return ok, detail
    except Exception:
        return False, "計算錯誤"


def signal_ma200_test(hist: pd.DataFrame) -> tuple[bool, str]:
    try:
        close = hist["Close"]
        if len(close) < 200:
            return False, "數據不足"
        ma200 = close.rolling(200).mean()
        price = close.iloc[-1]
        ma = ma200.iloc[-1]
        pct_from_ma = (price - ma) / ma * 100
        near_ma = abs(pct_from_ma) <= 3.5
        was_below = close.iloc[-6:-1].min() <= ma200.iloc[-6:-1].max() * 1.01
        ok = near_ma and (was_below or abs(pct_from_ma) <= 1.5)
        detail = f"距200MA: {pct_from_ma:+.1f}% | 測試中:{near_ma}"
        return ok, detail
    except Exception:
        return False, "計算錯誤"


def signal_higher_low(hist: pd.DataFrame) -> tuple[bool, str]:
    try:
        low = hist["Low"]
        close = hist["Close"]
        rolling_min = low.rolling(10, center=True).min()
        local_lows = low[low == rolling_min].dropna()
        if len(local_lows) < 3:
            return False, "擺動低點不足"
        last3 = local_lows.iloc[-3:]
        hl = last3.iloc[-1] > last3.iloc[-2] > last3.iloc[-3]
        ema50 = close.ewm(span=50, adjust=False).mean()
        ema_rising = ema50.iloc[-1] > ema50.iloc[-10]
        ok = hl and ema_rising
        vals = [f"{v:.2f}" for v in last3.values]
        detail = f"低點: {' → '.join(vals) if hl else ' ✗ '.join(vals)} | EMA50↑:{ema_rising}"
        return ok, detail
    except Exception:
        return False, "計算錯誤"


def signal_news(ticker: str) -> tuple[bool, str]:
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


def signal_base_consolidation(hist: pd.DataFrame) -> tuple[bool, str]:
    try:
        close = hist["Close"]; high = hist["High"]; low = hist["Low"]; volume = hist["Volume"]
        prev_close = close.shift(1)
        tr = pd.concat([(high-low),(high-prev_close).abs(),(low-prev_close).abs()],axis=1).max(axis=1)
        atr14 = tr.ewm(span=14, adjust=False).mean()
        atr_contracting = atr14.iloc[-20:].mean() < atr14.iloc[-40:-20].mean() * 0.85
        range_recent = (high.iloc[-30:].max() - low.iloc[-30:].min()) / close.iloc[-30:].mean()
        range_prior  = (high.iloc[-60:-30].max() - low.iloc[-60:-30].min()) / close.iloc[-60:-30].mean()
        range_tightening = range_recent < range_prior * 0.80
        vol_drying = volume.iloc[-20:].mean() < volume.iloc[-40:-20].mean() * 0.90
        ema50 = close.ewm(span=50, adjust=False).mean()
        above_ema50 = close.iloc[-1] > ema50.iloc[-1]
        score = sum([atr_contracting, range_tightening, vol_drying, above_ema50])
        ok = score >= 3
        detail = f"ATR收窄:{atr_contracting} | 價幅緊:{range_tightening} | 量縮:{vol_drying} | EMA50上:{above_ema50}"
        return ok, detail
    except Exception as e:
        return False, f"計算錯誤: {e}"


def signal_volume_breakout(hist: pd.DataFrame) -> tuple[bool, str]:
    try:
        close = hist["Close"]; high = hist["High"]; low = hist["Low"]; volume = hist["Volume"]
        base_high = close.iloc[-65:-5].max()
        breakout_day = None
        for i in range(-5, 0):
            if close.iloc[i] > base_high:
                breakout_day = i
                break
        if breakout_day is None:
            near_break = (close.iloc[-1] - base_high) / base_high * 100
            return False, f"未突破 | 距60日高點: {near_break:+.1f}%"
        vol_on_day = volume.iloc[breakout_day]
        vol_20_avg = volume.iloc[-25:breakout_day if breakout_day != -1 else None].mean()
        vol_ratio  = vol_on_day / vol_20_avg if vol_20_avg > 0 else 0
        day_range  = high.iloc[breakout_day] - low.iloc[breakout_day]
        close_pos  = (close.iloc[breakout_day] - low.iloc[breakout_day]) / day_range if day_range > 0 else 0
        ok = (vol_ratio >= 1.5) and (close_pos >= 0.6)
        detail = f"量比:{vol_ratio:.1f}x | 收盤位:{close_pos*100:.0f}% | 守住:{close.iloc[-1]>=close.iloc[breakout_day]*0.97}"
        return ok, detail
    except Exception as e:
        return False, f"計算錯誤: {e}"


def signal_catalyst(ticker: str) -> tuple[bool, str]:
    try:
        import time as _time
        tk = yf.Ticker(ticker)
        news_count = 0; news_title = ""
        try:
            news = tk.news or []
            recent = [n for n in news if (_time.time() - n.get("providerPublishTime", 0)) < 86400 * 7]
            news_count = len(recent)
            if recent: news_title = recent[0].get("title", "")[:50]
        except Exception:
            pass
        hist2 = tk.history(period="30d", interval="1d")
        gap_up = False; gap_pct = 0.0
        if not hist2.empty and len(hist2) > 2:
            for j in range(-10, -1):
                try:
                    g = (hist2["Open"].iloc[j] - hist2["Close"].iloc[j-1]) / hist2["Close"].iloc[j-1] * 100
                    if g >= 1.5: gap_up = True; gap_pct = max(gap_pct, g)
                except Exception:
                    pass
        ok = (news_count >= 2) or gap_up
        detail = f"新聞:{news_count}則 | 跳空{gap_pct:.1f}%:{gap_up} | {news_title[:40]+'...' if news_title else ''}"
        return ok, detail
    except Exception as e:
        return False, f"計算錯誤: {e}"


# ── Main scan ─────────────────────────────────────────────────────────────────

def signal_base_consolidation(hist: pd.DataFrame) -> tuple[bool, str]:
    """
    籌碼整固 (Base Formation / VCP):
    - 近60日價格波幅收窄（ATR縮小）
    - 成交量在整固期間萎縮
    - 股價仍在長期均線以上（未崩壞）
    """
    try:
        close  = hist["Close"]
        high   = hist["High"]
        low    = hist["Low"]
        volume = hist["Volume"]

        # ATR (pure python, no TA-Lib)
        prev_close = close.shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low  - prev_close).abs(),
        ], axis=1).max(axis=1)
        atr14 = tr.ewm(span=14, adjust=False).mean()

        # ATR contraction: recent 20-day ATR vs prior 20-day ATR
        atr_recent = atr14.iloc[-20:].mean()
        atr_prior  = atr14.iloc[-40:-20].mean()
        atr_contracting = atr_recent < atr_prior * 0.85

        # Price range contraction in last 30 days vs prior 30 days
        range_recent = (high.iloc[-30:].max() - low.iloc[-30:].min()) / close.iloc[-30:].mean()
        range_prior  = (high.iloc[-60:-30].max() - low.iloc[-60:-30].min()) / close.iloc[-60:-30].mean()
        range_tightening = range_recent < range_prior * 0.80

        # Volume drying up in consolidation (recent 20d avg < prior 20d avg)
        vol_recent = volume.iloc[-20:].mean()
        vol_prior  = volume.iloc[-40:-20].mean()
        vol_drying = vol_recent < vol_prior * 0.90

        # Price still above 50-day EMA (structure intact)
        ema50 = close.ewm(span=50, adjust=False).mean()
        above_ema50 = close.iloc[-1] > ema50.iloc[-1]

        score = sum([atr_contracting, range_tightening, vol_drying, above_ema50])
        ok = score >= 3

        detail = (f"ATR收窄:{atr_contracting}({atr_recent:.2f}<{atr_prior:.2f}) | "
                  f"價幅收緊:{range_tightening} | "
                  f"量能萎縮:{vol_drying} | "
                  f"EMA50上方:{above_ema50}")
        return ok, detail
    except Exception as e:
        return False, f"計算錯誤: {e}"


def signal_volume_breakout(hist: pd.DataFrame) -> tuple[bool, str]:
    """
    成交量突破 (Volume Breakout):
    - 近5日內出現突破：收盤創近60日新高
    - 突破當日成交量 >= 20日均量 x 1.5
    - 收盤在當日區間上半部（強勢收盤）
    """
    try:
        close  = hist["Close"]
        high   = hist["High"]
        low    = hist["Low"]
        volume = hist["Volume"]

        # Rolling 60-day high (excluding last 5 days as "base")
        base_high = close.iloc[-65:-5].max()

        # Check if any of last 5 days broke out
        breakout_day = None
        for i in range(-5, 0):
            if close.iloc[i] > base_high:
                breakout_day = i
                break

        if breakout_day is None:
            # Check near-breakout: within 1% of 60-day high
            near_break = (close.iloc[-1] - base_high) / base_high * 100
            detail = f"未突破 | 距60日高點: {near_break:+.1f}%"
            return False, detail

        # Volume on breakout day vs 20-day avg (excluding breakout day)
        vol_on_day  = volume.iloc[breakout_day]
        vol_20_avg  = volume.iloc[-25:breakout_day if breakout_day != -1 else None].mean()
        vol_ratio   = vol_on_day / vol_20_avg if vol_20_avg > 0 else 0
        vol_surge   = vol_ratio >= 1.5

        # Strong close: closed in upper half of day's range
        day_range = high.iloc[breakout_day] - low.iloc[breakout_day]
        close_pos = (close.iloc[breakout_day] - low.iloc[breakout_day]) / day_range if day_range > 0 else 0
        strong_close = close_pos >= 0.6

        # Still holding breakout (not collapsed back)
        holding = close.iloc[-1] >= close.iloc[breakout_day] * 0.97

        ok = vol_surge and strong_close
        detail = (f"突破日: {breakout_day}天前 | "
                  f"量比: {vol_ratio:.1f}x | "
                  f"收盤位置: {close_pos*100:.0f}% | "
                  f"守住突破:{holding}")
        return ok, detail
    except Exception as e:
        return False, f"計算錯誤: {e}"


def signal_catalyst(ticker: str) -> tuple[bool, str]:
    """
    催化劑 (Catalyst):
    - 近期有盈利公告、重大新聞（yfinance news）
    - 股價近期出現跳空（gap up >= 1.5%）作為消息面印記
    - 分析師評級變化（用異常價格/成交量作為代理）
    """
    try:
        import time as _time
        tk = yf.Ticker(ticker)

        # News check (7 days)
        news_count = 0
        news_title = ""
        try:
            news = tk.news or []
            recent = [n for n in news if (_time.time() - n.get("providerPublishTime", 0)) < 86400 * 7]
            news_count = len(recent)
            if recent:
                news_title = recent[0].get("title", "")[:50]
        except Exception:
            pass

        # Gap-up detection: any day in last 10 sessions with open > prev close by >= 1.5%
        hist = tk.history(period="30d", interval="1d")
        gap_up = False
        gap_pct = 0.0
        if not hist.empty and len(hist) > 2:
            opens  = hist["Open"]
            closes = hist["Close"]
            for j in range(-10, -1):
                try:
                    g = (opens.iloc[j] - closes.iloc[j-1]) / closes.iloc[j-1] * 100
                    if g >= 1.5:
                        gap_up = True
                        gap_pct = max(gap_pct, g)
                except Exception:
                    pass

        has_news = news_count >= 2
        ok = has_news or gap_up

        detail = (f"7日新聞: {news_count}則 | "
                  f"跳空缺口: {'✓' if gap_up else '✗'}"
                  f"({gap_pct:.1f}%) | "
                  f"{news_title[:40] + '...' if news_title else '無標題'}")
        return ok, detail
    except Exception as e:
        return False, f"計算錯誤: {e}"



def run_scan(
    min_market_cap_b: float,
    use_fundamental: bool,
    use_vol_expansion: bool,
    use_trend_accel: bool,
    use_accumulation: bool,
    use_ma200: bool,
    use_higher_low: bool,
    use_news: bool,
    use_base: bool,
    use_breakout: bool,
    use_catalyst: bool,
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

        if use_fundamental:
            ok, detail = signal_fundamental_shift(ticker, hist)
            signals["fundamental"] = (ok, detail)
            if ok: signal_count += 1

        if use_vol_expansion:
            ok, detail = signal_volume_expansion(hist)
            signals["vol_expansion"] = (ok, detail)
            if ok: signal_count += 1

        if use_trend_accel:
            ok, detail = signal_trend_acceleration(hist)
            signals["trend_accel"] = (ok, detail)
            if ok: signal_count += 1

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

        if use_base:
            ok, detail = signal_base_consolidation(hist)
            signals["base"] = (ok, detail)
            if ok: signal_count += 1

        if use_breakout:
            ok, detail = signal_volume_breakout(hist)
            signals["breakout"] = (ok, detail)
            if ok: signal_count += 1

        if use_catalyst:
            ok, detail = signal_catalyst(ticker)
            signals["catalyst"] = (ok, detail)
            if ok: signal_count += 1

        enabled_count = sum([use_fundamental, use_vol_expansion, use_trend_accel, use_accumulation, use_ma200, use_higher_low, use_news, use_base, use_breakout, use_catalyst])
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
        "fundamental":  ("badge-fundamental",  "① 業績質變"),
        "vol_expansion":("badge-vol-expansion","② 資金狂入"),
        "trend_accel":  ("badge-trend-accel",  "③ 趨勢加速"),
        "accumulation": ("badge-accumulation", "📈 OBV累積"),
        "ma200":        ("badge-ma200",        "〰 測試200MA"),
        "higher_low":   ("badge-higher-low",   "🔺 更高低點"),
        "news":         ("badge-news",          "📰 重大新聞"),
        "base":         ("badge-base",          "📦 籌碼整固"),
        "breakout":     ("badge-breakout",      "💥 量能突破"),
        "catalyst":     ("badge-catalyst",      "💡 催化劑"),
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
            "fundamental":   "① 業績／故事質變",
            "vol_expansion": "② 資金瘋狂流入",
            "trend_accel":   "③ 技術趨勢加速",
            "accumulation":  "📈 OBV累積信號",
            "ma200":         "〰 200MA測試",
            "higher_low":    "🔺 更高低點",
            "news":          "📰 重大新聞",
            "base":          "📦 籌碼整固",
            "breakout":      "💥 成交量突破",
            "catalyst":      "💡 催化劑",
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
      <p>大市值爆升股篩選器 · 市值 $1000億+ · 業績質變 × 資金狂入 × 技術加速</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown('<div class="filter-card"><div class="filter-card-title">⚙ 基本設定</div>', unsafe_allow_html=True)
        min_cap = st.slider("最低市值 (十億美元)", 50, 500, 100, step=50,
                            help="100 = $1000億")
        min_signals = st.slider("最少符合信號數", 1, 10, 2)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="filter-card"><div class="filter-card-title">🔥 爆升三核心條件</div>', unsafe_allow_html=True)
        use_fundamental  = st.checkbox("① 業績／故事質變", value=True,
            help="強於大盤RS + 利空不跌 + 跳空缺口 + 近52週高（市場重新估值）")
        use_vol_expansion= st.checkbox("② 資金瘋狂流入", value=True,
            help="RVOL≥1.5x + OBV持續走高 + 突破日量≥均量2x + 量價齊升")
        use_trend_accel  = st.checkbox("③ 技術趨勢加速", value=True,
            help="EMA多頭排列 + HH+HL + VCP突破 + MACD強勢")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="filter-card"><div class="filter-card-title">➕ 輔助篩選條件</div>', unsafe_allow_html=True)
        use_accumulation = st.checkbox("📈 OBV累積", value=False, help="OBV上升 + 成交量放大 + 價格在EMA50以上")
        use_ma200        = st.checkbox("〰 測試200MA", value=False, help="股價在200MA ±3.5%範圍內")
        use_higher_low   = st.checkbox("🔺 更高低點", value=False, help="近期擺動低點持續走高")
        use_news         = st.checkbox("📰 重大新聞", value=False, help="7日內有2則以上新聞報導")
        use_base         = st.checkbox("📦 籌碼整固", value=False, help="ATR收窄 + 量能萎縮 + 價幅收緊")
        use_breakout     = st.checkbox("💥 量能突破", value=False, help="近5日突破60日高點，當日量≥均量1.5倍")
        use_catalyst     = st.checkbox("💡 催化劑", value=False, help="重大新聞 或 跳空缺口≥1.5%")
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

            enabled_count = sum([use_fundamental, use_vol_expansion, use_trend_accel, use_accumulation, use_ma200, use_higher_low, use_news, use_base, use_breakout, use_catalyst])
            if enabled_count == 0:
                st.warning("請至少選擇一個篩選條件")
                return

            progress_bar = st.progress(0)
            status_text  = st.empty()

            with st.spinner(""):
                results = run_scan(
                    min_market_cap_b=min_cap,
                    use_fundamental=use_fundamental,
                    use_vol_expansion=use_vol_expansion,
                    use_trend_accel=use_trend_accel,
                    use_accumulation=use_accumulation,
                    use_ma200=use_ma200,
                    use_higher_low=use_higher_low,
                    use_news=use_news,
                    use_base=use_base,
                    use_breakout=use_breakout,
                    use_catalyst=use_catalyst,
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
                "use_fundamental": use_fundamental,
                "use_vol_expansion": use_vol_expansion,
                "use_trend_accel": use_trend_accel,
                "use_accumulation": use_accumulation,
                "use_ma200": use_ma200,
                "use_higher_low": use_higher_low,
                "use_news": use_news,
                "use_base": use_base,
                "use_breakout": use_breakout,
                "use_catalyst": use_catalyst,
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
                "①業績質變": r["signals"].get("fundamental",   (False,""))[0],
                "②資金狂入": r["signals"].get("vol_expansion", (False,""))[0],
                "③趨勢加速": r["signals"].get("trend_accel",   (False,""))[0],
                "OBV累積":   r["signals"].get("accumulation",  (False,""))[0],
                "200MA測試": r["signals"].get("ma200",         (False,""))[0],
                "更高低點":  r["signals"].get("higher_low",    (False,""))[0],
                "重大新聞":  r["signals"].get("news",          (False,""))[0],
                "籌碼整固":  r["signals"].get("base",          (False,""))[0],
                "量能突破":  r["signals"].get("breakout",      (False,""))[0],
                "催化劑":    r["signals"].get("catalyst",      (False,""))[0],
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
