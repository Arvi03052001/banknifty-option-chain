from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from option_chain_fetcher import run_option_chain, get_spot_price, get_futures_price, get_fyers_client, get_expiry_dates
from data_fetcher import get_banknifty_vwap, get_banknifty_heikin_ashi_vwap, calculate_vwap, calculate_atr
from futures_config import get_current_futures_symbol, get_next_futures_symbol, get_futures_info
from timezone_utils import get_ist_now, get_ist_time_string, get_ist_date, IST
from datetime import datetime, time
from option_chain_history_view import history_bp
# Import utility functions
from option_chain_utils import find_closest_strike, add_color_classes, calculate_color_intensity, format_number
import os

app = Flask(__name__)
# Add ProxyFix middleware to handle ngrok requests
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
app.register_blueprint(history_bp)


def get_option_ltp_data():
    """Fetch LTP data for options"""
    try:
        fyers = get_fyers_client()
        expiry_dates = get_expiry_dates()
        
        if len(expiry_dates) < 2:
            print("[ERROR] Less than 2 expiry dates available.")
            return [], []        # Get option chain data with LTP
        exp1 = expiry_dates[0]
        exp2 = expiry_dates[1]
        
        # Fetch option data for both expiries (needed for home page)
        data1 = get_option_data_with_ltp(exp1["expiry"])
        data2 = get_option_data_with_ltp(exp2["expiry"])
        
        # For OI-LTP page, only use current month data
        combined_data = data1  # Only use first expiry data for OI-LTP page
        
        # Process the data to combine strikes
        strike_data = {}
        for option in combined_data:
            strike = option.get("strike_price")
            option_type = option.get("option_type")
            ltp = option.get("ltp", 0)
            volume = option.get("volume", 0)
            
            if strike not in strike_data:
                strike_data[strike] = {
                    "strike": strike,
                    "call_ltp": 0,
                    "put_ltp": 0,
                    "call_volume": 0,
                    "put_volume": 0,
                    "total_volume": 0
                }
            
            if option_type == "CE":
                strike_data[strike]["call_ltp"] = ltp
                strike_data[strike]["call_volume"] = volume
            elif option_type == "PE":
                strike_data[strike]["put_ltp"] = ltp
                strike_data[strike]["put_volume"] = volume
            
            strike_data[strike]["total_volume"] = strike_data[strike]["call_volume"] + strike_data[strike]["put_volume"]
        
        # Convert to list and sort by strike price
        option_ltp_chain = list(strike_data.values())
        option_ltp_chain.sort(key=lambda x: x["strike"])
        
        return option_ltp_chain, expiry_dates
        
    except Exception as e:
        print(f"[ERROR] Failed to get option LTP data: {e}")
        return [], []

def get_option_data_with_ltp(expiry_timestamp):
    """Get option data including LTP for specific expiry"""
    try:
        fyers = get_fyers_client()
        data = {
            "symbol": "NSE:NIFTYBANK-INDEX",
            "strikecount": 100,
            "timestamp": expiry_timestamp
        }
        
        res = fyers.optionchain(data)
        if res["s"] != "ok":
            print("[ERROR] Option data not fetched:", res)
            return []
        
        return res["data"].get("optionsChain", [])
        
    except Exception as e:
        print(f"[ERROR] Failed to get option data with LTP: {e}")
        return []

def find_highest_volume_strike(option_ltp_chain):
    """Find the strike with highest total volume"""
    if not option_ltp_chain:
        return None
    
    highest_volume_strike = max(option_ltp_chain, key=lambda x: x["total_volume"])
    return highest_volume_strike["strike"]

def add_volume_color_classes(option_ltp_chain):
    """Add gradient color classes to call and put volumes"""
    if not option_ltp_chain:
        return option_ltp_chain

    # Extract all values for normalization
    call_volume_values = [opt["call_volume"] for opt in option_ltp_chain if opt["call_volume"] > 0]
    put_volume_values = [opt["put_volume"] for opt in option_ltp_chain if opt["put_volume"] > 0]

    # Get max values for normalization
    max_call_volume = max(call_volume_values) if call_volume_values else 1
    max_put_volume = max(put_volume_values) if put_volume_values else 1

    # Add color classes to each option
    for option in option_ltp_chain:
        # Call volume color intensity
        if option["call_volume"] > 0:
            call_intensity = calculate_color_intensity(option["call_volume"], max_call_volume)
            option["call_volume_class"] = f'call-volume-{call_intensity}'
        else:
            option["call_volume_class"] = ""

        # Put volume color intensity
        if option["put_volume"] > 0:
            put_intensity = calculate_color_intensity(option["put_volume"], max_put_volume)
            option["put_volume_class"] = f'put-volume-{put_intensity}'
        else:
            option["put_volume_class"] = ""

        # Format the volume values for display
        option["call_volume_display"] = format_number(option["call_volume"]) if option["call_volume"] > 0 else "-"
        option["put_volume_display"] = format_number(option["put_volume"]) if option["put_volume"] > 0 else "-"

    return option_ltp_chain

def get_current_month_futures_symbol():
    """Get the current month futures symbol for BankNifty"""
    return get_current_futures_symbol()

@app.route('/')
def index():
    # Get the current timestamp in IST
    last_updated = get_ist_time_string()
    
    # Get spot and futures prices
    spot_price = get_spot_price()
    futures_price = get_futures_price()
    
    # Get futures configuration info
    futures_info = get_futures_info()
    
    # Get option chain data
    option_chain = run_option_chain(return_data=True)
    
    # Find the closest strike to futures price
    closest_strike = find_closest_strike(futures_price, option_chain)
    
    # Add color intensity classes
    option_chain = add_color_classes(option_chain)
    
    return render_template('index.html',
                         spot_price=spot_price,
                         futures_price=futures_price,
                         futures_info=futures_info,
                         last_updated=last_updated,
                         option_chain=option_chain,
                         closest_strike=closest_strike)

