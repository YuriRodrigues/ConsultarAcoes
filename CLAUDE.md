# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
source .venv/bin/activate
streamlit run app.py
# Opens at http://localhost:8501
```

To stop: `pkill -f "streamlit run"`

## Architecture

Single-file Streamlit app (`app.py`). Streamlit reruns the entire script top-to-bottom on every user interaction, so `@st.cache_data(ttl=300)` on `fetch_data` is critical — without it, every interaction triggers a Yahoo Finance HTTP request.

Data flow: `yfinance.download()` → pandas DataFrame (dates × tickers) → `st.metric()` cards + `plotly.graph_objects` charts rendered via `st.plotly_chart()`.

## Adding or changing tickers

Edit the `TICKERS` dict in `app.py`. Keys are display labels, values are Yahoo Finance symbols. Brazilian B3 stocks use the `.SA` suffix (e.g. `VALE3.SA`).

## Dependencies

Managed via `.venv/`. To reinstall:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
