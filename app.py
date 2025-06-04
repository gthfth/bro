import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

st.set_page_config(page_title="🚀 S&P500 Research Terminal", layout="wide")
st.title("🚀 S&P 500 Quant Explorer Terminal")

# --- SIDEBAR: Data Source ---
with st.sidebar:
    st.header("📂 Data Source")
    data_type = st.radio("Choose Data Type", ["CSV upload", "SP500 JSON folder"])
    fee = st.number_input("Trade Fee (%)", min_value=0.0, max_value=1.0, value=0.0005)

    st.markdown("---")    
    st.header("🔬 Strategy Params")
    fast_ma = st.slider("Fast MA Days", 3, 50, 10)
    slow_ma = st.slider("Slow MA Days", 10, 200, 50)

# --- Main Data Load ---
symbol = None
df = None

if data_type == "CSV upload":
    uploaded = st.sidebar.file_uploader("Upload a CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded, parse_dates=["date"])
        symbol = uploaded.name.replace(".csv", "")
    else:
        st.info("Upload a CSV file with 'date','close',... columns")
        st.stop()
else:
    sp500_folder = os.path.join(os.getcwd(), "sp500")
    if not os.path.isdir(sp500_folder):
        st.error("No 'sp500' folder found in your project!")
        st.stop()
    json_files = [f for f in os.listdir(sp500_folder) if f.endswith(".json")]
    if not json_files:
        st.error("No JSON files found inside 'sp500/' folder.")
        st.stop()
    chosen = st.sidebar.selectbox("Pick a JSON file", json_files)
    st.write(f"**Loaded:** `{chosen}` from `sp500/`")
    with open(os.path.join(sp500_folder, chosen)) as f:
        data = json.load(f)
    result = data['chart']['result'][0]
    timestamps = result['timestamp']
    quote = result['indicators']['quote'][0]
    df = pd.DataFrame({
        "date": [datetime.fromtimestamp(ts) for ts in timestamps],
        "open": quote.get("open"),
        "high": quote.get("high"),
        "low": quote.get("low"),
        "close": quote.get("close"),
        "volume": quote.get("volume")
    })
    symbol = chosen.replace(".json", "")

# --- Quick Data Check ---
st.subheader(f"💡 Data Preview: `{symbol}`")
st.dataframe(df.head(), hide_index=True, use_container_width=True)

if 'close' not in df.columns:
    st.error("No 'close' column found. Check your data format.")
    st.stop()

# --- Strategy Logic ---
df["fast_ma"] = df["close"].rolling(fast_ma).mean()
df["slow_ma"] = df["close"].rolling(slow_ma).mean()
buy_signal = (df["fast_ma"] > df["slow_ma"]) & (df["fast_ma"].shift(1) <= df["slow_ma"].shift(1))
sell_signal = (df["fast_ma"] < df["slow_ma"]) & (df["fast_ma"].shift(1) >= df["slow_ma"].shift(1))
df["signal"] = np.nan
df.loc[buy_signal, "signal"] = 1
df.loc[sell_signal, "signal"] = -1
df["signal"] = df["signal"].ffill().fillna(0)
df["position"] = df["signal"].shift().fillna(0)
df["returns"] = df["close"].pct_change().fillna(0)
df["strategy_returns"] = df["position"] * df["returns"]

# Deduct trade fee on signal change
df["trade"] = df["signal"].diff().abs().fillna(0)
df["strategy_returns_net"] = df["strategy_returns"] - df["trade"] * fee

# Cumulative curves
df["cum_market"] = (1 + df["returns"]).cumprod()
df["cum_strategy"] = (1 + df["strategy_returns_net"]).cumprod()

# --- Dashboard Layout ---
tab1, tab2 = st.tabs(["📊 Charts", "🧾 Recent Trades & Performance"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Price & Moving Averages")
        chart_ma = df.set_index("date")[["close", "fast_ma", "slow_ma"]]
        st.line_chart(chart_ma, use_container_width=True)
    with c2:
        st.markdown("#### Cumulative Returns")
        chart_cum = df.set_index("date")[["cum_market", "cum_strategy"]]
        st.line_chart(chart_cum, use_container_width=True)

with tab2:
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### 📝 Performance Metrics")
        final_strat = df["cum_strategy"].iloc[-1]
        final_market = df["cum_market"].iloc[-1]
        sharpe = (
            df["strategy_returns_net"].mean() / df["strategy_returns_net"].std() * np.sqrt(252)
            if df["strategy_returns_net"].std() != 0 else float('nan')
        )
        # Max drawdown
        running_max = df["cum_strategy"].cummax()
        drawdown = ((df["cum_strategy"] / running_max).min() - 1) if not running_max.isnull().all() else None

        st.metric("Strategy Total Return (%)", f"{100 * (final_strat-1):.2f}")
        st.metric("Market Total Return (%)", f"{100 * (final_market-1):.2f}")
        st.metric("Sharpe Ratio", f"{sharpe:.2f}")
        st.metric("Max Drawdown (%)", f"{100 * drawdown:.2f}" if drawdown is not None else "N/A")
    with c4:
        st.markdown("#### 🗒️ Recent Trades Blotter")
        trade_blotter = df[df['signal'].diff() != 0][["date", "signal", "close"]]
        trade_blotter['Trade'] = trade_blotter['signal'].map({1: "BUY", -1: "SELL", 0: "HOLD"})
        st.dataframe(trade_blotter[["date", "Trade", "close"]].tail(10), hide_index=True)

# --- Raw Data Expand ---
with st.expander("Show Raw Simulation Data Table"):
    st.dataframe(df, use_container_width=True)

st.caption("💡 Place more JSON files into `sp500/` (at the same level as `app.py`), or upload a CSV file to analyze other assets. Happy researching!")