@app.route('/oi-ltp')
def oi_ltp():
    """Route for OI-LTP page"""
    # Get the current timestamp in IST
    last_updated = get_ist_time_string()
    
    # Get spot price
    spot_price = get_spot_price()
    
    # Get futures configuration info
    futures_info = get_futures_info()
    
    # Get option LTP data
    option_ltp_chain, expiry_dates = get_option_ltp_data()
    
    # Find highest volume strike
    highest_volume_strike = find_highest_volume_strike(option_ltp_chain)
    
    # Add color intensity classes for volumes
    option_ltp_chain = add_volume_color_classes(option_ltp_chain)
    return render_template('oi_ltp.html',
                         spot_price=spot_price,
                         last_updated=last_updated,
                         option_ltp_chain=option_ltp_chain,
                         expiry_dates=expiry_dates,
                         highest_volume_strike=highest_volume_strike,
                         futures_info=futures_info)

@app.route('/trade')
def trade():
    """Route for Trade page"""
    # Get the current timestamp in IST
    last_updated = get_ist_time_string()

    # Get futures price for the current month
    futures_symbol = get_current_month_futures_symbol()
    futures_price = get_futures_price()

    # Get Heikin Ashi VWAP for BankNifty futures (15-min, using close price)
    ha_vwap = get_banknifty_heikin_ashi_vwap()

    # Determine if price is above or below each VWAP
    ha_price_position = "above" if futures_price > ha_vwap else "below"

    # Calculate the absolute difference between price and VWAPs
    price_ha_vwap_diff = abs(futures_price - ha_vwap)
    
    # Get option LTP data (same as oi-ltp)
    option_ltp_chain, expiry_dates = get_option_ltp_data()

    def is_500_strike(strike):
        return strike % 500 == 0

    call_lt_200 = [
        {'strike': o['strike'], 'ltp': o['call_ltp']}
        for o in option_ltp_chain
        if o.get('call_ltp', 0) < 200 and o.get('call_ltp', 0) > 0 and is_500_strike(o['strike'])
    ]
    put_lt_200 = [
        {'strike': o['strike'], 'ltp': o['put_ltp']}
        for o in option_ltp_chain
        if o.get('put_ltp', 0) < 200 and o.get('put_ltp', 0) > 0 and is_500_strike(o['strike'])
    ]

    call_lt_200 = sorted(call_lt_200, key=lambda x: x['strike'])[:2]
    put_lt_200 = sorted(put_lt_200, key=lambda x: x['strike'], reverse=True)[:2]

    # Get expiry string for symbol construction (e.g., 25JUN)
    expiry_str = ''
    if expiry_dates:
        # Try to extract e.g. '25JUN' from expiry_dates[0]['expiry']
        import re
        match = re.search(r'(\d{2}[A-Z]{3})', str(expiry_dates[0].get('expiry', '')))
        if match:
            expiry_str = match.group(1)
        else:
            expiry_str = '25JUN'  # fallback
    else:
        expiry_str = '25JUN'

    # Helper to build symbol
    def build_symbol(strike, option_type):
        return f"NSE:BANKNIFTY{expiry_str}{int(strike)}{option_type}"

    # For each call/put, fetch its own VWAPs
    for opt in call_lt_200:
        symbol = build_symbol(opt['strike'], 'CE')
        opt['ha_vwap'] = calculate_vwap(symbol, timeframe="15", source="close", anchor="session", heikin_ashi=True)
        opt['atr'] = calculate_atr(symbol, length=9, timeframe="15")
    for opt in put_lt_200:
        symbol = build_symbol(opt['strike'], 'PE')
        opt['ha_vwap'] = calculate_vwap(symbol, timeframe="15", source="close", anchor="session", heikin_ashi=True)
        opt['atr'] = calculate_atr(symbol, length=9, timeframe="15")

    return render_template('trade.html',
                         last_updated=last_updated,
                         futures_price=futures_price,
                         futures_symbol=futures_symbol,
                         ha_vwap=ha_vwap,
                         ha_price_position=ha_price_position,
                         price_ha_vwap_diff=price_ha_vwap_diff,
                         timeframe="15 min",
                         call_lt_200=call_lt_200,
                         put_lt_200=put_lt_200)

