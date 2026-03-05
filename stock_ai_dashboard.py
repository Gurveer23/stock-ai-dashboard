import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
from openai import OpenAI

st.set_page_config(page_title="StockAI Dashboard", layout="wide")
st.title("📈 StockAI Dashboard")

# Put your real API key here
client = OpenAI(api_key="OPENAI_API_KEY")

ticker = st.text_input("Enter Stock Ticker (AAPL, TSLA, MSFT):", "AAPL").upper()

if ticker:
    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=180)

        df = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if df.empty:
            st.error("No data found.")
        else:
            df["EMA20"] = df["Close"].ewm(span=20).mean()

            delta = df["Close"].diff().fillna(0)
            up = delta.clip(lower=0).rolling(14).mean()
            down = -delta.clip(upper=0).rolling(14).mean().clip(lower=1e-6)
            df["RSI14"] = (100 - (100 / (1 + (up / down)))).fillna(50)

            df["MACD"] = df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()
            df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()

            latest = df.iloc[-1]

            close_price = float(latest["Close"])
            ema = float(latest["EMA20"])
            rsi = float(latest["RSI14"])
            macd = float(latest["MACD"])
            macd_signal = float(latest["MACD_Signal"])

            signals = []
            signals.append("Bullish" if rsi < 30 else "Bearish" if rsi > 70 else "Neutral")
            signals.append("Bullish" if close_price > ema else "Bearish")
            signals.append("Bullish" if macd > macd_signal else "Bearish")

            bullish = signals.count("Bullish")
            bearish = signals.count("Bearish")

            overall = (
                "BUY 🟢" if bullish >= 2 else
                "SELL 🔴" if bearish >= 2 else
                "HOLD 🟡"
            )

            col1, col2 = st.columns([2.5, 1.5])

            with col1:
                fig = go.Figure()

                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df["Open"],
                    high=df["High"],
                    low=df["Low"],
                    close=df["Close"]
                ))

                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df["EMA20"],
                    mode="lines",
                    name="EMA20"
                ))

                fig.update_layout(
                    xaxis_rangeslider_visible=False,
                    height=500,
                    template="plotly_white"
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.metric("Latest Close", f"${close_price:.2f}")
                st.metric("Signal", overall)

                st.markdown("---")
                st.write(f"RSI: {rsi:.2f}")
                st.write(f"EMA20: {ema:.2f}")
                st.write(f"MACD: {macd:.2f}")
                st.write(f"MACD Signal: {macd_signal:.2f}")

    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")
st.subheader("💬 Ask the Trading AI")

question = st.text_input("Ask about your next move:")

if question:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional trading assistant."},
                {"role": "user", "content": question}
            ]
        )

        answer = response.choices[0].message.content
        st.write(answer)

    except Exception as e:
        st.error(f"AI Error: {e}")
