# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Dashboard Streamlit de cotações de ações brasileiras (B3) para o ano de 2026. Exibe cards de preço com delta diário, gráficos individuais de evolução de preço e um gráfico comparativo normalizado (base 100 em 02/Jan/2026) para PETR4, ITUB4 e VALE3.

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

`START_DATE` is hardcoded to `"2026-01-01"` in `app.py`; `END_DATE` is always `date.today()`.

## UI features

- **Cards de cotação** — preço atual (R$) com delta em relação ao pregão anterior, um card por ativo.
- **Gráficos individuais** — evolução de preço em R$ para cada ativo, lado a lado.
- **Gráfico comparativo** — desempenho relativo normalizado (base 100) de todos os ativos no mesmo eixo.

## Adding or changing tickers

Edit the `TICKERS` dict in `app.py`. Keys are display labels, values are Yahoo Finance symbols. Brazilian B3 stocks use the `.SA` suffix (e.g. `VALE3.SA`).

## Auto-commit watcher (`watch.py`)

`watch.py` monitors changes to `.py`, `.txt`, and `.md` files (ignoring `.venv`, `.git`, `__pycache__`) and automatically commits and pushes after a 2-second debounce. Commit messages follow the format `"auto: {filename}"`.

To use it:

```bash
pip install watchdog   # not included in requirements.txt
source .venv/bin/activate
python watch.py
```

## Dependencies

Managed via `.venv/`. To reinstall:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`watch.py` additionally requires `watchdog`, which is not listed in `requirements.txt`.