@app.route('/strike-details/<option_type>/<int:strike>')
def strike_details(option_type, strike):
    """
    Show 15m candle data for the selected strike and option type (CE/PE) with date filtering capability.
    Supports query parameters: date (YYYY-MM-DD format)
    """
    from datetime import date, timedelta, datetime as dt
    import re
    import pytz
    import pandas as pd
    import numpy as np
    
    # Get date parameter from query string, default to today in IST
    selected_date = request.args.get('date')
    if selected_date:
        try:
            target_date = dt.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = get_ist_date()
    else:
        target_date = get_ist_date()
    
    # Get expiry string for symbol construction (e.g., 25JUN)
    expiry_dates = get_expiry_dates()
    expiry_str = ''
    if expiry_dates:
        match = re.search(r'(\d{2}[A-Z]{3})', str(expiry_dates[0].get('expiry', '')))
        if match:
            expiry_str = match.group(1)
        else:
            expiry_str = '25JUN'  # fallback
    else:
        expiry_str = '25JUN'
    symbol = f"NSE:BANKNIFTY{expiry_str}{int(strike)}{option_type.upper()}"
    
    # Fetch 15m candles with more historical data for proper ATR calculation
    fyers = get_fyers_client()
    # Get 20 days of historical data to ensure proper ATR(9) calculation
    start_date = target_date - timedelta(days=20)
    from_date = start_date.strftime("%Y-%m-%d")
    to_date = target_date.strftime("%Y-%m-%d")
    
    # Get futures configuration info
    futures_info = get_futures_info()
    
    data = {
        "symbol": symbol,
        "resolution": "15",
        "date_format": "1",
        "range_from": from_date,
        "range_to": to_date,
        "cont_flag": "1"
    }
    response = fyers.history(data)
    candles = response["candles"] if response.get("s") == "ok" else []
    rows = []
    error_message = None
    
    if candles:
        try:
            # Handle different possible data structures from API
            if len(candles) > 0 and len(candles[0]) >= 5:
                # Standard case: timestamp, open, high, low, close, volume (6 columns)
                if len(candles[0]) >= 6:
                    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
                else:
                    # Fallback: only OHLC data (5 columns)
                    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
                    df['volume'] = 0  # Add volume column with default value
                
                # Convert to IST
                ist = pytz.timezone('Asia/Kolkata')
                df["datetime"] = pd.to_datetime(df["timestamp"], unit='s').dt.tz_localize('UTC').dt.tz_convert(ist)
                df = df.sort_values("datetime")
                
                # Calculate ATR(9) with RMA for all historical data first
                if len(df) > 1:
                    df['prev_close'] = df['close'].shift(1)
                    df['tr1'] = df['high'] - df['low']
                    df['tr2'] = abs(df['high'] - df['prev_close'])
                    df['tr3'] = abs(df['low'] - df['prev_close'])
                    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
                    
                    def rma(series, length):
                        """Wilder's RMA (smoothed moving average) for ATR calculation."""
                        result = [np.nan] * len(series)
                        if len(series) < length:
                            return pd.Series(result, index=series.index)
                        
                        # Calculate initial SMA for the first ATR value
                        sma = series.iloc[:length].mean()
                        result[length-1] = sma
                        
                        # Use RMA formula for subsequent values
                        alpha = 1 / length
                        for i in range(length, len(series)):
                            result[i] = (series.iloc[i] * alpha) + (result[i-1] * (1 - alpha))
                        
                        return pd.Series(result, index=series.index)
                    
                    # Calculate ATR using RMA
                    df['atr'] = rma(df['tr'], 9)
                
                # Filter to target day's data for display
                df_today = df[df['datetime'].dt.date == target_date].copy()
                
                # Only show rows from 9:15 AM onwards
                df_today = df_today[df_today['datetime'].dt.time >= pd.to_datetime('09:15:00').time()]
                
                if len(df_today) > 0:
                    # Heikin Ashi for target day
                    ha_open = [df_today['open'].iloc[0]]
                    ha_close = [(df_today['open'].iloc[0] + df_today['high'].iloc[0] + df_today['low'].iloc[0] + df_today['close'].iloc[0]) / 4]
                    
                    for i in range(1, len(df_today)):
                        ha_open.append((ha_open[i-1] + ha_close[i-1]) / 2)
                        ha_close.append((df_today['open'].iloc[i] + df_today['high'].iloc[i] + df_today['low'].iloc[i] + df_today['close'].iloc[i]) / 4)
                    
                    df_today['ha_open'] = ha_open
                    df_today['ha_close'] = ha_close
                    df_today['ha_high'] = df_today[['high', 'ha_open', 'ha_close']].max(axis=1)
                    df_today['ha_low'] = df_today[['low', 'ha_open', 'ha_close']].min(axis=1)
                    
                    # Heikin Ashi VWAP (cumulative, only target day)
                    if 'volume' in df_today.columns and df_today['volume'].sum() > 0:
                        df_today['ha_pv'] = df_today['ha_close'] * df_today['volume']
                        df_today['ha_cum_pv'] = df_today['ha_pv'].cumsum()
                        df_today['ha_cum_vol'] = df_today['volume'].cumsum()
                        df_today['ha_vwap'] = df_today['ha_cum_pv'] / df_today['ha_cum_vol']
                    else:
                        # Fallback: use simple moving average of ha_close
                        df_today['ha_vwap'] = df_today['ha_close'].expanding().mean()
                    
                    # Map ATR values from the full dataset to today's candles
                    atr_map = dict(zip(df['datetime'], df['atr']))
                    
                    # Prepare data for template
                    for _, row in df_today.iterrows():
                        open_price = float(row['open'])
                        close_price = float(row['close'])
                        ha_vwap_price = float(row['ha_vwap'])
                        
                        # Calculate status based on conditions:
                        # 1. Open integer value should be less than HA VWAP integer value
                        # 2. Close integer value should be greater than HA VWAP integer value
                        open_int = int(open_price)
                        close_int = int(close_price)
                        ha_vwap_int = int(ha_vwap_price)
                        
                        # Status logic for strike-details page:
                        # Green: Open integer < HA VWAP integer AND Close integer > HA VWAP integer AND |Open - Close| <= 20
                        # Red: Otherwise
                        open_close_diff = abs(open_price - close_price)
                        status = open_int < ha_vwap_int and close_int > ha_vwap_int and open_close_diff <= 20
                        
                        # Get ATR value for this candle
                        atr_value = atr_map.get(row['datetime'], np.nan)
                        
                        rows.append({
                            'time': row['datetime'].strftime('%H:%M'),
                            'open': open_price,
                            'high': float(row['high']),
                            'low': float(row['low']),
                            'close': close_price,
                            'ha_vwap': ha_vwap_price,
                            'atr': atr_value,
                            'status': status
                        })
                else:
                    error_message = f"No trading data available for {target_date.strftime('%Y-%m-%d')}. This might be a holiday or weekend."
            else:
                error_message = f"Invalid data format received for {target_date.strftime('%Y-%m-%d')}."
        except Exception as e:
            error_message = f"Error processing data for {target_date.strftime('%Y-%m-%d')}: {str(e)}"
            print(f"[DEBUG] Strike details error: {e}")
    else:
        error_message = f"No data available for {target_date.strftime('%Y-%m-%d')}. This might be a holiday, weekend, or the market was closed."
    
    return render_template('strike_details.html',
                          option_type=option_type,
                          strike=strike,
                          symbol=symbol,
                          rows=rows,
                          selected_date=target_date.strftime('%Y-%m-%d'),
                          futures_info=futures_info,
                          error_message=error_message)

