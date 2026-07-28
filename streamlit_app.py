import streamlit as st
import pandas as pd
import yfinance as yf

with st.form:
  ticker = st.text_input("Enter ticker")

  btn = st.form_sumit_button()

st.write("Hello")
df = yf.download("GOOGL",period="5y")
st.table(df.head())
st.line_chart(df["Close"])
