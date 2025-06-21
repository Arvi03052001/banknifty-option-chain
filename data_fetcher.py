# data_fetcher.py

from token_manager import get_fyers_client
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_profile():
    fyers = get_fyers_client()
    return fyers.get_profile()

def get_market_data(symbol):
    fyers = get_fyers_client()
    data = {
        "symbols": symbol
    }
    return fyers.quotes(data)

def calculate_vwap(symbol, timeframe="15", source="close", days_back=5, heikin_ashi=False, anchor="session"):
    """
    Calculate VWAP for a given symbol on specified timeframe
    
    Args:
        symbol (str): Trading symbol (e.g., "NSE:BANKNIFTY25JUNFUT")
        timeframe (str): Candle timeframe in minutes (default: "15")
        source (str): Price source for VWAP calculation (default: "close")
        days_back (int): Number of days to look back (default: 5)
        heikin_ashi (bool): Whether to use Heikin Ashi candles (default: False)
        anchor (str): Anchor period for VWAP calculation (default: "session")
        
    Returns:
        float: VWAP value
    """
    try:
        fyers = get_fyers_client()
        
        # Calculate date range - use more days to ensure we have data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Format dates for API
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        # Prepare data request
        data = {
            "symbol": symbol,
            "resolution": timeframe,
            "date_format": "1",
            "range_from": from_date,
            "range_to": to_date,
            "cont_flag": "1"
        }
        
        print(f"[DEBUG] Fetching historical data for {'Heikin Ashi' if heikin_ashi else 'Standard'} VWAP calculation: {data}")
        
        # Get historical data
        response = fyers.history(data)
        
        if response.get("s") != "ok" or not response.get("candles"):
            print(f"[ERROR] Failed to get historical data: {response}")
            return 0
        
        # Convert to DataFrame
        candles = response["candles"]
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        
        if df.empty:
            print("[ERROR] No candle data found")
            return 0
        
        # Convert timestamps to datetime
        df["datetime"] = pd.to_datetime(df["timestamp"], unit='s')
        
        # Process based on anchor period
        if anchor.lower() == "session":
            # Group by trading day
            df['date'] = df['datetime'].dt.date
            
            # Get the most recent date in the data
            most_recent_date = df['date'].max()
            
            # Filter to just the most recent day's data
            df = df[df['date'] == most_recent_date]
            
            print(f"[DEBUG] Using session anchor with most recent date: {most_recent_date}")
        elif anchor.lower() == "week":
            # Get data for the current week
            df['week'] = df['datetime'].dt.isocalendar().week
            current_week = end_date.isocalendar()[1]
            df = df[df['week'] == current_week]
            
            print(f"[DEBUG] Using week anchor for week number: {current_week}")
        
        # If we filtered out all data, return 0
        if df.empty:
            print("[ERROR] No data found after applying anchor filter")
            return 0
        
        # Convert to Heikin Ashi if requested
        if heikin_ashi:
            df = convert_to_heikin_ashi(df)
            print("[DEBUG] Converted to Heikin Ashi candles")
        
        # Calculate VWAP
        # Get price based on selected source
        if source.lower() == "close":
            price = df["close"]
        elif source.lower() == "open":
            price = df["open"]
        elif source.lower() == "high":
            price = df["high"]
        elif source.lower() == "low":
            price = df["low"]
        elif source.lower() == "hl2":
            price = (df["high"] + df["low"]) / 2
        elif source.lower() == "hlc3":
            price = (df["high"] + df["low"] + df["close"]) / 3
        elif source.lower() == "ohlc4":
            price = (df["open"] + df["high"] + df["low"] + df["close"]) / 4
        else:
            price = df["close"]  # Default to close
        
        # Calculate VWAP
        df["pv"] = price * df["volume"]
        df["cumulative_pv"] = df["pv"].cumsum()
        df["cumulative_volume"] = df["volume"].cumsum()
        df["vwap"] = df["cumulative_pv"] / df["cumulative_volume"]
        
        # Get the latest VWAP value
        latest_vwap = df["vwap"].iloc[-1] if not df.empty else 0
        
        print(f"[DEBUG] Calculated {'Heikin Ashi' if heikin_ashi else 'Standard'} VWAP: {latest_vwap}")
        print(f"[DEBUG] Using candles from {df['datetime'].min()} to {df['datetime'].max()}")
        
        return latest_vwap
    
    except Exception as e:
        print(f"[ERROR] VWAP calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return 0

def convert_to_heikin_ashi(df):
    """
    Convert a DataFrame of OHLCV candles to Heikin Ashi candles.
    Expects columns: ['open', 'high', 'low', 'close', 'volume']
    """
    ha_df = df.copy()
    ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_open = [df['open'].iloc[0]]
    for i in range(1, len(df)):
        ha_open.append((ha_open[i-1] + ha_close.iloc[i-1]) / 2)
    ha_open = pd.Series(ha_open, index=df.index)
    ha_high = pd.concat([df['high'], ha_open, ha_close], axis=1).max(axis=1)
    ha_low = pd.concat([df['low'], ha_open, ha_close], axis=1).min(axis=1)
    ha_df['open'] = ha_open
    ha_df['close'] = ha_close
    ha_df['high'] = ha_high
    ha_df['low'] = ha_low
    return ha_df

def get_banknifty_vwap():
    """Get standard VWAP for BankNifty futures with 15-min timeframe using close price and session anchor"""
    symbol = "NSE:BANKNIFTY25JUNFUT"  # Current month BankNifty futures
    return calculate_vwap(symbol, timeframe="15", source="close", anchor="session")

def get_banknifty_heikin_ashi_vwap():
    """Get Heikin Ashi VWAP for BankNifty futures with 15-min timeframe using close price and session anchor"""
    symbol = "NSE:BANKNIFTY25JUNFUT"  # Current month BankNifty futures
    return calculate_vwap(symbol, timeframe="15", source="close", heikin_ashi=True, anchor="session")

def rma(series, length):
    """Wilder's RMA (smoothed moving average) for ATR calculation."""
    result = [np.nan] * len(series)
    if len(series) < length:
        return pd.Series(result, index=series.index)
    # First value is SMA
    sma = series.iloc[:length].mean()
    result[length-1] = sma
    alpha = 1 / length
    for i in range(length, len(series)):
        result[i] = (series.iloc[i] * alpha) + (result[i-1] * (1 - alpha))
    return pd.Series(result, index=series.index)

def calculate_atr(symbol, length=9, timeframe="15", days_back=5):
    """
    Calculate ATR (Average True Range) for a given symbol and length using RMA.
    Args:
        symbol (str): Trading symbol (e.g., "NSE:BANKNIFTY25JUN57000CE")
        length (int): ATR period length (default: 9)
        timeframe (str): Candle timeframe in minutes (default: "15")
        days_back (int): Number of days to look back (default: 5)
    Returns:
        float: Latest ATR value
    """
    try:
        fyers = get_fyers_client()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        data = {
            "symbol": symbol,
            "resolution": timeframe,
            "date_format": "1",
            "range_from": from_date,
            "range_to": to_date,
            "cont_flag": "1"
        }
        response = fyers.history(data)
        if response.get("s") != "ok" or not response.get("candles"):
            print(f"[ERROR] Failed to get historical data for ATR: {response}")
            return 0
        candles = response["candles"]
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        if df.empty or len(df) < length:
            print("[ERROR] Not enough candle data for ATR calculation")
            return 0
        # Calculate True Range
        df['prev_close'] = df['close'].shift(1)
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['prev_close'])
        df['tr3'] = abs(df['low'] - df['prev_close'])
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        # Calculate ATR using RMA
        df['atr'] = rma(df['tr'], length)
        latest_atr = df['atr'].iloc[-1] if not df['atr'].isna().all() else 0
        return latest_atr
    except Exception as e:
        print(f"[ERROR] ATR calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return 0