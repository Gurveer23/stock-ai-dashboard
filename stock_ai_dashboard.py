import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from tradingview_ta import TA_Handler, Interval
import openai
import os

# --- Set OpenAI key from Render environment variable ---
openai.api_key = os.environ.get("OPENAI_API_KEY")

st.title("Stock & Asset AI Dashboard")

# --- User input ---
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
        # --- Historical chart (30 days placeholder) ---
        dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
        prices = np.linspace(close_price * 0.95, close_price * 1.05, 30)
        df = pd.DataFrame({"Date": dates, "Close": prices})

        st.subheader(f"{symbol} Price Chart (Last 30 Days)")
        fig = px.line(df, x="Date", y="Close", title=f"{symbol} Closing Prices")
        st.plotly_chart(fig)

        # --- AI Analysis ---
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
