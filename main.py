import yfinance as yf
import pandas as pd
import numpy as np
import talib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Fetch crypto data from Yahoo Finance
def get_crypto_data(symbol, interval, period="1d"):
    data = yf.download(tickers=symbol, interval=interval, period=period)
    if data.empty:
        raise Exception(f"No data fetched for {symbol} at interval {interval}.")
    return data

# Custom Indicator: Donchian Channels
def donchian_channels(df, period=20):
    df["donchian_upper"] = df["High"].rolling(window=period).max()
    df["donchian_lower"] = df["Low"].rolling(window=period).min()
    df["donchian_middle"] = (df["donchian_upper"] + df["donchian_lower"]) / 2

# Custom Indicator: Hull Moving Average
def hull_moving_average(df, period=20):
    wma_half = talib.WMA(df["Close"].values, timeperiod=int(period / 2))
    wma_full = talib.WMA(df["Close"].values, timeperiod=period)
    hull_ma = talib.WMA(2 * wma_half - wma_full, timeperiod=int(np.sqrt(period)))
    df["hull_ma"] = hull_ma

# Custom Indicator: Keltner Channel
def keltner_channel(df, period=20, multiplier=2):
    atr = talib.ATR(df["High"].values, df["Low"].values, df["Close"].values, timeperiod=period)
    middle = talib.EMA(df["Close"].values, timeperiod=period)
    df["keltner_upper"] = middle + multiplier * atr
    df["keltner_lower"] = middle - multiplier * atr
    df["keltner_middle"] = middle

# Custom Indicator: Aroon
def aroon_indicator(df, period=14):
    aroon_up = ((period - (period - df["High"].rolling(window=period).apply(lambda x: np.argmax(x[::-1]) + 1))) / period) * 100
    aroon_down = ((period - (period - df["Low"].rolling(window=period).apply(lambda x: np.argmin(x[::-1]) + 1))) / period) * 100
    df["aroon_up"] = aroon_up
    df["aroon_down"] = aroon_down

# Custom Indicator: Anchored VWAP
def anchored_vwap(df):
    cum_vol = df["Volume"].cumsum()
    cum_vol_price = (df["Close"] * df["Volume"]).cumsum()
    df["anchored_vwap"] = cum_vol_price / cum_vol

# Analyze market with technical indicators
def analyze_market(df):
    close_values = df["Close"].values
    high_values = df["High"].values
    low_values = df["Low"].values
    volume_values = df["Volume"].values

    ma = talib.SMA(close_values, timeperiod=20)
    ema = talib.EMA(close_values, timeperiod=20)
    macd, macd_signal, _ = talib.MACD(close_values, fastperiod=12, slowperiod=26, signalperiod=9)
    adx = talib.ADX(high_values, low_values, close_values, timeperiod=14)
    atr = talib.ATR(high_values, low_values, close_values, timeperiod=14)
    rsi = talib.RSI(close_values, timeperiod=14)
    bb_upper, bb_middle, bb_lower = talib.BBANDS(close_values, timeperiod=20, nbdevup=2, nbdevdn=2)

    donchian_upper = pd.Series(high_values).rolling(window=20).max()
    donchian_lower = pd.Series(low_values).rolling(window=20).min()
    donchian_middle = (donchian_upper + donchian_lower) / 2

    wma_half = talib.WMA(close_values, timeperiod=10)
    wma_full = talib.WMA(close_values, timeperiod=20)
    hull_ma = talib.WMA(2 * wma_half - wma_full, timeperiod=int(np.sqrt(20)))

    atr_values = talib.ATR(high_values, low_values, close_values, timeperiod=20)
    middle = talib.EMA(close_values, timeperiod=20)
    keltner_upper = middle + 2 * atr_values
    keltner_lower = middle - 2 * atr_values
    keltner_middle = middle

    aroon_up = ((20 - (20 - pd.Series(high_values).rolling(window=20).apply(lambda x: np.argmax(x[::-1]) + 1))) / 20) * 100
    aroon_down = ((20 - (20 - pd.Series(low_values).rolling(window=20).apply(lambda x: np.argmin(x[::-1]) + 1))) / 20) * 100

    cum_vol = np.cumsum(volume_values)
    cum_vol_price = np.cumsum(close_values * volume_values)
    anchored_vwap = cum_vol_price / cum_vol

    latest_close = close_values[-1]
    latest_ma = ma[-1]
    latest_ema = ema[-1]
    latest_macd = macd[-1]
    latest_macd_signal = macd_signal[-1]
    latest_adx = adx[-1]
    latest_atr = atr[-1]
    latest_rsi = rsi[-1]
    latest_bb_middle = bb_middle[-1]
    latest_donchian_middle = donchian_middle.iloc[-1]
    latest_hull_ma = hull_ma[-1]
    latest_keltner_middle = keltner_middle[-1]
    latest_aroon_up = aroon_up.iloc[-1]
    latest_aroon_down = aroon_down.iloc[-1]
    latest_anchored_vwap = anchored_vwap[-1]

    analysis = {
        "MA": "Bullish" if latest_close > latest_ma else "Bearish",
        "EMA": "Bullish" if latest_close > latest_ema else "Bearish",
        "MACD": "Bullish" if latest_macd > latest_macd_signal else "Bearish",
        "ADX": "Strong Trend" if latest_adx > 25 else "Weak Trend",
        "ATR": "High Volatility" if latest_atr > np.mean(atr) else "Low Volatility",
        "RSI": "Overbought" if latest_rsi > 70 else "Oversold" if latest_rsi < 30 else "Neutral",
        "Bollinger Bands": "Bullish" if latest_close > latest_bb_middle else "Bearish",
        "Donchian Channels": "Bullish" if latest_close > latest_donchian_middle else "Bearish",
        "Hull MA": "Bullish" if latest_close > latest_hull_ma else "Bearish",
        "Keltner Channel": "Bullish" if latest_close > latest_keltner_middle else "Bearish",
        "Aroon": "Bullish" if latest_aroon_up > latest_aroon_down else "Bearish",
        "Anchored VWAP": "Bullish" if latest_close > latest_anchored_vwap else "Bearish",
    }
    return analysis

class AnalysisRequest(BaseModel):
    symbol: str
    interval: str

@app.post("/analyze/")
async def analyze(request: AnalysisRequest):
    try:
        data = get_crypto_data(request.symbol, request.interval)
        analysis = analyze_market(data)
        return {"symbol": request.symbol, "interval": request.interval, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Crypto Analysis API. Use /analyze/ to get market analysis."}
