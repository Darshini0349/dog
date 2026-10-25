

"""
Project 2 (APIs): Stock Market Dashboard
Fetches recent stock price history, prints summary stats, and saves a
price chart as a PNG.

REAL API: uses Stooq's free CSV endpoint (stooq.com) which needs no API key.
Production-correct code. If the network is blocked, it falls back to
generated sample prices (clearly labelled) so the chart + stats still render.

Run: pip install requests pandas matplotlib
     python 02_stock_market_dashboard.py AAPL

Concepts practiced: fetching + parsing CSV from an API into pandas,
computing rolling stats (moving average, daily returns, volatility),
saving a matplotlib chart to a file, offline fallback.
"""

import sys
import io
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend, for saving files
import matplotlib.pyplot as plt


def fetch_prices(ticker):
    # Stooq serves daily CSV; US tickers use the ".us" suffix.
    url = f"https://stooq.com/q/d/l/?s={ticker.lower()}.us&i=d"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text))
    if df.empty or "Close" not in df.columns:
        return None
    df["Date"] = pd.to_datetime(df["Date"])
    return df.tail(60).reset_index(drop=True)


def sample_prices(ticker, seed=42):
    """Clearly-labelled offline fallback: a synthetic random-walk price series."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=60)
    start = 150
    returns = rng.normal(0.0005, 0.02, 60)
    prices = start * np.cumprod(1 + returns)
    return pd.DataFrame({"Date": dates, "Close": prices})


def analyze(df):
    df = df.copy()
    df["MA7"] = df["Close"].rolling(7).mean()
    df["daily_return"] = df["Close"].pct_change()
    latest = df["Close"].iloc[-1]
    change = df["Close"].iloc[-1] - df["Close"].iloc[-2]
    pct_change = (change / df["Close"].iloc[-2]) * 100
    volatility = df["daily_return"].std() * 100
    return df, latest, change, pct_change, volatility


def save_chart(df, ticker, path):
    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Close"], label="Close", linewidth=1.5)
    plt.plot(df["Date"], df["MA7"], label="7-day MA", linewidth=1.5, linestyle="--")
    plt.title(f"{ticker.upper()} — Last {len(df)} Trading Days")
    plt.xlabel("Date"); plt.ylabel("Price")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(path, dpi=100)
    plt.close()


def main():
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    print(f"=== Stock Market Dashboard: {ticker.upper()} ===")

    try:
        df = fetch_prices(ticker)
        if df is None:
            print(f"No data for ticker '{ticker}'.")
            return
        source = "LIVE (Stooq)"
    except requests.exceptions.RequestException as e:
        print(f"[Network unavailable: {type(e).__name__}] Using SAMPLE data.")
        df = sample_prices(ticker)
        source = "SAMPLE (offline fallback)"

    df, latest, change, pct, vol = analyze(df)

    print(f"\nData source: {source}")
    print(f"Latest close:      {latest:.2f}")
    print(f"Change vs prev day: {change:+.2f} ({pct:+.2f}%)")
    print(f"60-day high/low:   {df['Close'].max():.2f} / {df['Close'].min():.2f}")
    print(f"Daily volatility:  {vol:.2f}%")

    chart_path = f"{ticker.lower()}_chart.png"
    save_chart(df, ticker, chart_path)
    print(f"\nChart saved: {chart_path}")


if __name__ == "__main__":
    main()