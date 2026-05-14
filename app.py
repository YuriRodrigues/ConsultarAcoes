import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Ações BR 2026", layout="wide")

TICKERS = {
    "Petrobras (PETR4)": "PETR4.SA",
    "Itaú (ITUB4)":      "ITUB4.SA",
    "Vale (VALE3)":       "VALE3.SA",
}
START_DATE = "2026-01-01"
END_DATE   = date.today().isoformat()


@st.cache_data(ttl=300)
def fetch_data(tickers: list, start: str, end: str) -> pd.DataFrame:
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    return raw["Close"]


st.title("Painel de Ações Brasileiras — 2026")

df = fetch_data(list(TICKERS.values()), START_DATE, END_DATE)

if df.empty:
    st.error("Não foi possível carregar dados. Verifique sua conexão com a internet.")
    st.stop()

# Cards de cotação atual
cols = st.columns(len(TICKERS))
for col, (label, ticker) in zip(cols, TICKERS.items()):
    series = df[ticker].dropna()
    price  = series.iloc[-1]
    prev   = series.iloc[-2] if len(series) > 1 else price
    delta  = price - prev
    col.metric(label=label, value=f"R$ {price:.2f}", delta=f"{delta:+.2f}")

st.divider()

# Gráficos individuais
st.subheader("Evolução do Preço em 2026")
chart_cols = st.columns(len(TICKERS))
for col, (label, ticker) in zip(chart_cols, TICKERS.items()):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[ticker],
        mode="lines",
        name=ticker,
        line=dict(width=2),
    ))
    fig.update_layout(
        title=label,
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        height=350,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    col.plotly_chart(fig, use_container_width=True)

st.divider()

# Gráfico comparativo normalizado
st.subheader("Comparativo de Desempenho (Base 100 em 02/Jan/2026)")
normalized = (df / df.iloc[0]) * 100
fig_all = go.Figure()
for label, ticker in TICKERS.items():
    fig_all.add_trace(go.Scatter(
        x=normalized.index,
        y=normalized[ticker],
        name=label,
        mode="lines",
        line=dict(width=2),
    ))
fig_all.update_layout(
    xaxis_title="Data",
    yaxis_title="Desempenho relativo (base 100)",
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_all, use_container_width=True)

st.caption(f"Dados: Yahoo Finance · Última atualização: {END_DATE} · Cache: 5 min")
