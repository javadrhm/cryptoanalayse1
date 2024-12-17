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

    # Debugging: Print shapes and check for NaN values
    print("Close values shape:", close_values.shape)
    print("High values shape:", high_values.shape)
    print("Low values shape:", low_values.shape)
    print("Volume values shape:", volume_values.shape)

    if np.any(np.isnan(close_values)):
        print("NaN values found in close_values")
    if np.any(np.isnan(high_values)):
        print("NaN values found in high_values")
    if np.any(np.isnan(low_values)):
        print("NaN values found in low_values")
    if np.any(np.isnan(volume_values)):
        print("NaN values found in volume_values")

    # Calculate indicators
    try:
        donchian_channels(df)
        hull_moving_average(df)
        keltner_channel(df)
        aroon_indicator(df)
        anchored_vwap(df)

        ma = talib.SMA(close_values, timeperiod=20)
        ema = talib.EMA(close_values, timeperiod=20)
        macd, macd_signal, _ = talib.MACD(close_values, fastperiod=12, slowperiod=26, signalperiod=9)
        adx = talib.ADX(high_values, low_values, close_values, timeperiod=14)
        atr = talib.ATR(high_values, low_values, close_values, timeperiod=14)
        rsi = talib.RSI(close_values, timeperiod=14 bb_upper, bb_middle, bb_lower = talib.BBANDS(close_values, timeperiod=20, nbdevup=2, nbdevdn=2)
    except Exception as e:
        print("Error in indicator calculation:", e)
        raise

    # Return the analysis results
    analysis = {
        "MA": "Bullish" if close_values[-1] > ma[-1] else "Bearish",
        "EMA": "Bullish" if close_values[-1] > ema[-1] else "Bearish",
        "MACD": "Bullish" if macd[-1] > macd_signal[-1] else "Bearish",
        "ADX": "Strong Trend" if adx[-1] > 25 else "Weak Trend",
        "ATR": "High Volatility" if atr[-1] > np.mean(atr) else "Low Volatility",
        "RSI": "Overbought" if rsi[-1] > 70 else "Oversold" if rsi[-1] < 30 else "Neutral",
        "Bollinger Bands": "Bullish" if close_values[-1] > bb_middle[-1] else "Bearish",
        "Donchian Channels": "Bullish" if close_values[-1] > df["donchian_middle"].iloc[-1] else "Bearish",
        "Hull MA": "Bullish" if close_values[-1] > df["hull_ma"].iloc[-1] else "Bearish",
        "Keltner Channel": "Bullish" if close_values[-1] > df["keltner_upper"].iloc[-1] else "Bearish",
        "Aroon": "Bullish" if df["aroon_up"].iloc[-1] > df["aroon_down"].iloc[-1] else "Bearish",
        "Anchored VWAP": "Bullish" if close_values[-1] > df["anchored_vwap"].iloc[-1] else "Bearish",
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
