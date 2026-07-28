import streamlit as st
import yfinance as yf
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

st.title("📈 Stock Price Predictor")

with st.form("stock_form"):
    ticker = st.text_input("Ticker", "AAPL").upper().strip()
    submit = st.form_submit_button("Predict")

if submit:

    df = yf.download(
        ticker,
        period="5y",
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        st.error("Invalid ticker.")
        st.stop()

    # -----------------------
    # Feature Engineering
    # -----------------------
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()

    df["Return"] = df["Close"].pct_change()

    df["High_Low"] = df["High"] - df["Low"]
    df["Open_Close"] = df["Open"] - df["Close"]

    # Tomorrow's close
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

    # Preserve chronological order
    split = int(len(df) * 0.8)

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]

    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)

    # Tomorrow prediction
    latest_features = X.iloc[[-1]]

    tomorrow_prediction = model.predict(latest_features)[0]

    st.subheader("Prediction")

    st.metric(
        "Predicted Tomorrow Close",
        f"${tomorrow_prediction:.2f}"
    )

    st.metric(
        "Mean Absolute Error",
        f"${mae:.2f}"
    )

    st.subheader("Historical Closing Price")
    st.line_chart(df["Close"])

    result = pd.DataFrame({
        "Actual": y_test,
        "Predicted": predictions
    })

    st.subheader("Actual vs Predicted")
    st.line_chart(result)

    st.subheader("Latest Data")
    st.dataframe(df.tail())
