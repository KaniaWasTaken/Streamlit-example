import streamlit as st
import pandas as pd
import yfinance as yf

st.write("Hello")
df = yf.download("GOOGL",period="5y",interval="1m")
st.table(df.head())
st.line_chart(df["Close"])