@app.route('/futures-details')
def futures_details():
    """
    Show 15m candle data for BankNifty Futures with date filtering capability.
    Supports query parameters: date (YYYY-MM-DD format)
    """
    from datetime import date, timedelta, datetime as dt
    import pytz
    import pandas as pd
    
    # Get date parameter from query string, default to today in IST
    selected_date = request.args.get('date')
    if selected_date:
        try:
            target_date = dt.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = get_ist_date()
    else:
        target_date = get_ist_date()
    
    # Use current month futures symbol
    symbol = get_current_month_futures_symbol()
    
    # Set date range for data fetching
    from_date = target_date.strftime("%Y-%m-%d")
    to_date = target_date.strftime("%Y-%m-%d")
    
    # Get futures configuration info
    futures_info = get_futures_info()
    
    fyers = get_fyers_client()
    data = {
        "symbol": symbol,
        "resolution": "15",
        "date_format": "1",
        "range_from": from_date,
        "range_to": to_date,
        "cont_flag": "1"
    }
    
    response = fyers.history(data)
    candles = response["candles"] if response.get("s") == "ok" else []
    rows = []
    error_message = None
    
    if candles:
        try:
            # Handle different possible data structures from API
            if len(candles) > 0 and len(candles[0]) >= 5:
                # Standard case: timestamp, open, high, low, close, volume (6 columns)
                if len(candles[0]) >= 6:
                    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
                else:
                    # Fallback: only OHLC data (5 columns)
                    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
                    df['volume'] = 0  # Add volume column with default value
                
                ist = pytz.timezone('Asia/Kolkata')
                df["datetime"] = pd.to_datetime(df["timestamp"], unit='s').dt.tz_localize('UTC').dt.tz_convert(ist)
                df = df.sort_values("datetime")
                
                # Only show rows from 9:15 AM onwards
                df = df[df['datetime'].dt.time >= pd.to_datetime('09:15:00').time()]
                
                if len(df) > 0:
                    # Heikin Ashi calculations
                    ha_open = [df['open'].iloc[0]]
                    ha_close = [(df['open'].iloc[0] + df['high'].iloc[0] + df['low'].iloc[0] + df['close'].iloc[0]) / 4]
                    
                    for i in range(1, len(df)):
                        ha_open.append((ha_open[i-1] + ha_close[i-1]) / 2)
                        ha_close.append((df['open'].iloc[i] + df['high'].iloc[i] + df['low'].iloc[i] + df['close'].iloc[i]) / 4)
                    
                    df['ha_open'] = ha_open
                    df['ha_close'] = ha_close
                    df['ha_high'] = df[['high', 'ha_open', 'ha_close']].max(axis=1)
                    df['ha_low'] = df[['low', 'ha_open', 'ha_close']].min(axis=1)
                    
                    # Heikin Ashi VWAP (cumulative) - only if volume data exists
                    if 'volume' in df.columns and df['volume'].sum() > 0:
                        df['ha_pv'] = df['ha_close'] * df['volume']
                        df['ha_cum_pv'] = df['ha_pv'].cumsum()
                        df['ha_cum_vol'] = df['volume'].cumsum()
                        df['ha_vwap'] = df['ha_cum_pv'] / df['ha_cum_vol']
                    else:
                        # Fallback: use simple moving average of ha_close
                        df['ha_vwap'] = df['ha_close'].expanding().mean()
                    
                    # Prepare data for template
                    for _, row in df.iterrows():
                        volume_val = 0
                        if 'volume' in df.columns and pd.notna(row.get('volume')):
                            try:
                                volume_val = int(float(row['volume']))
                            except (ValueError, TypeError):
                                volume_val = 0
                        
                        open_price = float(row['open'])
                        close_price = float(row['close'])
                        ha_vwap_price = float(row['ha_vwap'])
                        
                        # Calculate status based on conditions:
                        # 1. Open integer value should be less than HA VWAP integer value
                        # 2. Close integer value should be greater than HA VWAP integer value
                        open_int = int(open_price)
                        close_int = int(close_price)
                        ha_vwap_int = int(ha_vwap_price)
                        
                        open_condition = open_int < ha_vwap_int
                        close_condition = close_int > ha_vwap_int
                        # Green conditions: (Open < VWAP AND Close > VWAP) OR (Open > VWAP AND Close > VWAP)
                        condition1 = open_int < ha_vwap_int and close_int > ha_vwap_int
                        condition2 = open_int > ha_vwap_int and close_int > ha_vwap_int
                        status = condition1 or condition2
                        
                        rows.append({
                            'time': row['datetime'].strftime('%H:%M'),
                            'open': open_price,
                            'high': float(row['high']),
                            'low': float(row['low']),
                            'close': close_price,
                            'ha_vwap': ha_vwap_price,
                            'volume': volume_val,
                            'status': status
                        })
                else:
                    error_message = f"No trading data available for {target_date.strftime('%Y-%m-%d')}. This might be a holiday or weekend."
            else:
                error_message = f"Invalid data format received for {target_date.strftime('%Y-%m-%d')}."
        except Exception as e:
            error_message = f"Error processing data for {target_date.strftime('%Y-%m-%d')}: {str(e)}"
            print(f"[DEBUG] Error details: {e}")
            print(f"[DEBUG] Candles data sample: {candles[:2] if candles else 'No candles'}")  # Print first 2 rows for debugging
    else:
        error_message = f"No data available for {target_date.strftime('%Y-%m-%d')}. This might be a holiday, weekend, or the market was closed."
    
    return render_template('futures_details.html',
                          symbol=symbol,
                          rows=rows,
                          selected_date=target_date.strftime('%Y-%m-%d'),
                          futures_info=futures_info,
                          error_message=error_message)

