import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

st.set_page_config(page_title="Stock Price Predictor", layout="wide")

st.title("📈 Tomorrow's Stock Price Prediction")

with st.form("stock-form"):
    ticker = st.text_input(
        "Enter Stock Ticker",
        placeholder="Example: RELIANCE.NS or AAPL"
    ).upper().strip()

    submit = st.form_submit_button("Predict")

if submit:

    if ticker == "":
        st.warning("Please enter a ticker.")
        st.stop()

    df = yf.download(
        ticker,
        period="5y",
        auto_adjust=True,
        progress=False,
    )

    if df.empty:
        st.error("Invalid ticker or no data available.")
        st.stop()

    # ----------------------------
    # Feature Engineering
    # ----------------------------
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()

    df["Return"] = df["Close"].pct_change()

    df["High_Low"] = df["High"] - df["Low"]
    df["Open_Close"] = df["Open"] - df["Close"]

    # Target = Tomorrow's Close
    df["Target"] = df["Close"].shift(-1)

    df.dropna(inplace=True)

    features = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "MA5",
        "MA20",
        "Return",
        "High_Low",
        "Open_Close",
    ]

    X = df[features]
    y = df["Target"]

    # Train/Test Split (Chronological)
    split = int(len(df) * 0.8)

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]

    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    # ----------------------------
    # Linear Regression
    # ----------------------------
    model = LinearRegression()

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    # ----------------------------
    # Evaluation
    # ----------------------------
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    # Tomorrow Prediction
    latest = X.iloc[[-1]]

    tomorrow_price = model.predict(latest)[0]

    st.subheader("Prediction")

    st.metric(
        "Predicted Tomorrow Close",
        f"${tomorrow_price:.2f}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("MAE", f"${mae:.2f}")

    with col2:
        st.metric("RMSE", f"${rmse:.2f}")

    with col3:
        st.metric("R² Score", f"{r2:.3f}")

    st.divider()

    st.subheader("Historical Closing Price")

    st.line_chart(df["Close"])

    st.subheader("Actual vs Predicted")

    result = pd.DataFrame({
        "Actual": y_test,
        "Predicted": predictions,
    })

    st.line_chart(result)

    st.subheader("Recent Data")

    st.dataframe(df.tail())
