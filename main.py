from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
import talib

app = Flask(__name__)

def get_crypto_data(symbol, interval, period="max"):
    try:
        data = yf.download(tickers=symbol, interval=interval, period='max')
        if data.empty:
            raise ValueError(f"No data fetched for {symbol} at interval {interval}.")
        
        # Flatten MultiIndex columns
        data.columns = [col[0] for col in data.columns]
        return data
    except Exception as e:
        raise RuntimeError(f"Failed to fetch data: {e}")

def analyze_market(df):
    try:
        # Drop rows with missing data
        df = df.dropna()
        if df.empty:
            raise ValueError("Data contains only NaN values after cleaning.")

        # Extract relevant columns
        close_values = df["Close"].values
        high_values = df["High"].values
        low_values = df["Low"].values
        volume_values = df["Volume"].values

        if len(close_values) < 20:
            raise ValueError("Not enough data points to calculate indicators. Try a longer period.")

        # Indicators
        ma = talib.SMA(close_values, timeperiod=20)
        ema = talib.EMA(close_values, timeperiod=20)
        macd, macd_signal, _ = talib.MACD(close_values, fastperiod=12, slowperiod=26, signalperiod=9)
        adx = talib.ADX(high_values, low_values, close_values, timeperiod=14)
        atr = talib.ATR(high_values, low_values, close_values, timeperiod=14)
        rsi = talib.RSI(close_values, timeperiod=14)
        bb_upper, bb_middle, bb_lower = talib.BBANDS(close_values, timeperiod=20, nbdevup=2, nbdevdn=2)

        donchian_upper = pd.Series(high_values).rolling(window=20).max().values
        donchian_lower = pd.Series(low_values).rolling(window=20).min().values
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

        # Latest values
        latest_close = close_values[-1]
        latest_ma = ma[-1] if len(ma) > 0 else None
        latest_ema = ema[-1] if len(ema) > 0 else None
        latest_macd = macd[-1] if len(macd) > 0 else None
        latest_macd_signal = macd_signal[-1] if len(macd_signal) > 0 else None
        latest_adx = adx[-1] if len(adx) > 0 else None
        latest_atr = atr[-1] if len(atr) > 0 else None
        latest_rsi = rsi[-1] if len(rsi) > 0 else None
        latest_bb_middle = bb_middle[-1] if len(bb_middle) > 0 else None
        latest_donchian_middle = donchian_middle[-1] if len(donchian_middle) > 0 else None
        latest_hull_ma = hull_ma[-1] if len(hull_ma) > 0 else None
        latest_keltner_middle = keltner_middle[-1] if len(keltner_middle) > 0 else None
        latest_aroon_up = aroon_up.iloc[-1] if len(aroon_up) > 0 else None
        latest_aroon_down = aroon_down.iloc[-1] if len(aroon_down) > 0 else None
        latest_anchored_vwap = anchored_vwap[-1] if len(anchored_vwap) > 0 else None

        analysis = {
            "MA": "Bullish" if latest_close > latest_ma else "Bearish" if latest_ma is not None else "N/A",
            "EMA": "Bullish" if latest_close > latest_ema else "Bearish" if latest_ema is not None else "N/A",
            "MACD": "Bullish" if latest_macd > latest_macd_signal else "Bearish" if latest_macd is not None else "N/A",
            "ADX": "Strong Trend" if latest_adx > 25 else "Weak Trend" if latest_adx is not None else "N/A",
            "ATR": "High Volatility" if latest_atr > np.mean(atr) else "Low Volatility" if latest_atr is not None else "N/A",
            "RSI": "Overbought" if latest_rsi > 70 else "Oversold" if latest_rsi < 30 else "Neutral" if latest_rsi is not None else "N/A",
            "Bollinger Bands": "Bullish" if latest_close > latest_bb_middle else "Bearish" if latest_bb_middle is not None else "N/A",
            "Donchian Channels": "Bullish" if latest_close > latest_donchian_middle else "Bearish" if latest_donchian_middle is not None else "N/A",
            "Hull MA": "Bullish" if latest_close > latest_hull_ma else "Bearish" if latest_hull_ma is not None else "N/A",
            "Keltner Channel": "Bullish" if latest_close > latest_keltner_middle else "Bearish" if latest_keltner_middle is not None else "N/A",
            "Aroon": "Bullish" if latest_aroon_up > latest_aroon_down else "Bearish" if latest_aroon_up is not None else "N/A",
            "Anchored VWAP": "Bullish" if latest_close > latest_anchored_vwap else "Bearish" if latest_anchored_vwap is not None else "N/A",
        }
        return analysis

    except Exception as e:
        raise RuntimeError(f"Failed to analyze market data: {e}")

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        symbol = data.get('symbol')
        interval = data.get('interval')
        period = data.get('period', '1d')

        if not symbol or not interval:
            return jsonify({"error": "Symbol and interval are required fields"}), 400

        crypto_data = get_crypto_data(symbol, interval, period)
        analysis = analyze_market(crypto_data)
        return jsonify({"symbol": symbol, "interval": interval, "analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,port=8000)