@app.route('/futures-config')
def futures_config():
    """
    Show futures configuration page with current and next month details.
    """
    futures_info = get_futures_info()
    return render_template('futures_config.html',
                          futures_info=futures_info)

@app.route('/fut-oi-chart')
def fut_oi_chart():
    """
    Show futures price chart with OI data - 15 minute candles with HA VWAP
    """
    from datetime import date, timedelta, datetime as dt
    import pytz
    import pandas as pd
    
    # Get date parameter from query string, default to today in IST
    selected_date = request.args.get('date')
    if selected_date:
        try:
            target_date = dt.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = get_ist_date()
    else:
        target_date = get_ist_date()
    
    # Use current month futures symbol
    symbol = get_current_month_futures_symbol()
    
    # Set date range for data fetching
    from_date = target_date.strftime("%Y-%m-%d")
    to_date = target_date.strftime("%Y-%m-%d")
    
    # Get futures configuration info
    futures_info = get_futures_info()
    
    fyers = get_fyers_client()
    data = {
        "symbol": symbol,
        "resolution": "15",
        "date_format": "1",
        "range_from": from_date,
        "range_to": to_date,
        "cont_flag": "1"
    }
    
    response = fyers.history(data)
    candles = response["candles"] if response.get("s") == "ok" else []
    rows = []
    error_message = None
    
    if candles:
        try:
            # Handle different possible data structures from API
            if len(candles) > 0 and len(candles[0]) >= 5:
                # Standard case: timestamp, open, high, low, close, volume (6 columns)
                if len(candles[0]) >= 6:
                    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
                else:
                    # Fallback: only OHLC data (5 columns)
                    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
                    df['volume'] = 0  # Add volume column with default value
                
                ist = pytz.timezone('Asia/Kolkata')
                df["datetime"] = pd.to_datetime(df["timestamp"], unit='s').dt.tz_localize('UTC').dt.tz_convert(ist)
                df = df.sort_values("datetime")
                
                # Only show rows from 9:15 AM onwards
                df = df[df['datetime'].dt.time >= pd.to_datetime('09:15:00').time()]
                
                if len(df) > 0:
                    # Heikin Ashi calculations
                    ha_open = [df['open'].iloc[0]]
                    ha_close = [(df['open'].iloc[0] + df['high'].iloc[0] + df['low'].iloc[0] + df['close'].iloc[0]) / 4]
                    
                    for i in range(1, len(df)):
                        ha_open.append((ha_open[i-1] + ha_close[i-1]) / 2)
                        ha_close.append((df['open'].iloc[i] + df['high'].iloc[i] + df['low'].iloc[i] + df['close'].iloc[i]) / 4)
                    
                    df['ha_open'] = ha_open
                    df['ha_close'] = ha_close
                    df['ha_high'] = df[['high', 'ha_open', 'ha_close']].max(axis=1)
                    df['ha_low'] = df[['low', 'ha_open', 'ha_close']].min(axis=1)
                    
                    # Heikin Ashi VWAP (cumulative) - only if volume data exists
                    if 'volume' in df.columns and df['volume'].sum() > 0:
                        df['ha_pv'] = df['ha_close'] * df['volume']
                        df['ha_cum_pv'] = df['ha_pv'].cumsum()
                        df['ha_cum_vol'] = df['volume'].cumsum()
                        df['ha_vwap'] = df['ha_cum_pv'] / df['ha_cum_vol']
                    else:
                        # Fallback: use simple moving average of ha_close
                        df['ha_vwap'] = df['ha_close'].expanding().mean()
                    
                    # Prepare data for template
                    for _, row in df.iterrows():
                        volume_val = 0
                        if 'volume' in df.columns and pd.notna(row.get('volume')):
                            try:
                                volume_val = int(float(row['volume']))
                            except (ValueError, TypeError):
                                volume_val = 0
                        
                        open_price = float(row['open'])
                        close_price = float(row['close'])
                        ha_vwap_price = float(row['ha_vwap'])
                        
                        rows.append({
                            'time': row['datetime'].strftime('%H:%M'),
                            'datetime': row['datetime'].isoformat(),
                            'open': open_price,
                            'high': float(row['high']),
                            'low': float(row['low']),
                            'close': close_price,
                            'ha_open': float(row['ha_open']),
                            'ha_high': float(row['ha_high']),
                            'ha_low': float(row['ha_low']),
                            'ha_close': float(row['ha_close']),
                            'ha_vwap': ha_vwap_price,
                            'volume': volume_val
                        })
                else:
                    error_message = f"No trading data available for {target_date.strftime('%Y-%m-%d')}. This might be a holiday or weekend."
            else:
                error_message = f"Invalid data format received for {target_date.strftime('%Y-%m-%d')}."
        except Exception as e:
            error_message = f"Error processing data for {target_date.strftime('%Y-%m-%d')}: {str(e)}"
            print(f"[DEBUG] Error details: {e}")
    else:
        error_message = f"No data available for {target_date.strftime('%Y-%m-%d')}. This might be a holiday, weekend, or the market was closed."
    
    return render_template('fut_oi_chart.html',
                          symbol=symbol,
                          rows=rows,
                          selected_date=target_date.strftime('%Y-%m-%d'),
                          futures_info=futures_info,
                          error_message=error_message)

