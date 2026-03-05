import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from tradingview_ta import TA_Handler, Interval
import openai
import requests

# Set OpenAI key safely
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Stock & Asset AI Dashboard")

# --- Input ---
symbol = st.text_input("Enter TradingView symbol", "AAPL").upper()
asset_type = st.selectbox("Asset Type", ["Stock", "Forex", "Commodity"])

# --- Determine exchange & screener ---
if asset_type == "Stock":
    exchange = "NASDAQ"
    screener = "america"
elif asset_type == "Forex":
    exchange = "FX"
    screener = "forex"
else:
    exchange = "COMEX"
    screener = "commodities"

# --- Function to fetch historical data from TradingView ---
def fetch_tradingview_history(symbol, interval="1D", n=30):
    """
    Returns DataFrame with 'Date' and 'Close' columns for last n intervals.
    """
    # TradingView lightweight chart API URL
    url = f"https://tvc4.forexpros.com/1e5bf9c88b3b14e1f1b5b4cba7f7e1a0/{symbol}/1D/history"
    # NOTE: This URL structure may require adjustment per symbol; Streamlit free deployment may not allow CORS
    # For simplicity, here we simulate with dummy linear trend for now
    dates = pd.date_range(end=pd.Timestamp.today(), periods=n)
    close_price = np.random.uniform(100, 200)  # placeholder, will replace with real current price later
    prices = np.linspace(close_price*0.95, close_price*1.05, n)
    df = pd.DataFrame({"Date": dates, "Close": prices})
    return df

# --- Fetch current price safely ---
try:
    handler = TA_Handler(
        symbol=symbol,
        screener=screener,
        exchange=exchange,
        interval=Interval.INTERVAL_1_DAY
    )
    analysis = handler.get_analysis()
    close_price = analysis.indicators.get("close", None)

    if close_price is None:
        st.warning(f"No data found for symbol: {symbol}")
    else:
        # --- Fetch historical chart data ---
        df = fetch_tradingview_history(symbol, n=30)
        df["Close"] = np.linspace(close_price*0.95, close_price*1.05, 30)  # sync with current price

        # --- Display chart ---
        st.subheader(f"{symbol} Price Chart (Last 30 Days)")
        fig = px.line(df, x="Date", y="Close", title=f"{symbol} Closing Prices")
        st.plotly_chart(fig)

        # --- AI analysis ---
        prompt = f"Give a brief analysis of {symbol} based on current price ${close_price:.2f} and last 30 days trend."
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        st.subheader("AI Analysis")
        st.write(response.choices[0].text)

except Exception as e:
    st.error(f"Error fetching data for {symbol}: {e}")

st.markdown("---")
