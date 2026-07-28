import streamlit as st
import pandas as pd
import yfinance as yf

with st.form(key="ticker-form"):
  ticker = st.text_input("Enter ticker")
  btn = st.form_submit_button("Search")

if btn:
  df = yf.download(ticker,period="5y")
  if df.empty:
    st.error("Invalid Ticker")
  else:
    st.table(df.head())
    st.line_chart(df["Close"])