# AJAX endpoints for auto-updating data
@app.route('/api/index-data')
def api_index_data():
    """AJAX endpoint for index page data"""
    try:
        # Get the current timestamp in IST
        last_updated = get_ist_time_string()
        
        # Get spot and futures prices
        spot_price = get_spot_price()
        futures_price = get_futures_price()
        
        # Get futures configuration info
        futures_info = get_futures_info()
        
        # Get option chain data
        option_chain = run_option_chain(return_data=True)
        
        # Find the closest strike to futures price
        closest_strike = find_closest_strike(futures_price, option_chain)
        
        # Add color intensity classes
        option_chain = add_color_classes(option_chain)
        
        return jsonify({
            'success': True,
            'data': {
                'spot_price': spot_price,
                'futures_price': futures_price,
                'futures_info': futures_info,
                'last_updated': last_updated,
                'option_chain': option_chain,
                'closest_strike': closest_strike
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/oi-ltp-data')
def api_oi_ltp_data():
    """AJAX endpoint for OI-LTP page data"""
    try:
        # Get the current timestamp in IST
        last_updated = get_ist_time_string()
        
        # Get spot price
        spot_price = get_spot_price()
        
        # Get futures configuration info
        futures_info = get_futures_info()
        
        # Get option LTP data
        option_ltp_chain, expiry_dates = get_option_ltp_data()
        
        # Find highest volume strike
        highest_volume_strike = find_highest_volume_strike(option_ltp_chain)
        
        # Add color intensity classes for volumes
        option_ltp_chain = add_volume_color_classes(option_ltp_chain)
        
        return jsonify({
            'success': True,
            'data': {
                'spot_price': spot_price,
                'last_updated': last_updated,
                'option_ltp_chain': option_ltp_chain,
                'expiry_dates': expiry_dates,
                'highest_volume_strike': highest_volume_strike,
                'futures_info': futures_info
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trade-data')
def api_trade_data():
    """AJAX endpoint for Trade page data"""
    try:
        # Get the current timestamp in IST
        last_updated = get_ist_time_string()

        # Get futures price for the current month
        futures_symbol = get_current_month_futures_symbol()
        futures_price = get_futures_price()

        # Get Heikin Ashi VWAP for BankNifty futures (15-min, using close price)
        ha_vwap = get_banknifty_heikin_ashi_vwap()

        # Determine if price is above or below each VWAP
        ha_price_position = "above" if futures_price > ha_vwap else "below"

        # Calculate the absolute difference between price and VWAPs
        price_ha_vwap_diff = abs(futures_price - ha_vwap)
        
        # Get option LTP data (same as oi-ltp)
        option_ltp_chain, expiry_dates = get_option_ltp_data()

        def is_500_strike(strike):
            return strike % 500 == 0

        call_lt_200 = [
            {'strike': o['strike'], 'ltp': o['call_ltp']}
            for o in option_ltp_chain
            if o.get('call_ltp', 0) < 200 and o.get('call_ltp', 0) > 0 and is_500_strike(o['strike'])
        ]
        put_lt_200 = [
            {'strike': o['strike'], 'ltp': o['put_ltp']}
            for o in option_ltp_chain
            if o.get('put_ltp', 0) < 200 and o.get('put_ltp', 0) > 0 and is_500_strike(o['strike'])
        ]

        call_lt_200 = sorted(call_lt_200, key=lambda x: x['strike'])[:2]
        put_lt_200 = sorted(put_lt_200, key=lambda x: x['strike'], reverse=True)[:2]

        # Get expiry string for symbol construction (e.g., 25JUN)
        expiry_str = ''
        if expiry_dates:
            # Try to extract e.g. '25JUN' from expiry_dates[0]['expiry']
            import re
            match = re.search(r'(\d{2}[A-Z]{3})', str(expiry_dates[0].get('expiry', '')))
            if match:
                expiry_str = match.group(1)
            else:
                expiry_str = '25JUN'  # fallback
        else:
            expiry_str = '25JUN'

        # Helper to build symbol
        def build_symbol(strike, option_type):
            return f"NSE:BANKNIFTY{expiry_str}{int(strike)}{option_type}"

        # For each call/put, fetch its own VWAPs
        for opt in call_lt_200:
            symbol = build_symbol(opt['strike'], 'CE')
            opt['ha_vwap'] = calculate_vwap(symbol, timeframe="15", source="close", anchor="session", heikin_ashi=True)
            opt['atr'] = calculate_atr(symbol, length=9, timeframe="15")
        for opt in put_lt_200:
            symbol = build_symbol(opt['strike'], 'PE')
            opt['ha_vwap'] = calculate_vwap(symbol, timeframe="15", source="close", anchor="session", heikin_ashi=True)
            opt['atr'] = calculate_atr(symbol, length=9, timeframe="15")

        return jsonify({
            'success': True,
            'data': {
                'last_updated': last_updated,
                'futures_price': futures_price,
                'futures_symbol': futures_symbol,
                'ha_vwap': ha_vwap,
                'ha_price_position': ha_price_position,
                'price_ha_vwap_diff': price_ha_vwap_diff,
                'timeframe': "15 min",
                'call_lt_200': call_lt_200,
                'put_lt_200': put_lt_200
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/futures-details-data')
def api_futures_details_data():
    """AJAX endpoint for Futures Details page data"""
    try:
        from datetime import date, timedelta, datetime as dt
        import pytz
        import pandas as pd
        
        # Get date parameter from query string, default to today in IST
        selected_date = request.args.get('date')
        if selected_date:
            try:
                target_date = dt.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                target_date = get_ist_date()
        else:
            target_date = get_ist_date()
        
        # Use current month futures symbol
        symbol = get_current_month_futures_symbol()
        
        # Set date range for data fetching
        from_date = target_date.strftime("%Y-%m-%d")
        to_date = target_date.strftime("%Y-%m-%d")
        
        # Get futures configuration info
        futures_info = get_futures_info()
        
        fyers = get_fyers_client()
        data = {
            "symbol": symbol,
            "resolution": "15",
            "date_format": "1",
            "range_from": from_date,
            "range_to": to_date,
            "cont_flag": "1"
        }
        
        response = fyers.history(data)
        candles = response["candles"] if response.get("s") == "ok" else []
        rows = []
        error_message = None
        
        if candles:
            try:
                # Handle different possible data structures from API
                if len(candles) > 0 and len(candles[0]) >= 5:
                    # Standard case: timestamp, open, high, low, close, volume (6 columns)
                    if len(candles[0]) >= 6:
                        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
                    else:
                        # Fallback: only OHLC data (5 columns)
                        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
                        df['volume'] = 0  # Add volume column with default value
                    
                    ist = pytz.timezone('Asia/Kolkata')
                    df["datetime"] = pd.to_datetime(df["timestamp"], unit='s').dt.tz_localize('UTC').dt.tz_convert(ist)
                    df = df.sort_values("datetime")
                    
                    # Only show rows from 9:15 AM onwards
                    df = df[df['datetime'].dt.time >= pd.to_datetime('09:15:00').time()]
                    
                    if len(df) > 0:
                        # Heikin Ashi calculations
                        ha_open = [df['open'].iloc[0]]
                        ha_close = [(df['open'].iloc[0] + df['high'].iloc[0] + df['low'].iloc[0] + df['close'].iloc[0]) / 4]
                        
                        for i in range(1, len(df)):
                            ha_open.append((ha_open[i-1] + ha_close[i-1]) / 2)
                            ha_close.append((df['open'].iloc[i] + df['high'].iloc[i] + df['low'].iloc[i] + df['close'].iloc[i]) / 4)
                        
                        df['ha_open'] = ha_open
                        df['ha_close'] = ha_close
                        df['ha_high'] = df[['high', 'ha_open', 'ha_close']].max(axis=1)
                        df['ha_low'] = df[['low', 'ha_open', 'ha_close']].min(axis=1)
                        
                        # Heikin Ashi VWAP (cumulative) - only if volume data exists
                        if 'volume' in df.columns and df['volume'].sum() > 0:
                            df['ha_pv'] = df['ha_close'] * df['volume']
                            df['ha_cum_pv'] = df['ha_pv'].cumsum()
                            df['ha_cum_vol'] = df['volume'].cumsum()
                            df['ha_vwap'] = df['ha_cum_pv'] / df['ha_cum_vol']
                        else:
                            # Fallback: use simple moving average of ha_close
                            df['ha_vwap'] = df['ha_close'].expanding().mean()
                        
                        # Prepare data for template
                        for _, row in df.iterrows():
                            volume_val = 0
                            if 'volume' in df.columns and pd.notna(row.get('volume')):
                                try:
                                    volume_val = int(float(row['volume']))
                                except (ValueError, TypeError):
                                    volume_val = 0
                            
                            open_price = float(row['open'])
                            close_price = float(row['close'])
                            ha_vwap_price = float(row['ha_vwap'])
                            
                            # Calculate status based on conditions:
                            open_int = int(open_price)
                            close_int = int(close_price)
                            ha_vwap_int = int(ha_vwap_price)
                            
                            condition1 = open_int < ha_vwap_int and close_int > ha_vwap_int
                            condition2 = open_int > ha_vwap_int and close_int > ha_vwap_int
                            status = condition1 or condition2
                            
                            rows.append({
                                'time': row['datetime'].strftime('%H:%M'),
                                'open': open_price,
                                'high': float(row['high']),
                                'low': float(row['low']),
                                'close': close_price,
                                'ha_vwap': ha_vwap_price,
                                'volume': volume_val,
                                'status': status
                            })
                    else:
                        error_message = f"No trading data available for {target_date.strftime('%Y-%m-%d')}."
                else:
                    error_message = f"Invalid data format received for {target_date.strftime('%Y-%m-%d')}."
            except Exception as e:
                error_message = f"Error processing data for {target_date.strftime('%Y-%m-%d')}: {str(e)}"
        else:
            error_message = f"No data available for {target_date.strftime('%Y-%m-%d')}."
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'rows': rows,
                'selected_date': target_date.strftime('%Y-%m-%d'),
                'futures_info': futures_info,
                'error_message': error_message,
                'last_updated': get_ist_time_string()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/strike-details-data/<option_type>/<int:strike>')
def api_strike_details_data(option_type, strike):
    """AJAX endpoint for Strike Details page data"""
    try:
        from datetime import date, timedelta, datetime as dt
        import re
        import pytz
        import pandas as pd
        import numpy as np
        
        # Get date parameter from query string, default to today in IST
        selected_date = request.args.get('date')
        if selected_date:
            try:
                target_date = dt.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                target_date = get_ist_date()
        else:
            target_date = get_ist_date()
        
        # Get expiry string for symbol construction (e.g., 25JUN)
        expiry_dates = get_expiry_dates()
        expiry_str = ''
        if expiry_dates:
            match = re.search(r'(\d{2}[A-Z]{3})', str(expiry_dates[0].get('expiry', '')))
            if match:
                expiry_str = match.group(1)
            else:
                expiry_str = '25JUN'  # fallback
        else:
            expiry_str = '25JUN'
        symbol = f"NSE:BANKNIFTY{expiry_str}{int(strike)}{option_type.upper()}"
        
        # Fetch 15m candles with more historical data for proper ATR calculation
        fyers = get_fyers_client()
        # Get 20 days of historical data to ensure proper ATR(9) calculation
        start_date = target_date - timedelta(days=20)
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = target_date.strftime("%Y-%m-%d")
        
        # Get futures configuration info
        futures_info = get_futures_info()
        
        data = {
            "symbol": symbol,
            "resolution": "15",
            "date_format": "1",
            "range_from": from_date,
            "range_to": to_date,
            "cont_flag": "1"
        }
        response = fyers.history(data)
        candles = response["candles"] if response.get("s") == "ok" else []
        rows = []
        error_message = None
        
        if candles:
            try:
                # Handle different possible data structures from API
                if len(candles) > 0 and len(candles[0]) >= 5:
                    # Standard case: timestamp, open, high, low, close, volume (6 columns)
                    if len(candles[0]) >= 6:
                        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
                    else:
                        # Fallback: only OHLC data (5 columns)
                        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
                        df['volume'] = 0  # Add volume column with default value
                    
                    # Convert to IST
                    ist = pytz.timezone('Asia/Kolkata')
                    df["datetime"] = pd.to_datetime(df["timestamp"], unit='s').dt.tz_localize('UTC').dt.tz_convert(ist)
                    df = df.sort_values("datetime")
                    
                    # Calculate ATR(9) with RMA for all historical data first
                    if len(df) > 1:
                        df['prev_close'] = df['close'].shift(1)
                        df['tr1'] = df['high'] - df['low']
                        df['tr2'] = abs(df['high'] - df['prev_close'])
                        df['tr3'] = abs(df['low'] - df['prev_close'])
                        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
                        
                        def rma(series, length):
                            """Wilder's RMA (smoothed moving average) for ATR calculation."""
                            result = [np.nan] * len(series)
                            if len(series) < length:
                                return pd.Series(result, index=series.index)
                            
                            # Calculate initial SMA for the first ATR value
                            sma = series.iloc[:length].mean()
                            result[length-1] = sma
                            
                            # Use RMA formula for subsequent values
                            alpha = 1 / length
                            for i in range(length, len(series)):
                                result[i] = (series.iloc[i] * alpha) + (result[i-1] * (1 - alpha))
                            
                            return pd.Series(result, index=series.index)
                        
                        # Calculate ATR using RMA
                        df['atr'] = rma(df['tr'], 9)
                    
                    # Filter to target day's data for display
                    df_today = df[df['datetime'].dt.date == target_date].copy()
                    
                    # Only show rows from 9:15 AM onwards
                    df_today = df_today[df_today['datetime'].dt.time >= pd.to_datetime('09:15:00').time()]
                    
                    if len(df_today) > 0:
                        # Heikin Ashi for target day
                        ha_open = [df_today['open'].iloc[0]]
                        ha_close = [(df_today['open'].iloc[0] + df_today['high'].iloc[0] + df_today['low'].iloc[0] + df_today['close'].iloc[0]) / 4]
                        
                        for i in range(1, len(df_today)):
                            ha_open.append((ha_open[i-1] + ha_close[i-1]) / 2)
                            ha_close.append((df_today['open'].iloc[i] + df_today['high'].iloc[i] + df_today['low'].iloc[i] + df_today['close'].iloc[i]) / 4)
                        
                        df_today['ha_open'] = ha_open
                        df_today['ha_close'] = ha_close
                        df_today['ha_high'] = df_today[['high', 'ha_open', 'ha_close']].max(axis=1)
                        df_today['ha_low'] = df_today[['low', 'ha_open', 'ha_close']].min(axis=1)
                        
                        # Heikin Ashi VWAP (cumulative, only target day)
                        if 'volume' in df_today.columns and df_today['volume'].sum() > 0:
                            df_today['ha_pv'] = df_today['ha_close'] * df_today['volume']
                            df_today['ha_cum_pv'] = df_today['ha_pv'].cumsum()
                            df_today['ha_cum_vol'] = df_today['volume'].cumsum()
                            df_today['ha_vwap'] = df_today['ha_cum_pv'] / df_today['ha_cum_vol']
                        else:
                            # Fallback: use simple moving average of ha_close
                            df_today['ha_vwap'] = df_today['ha_close'].expanding().mean()
                        
                        # Map ATR values from the full dataset to today's candles
                        atr_map = dict(zip(df['datetime'], df['atr']))
                        
                        # Prepare data for template
                        for _, row in df_today.iterrows():
                            open_price = float(row['open'])
                            close_price = float(row['close'])
                            ha_vwap_price = float(row['ha_vwap'])
                            
                            # Calculate status based on conditions:
                            open_int = int(open_price)
                            close_int = int(close_price)
                            ha_vwap_int = int(ha_vwap_price)
                            
                            # Status logic for strike-details page:
                            # Green: Open integer < HA VWAP integer AND Close integer > HA VWAP integer AND |Open - Close| <= 20
                            open_close_diff = abs(open_price - close_price)
                            status = open_int < ha_vwap_int and close_int > ha_vwap_int and open_close_diff <= 20
                            
                            # Get ATR value for this candle
                            atr_value = atr_map.get(row['datetime'], np.nan)
                            
                            rows.append({
                                'time': row['datetime'].strftime('%H:%M'),
                                'open': open_price,
                                'high': float(row['high']),
                                'low': float(row['low']),
                                'close': close_price,
                                'ha_vwap': ha_vwap_price,
                                'atr': atr_value,
                                'status': status
                            })
                    else:
                        error_message = f"No trading data available for {target_date.strftime('%Y-%m-%d')}."
                else:
                    error_message = f"Invalid data format received for {target_date.strftime('%Y-%m-%d')}."
            except Exception as e:
                error_message = f"Error processing data for {target_date.strftime('%Y-%m-%d')}: {str(e)}"
        else:
            error_message = f"No data available for {target_date.strftime('%Y-%m-%d')}."
        
        return jsonify({
            'success': True,
            'data': {
                'option_type': option_type,
                'strike': strike,
                'symbol': symbol,
                'rows': rows,
                'selected_date': target_date.strftime('%Y-%m-%d'),
                'futures_info': futures_info,
                'error_message': error_message,
                'last_updated': get_ist_time_string()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': get_ist_time_string(),
        'service': 'BankNifty Option Chain'
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    try:
        # Test basic functionality
        spot_price = get_spot_price()
        return jsonify({
            'status': 'operational',
            'timestamp': get_ist_time_string(),
            'spot_price': spot_price,
            'services': {
                'fyers_api': 'connected',
                'option_chain': 'active',
                'web_interface': 'running'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'timestamp': get_ist_time_string(),
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting BankNifty Web Application...")
    print("Note: Run 'python snapshot_service.py' in a separate terminal for option chain snapshots")
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    try:
        app.run(debug=False, host='0.0.0.0', port=port)
    except (KeyboardInterrupt, SystemExit):
        print("Web application stopped")
