# option_chain_fetcher.py

from token_manager import get_fyers_client
from datetime import datetime
from collections import defaultdict
from fyers_apiv3 import fyersModel
from config import client_id
from token_manager import read_token
from futures_config import get_current_futures_symbol, get_next_futures_symbol

# Create fyers client
access_token = read_token()
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")

def get_spot_price():
    try:
        symbol = "NSE:NIFTYBANK-INDEX"
        data = {"symbols": symbol}
        res = fyers.quotes(data)

        # Add debug print
        print("[DEBUG] get_spot_price() response:", res)

        if res and "d" in res and res["d"] and len(res["d"]) > 0:
            return res["d"][0]["v"]["lp"]
        else:
            print(f"[ERROR] Invalid spot price response: {res}")
            return 50000  # Default fallback value for BankNifty
    except Exception as e:
        print(f"[ERROR] Failed to get spot price: {e}")
        return 50000  # Default fallback value



def get_futures_price():
    try:
        symbol = get_current_futures_symbol()
        data = {"symbols": symbol}
        res = fyers.quotes(data)

        # Add debug print
        print(f"[DEBUG] get_futures_price() for {symbol} response:", res)

        if res and "d" in res and res["d"] and len(res["d"]) > 0:
            return res["d"][0]["v"]["lp"]
        else:
            print(f"[ERROR] Invalid futures price response: {res}")
            return 50000  # Default fallback value for BankNifty futures
    except Exception as e:
        print(f"[ERROR] Failed to get futures price: {e}")
        return 50000  # Default fallback value



def fetch_option_chain_for_expiry(symbol, expiry_timestamp, fyers):
    data = {
        "symbol": symbol,
        "strikecount": 0,  # 0 = full chain
        "timestamp": str(expiry_timestamp)
    }
    response = fyers.optionchain(data=data)
    if response.get("s") != "ok":
        print(f"⚠️ Error: {response.get('message')}")
        return []

    return response["data"].get("optionsChain", [])


def combine_option_chain_data(option_chain_list):
    combined = defaultdict(lambda: {"CALL": {"oi": 0, "chg_oi": 0}, "PUT": {"oi": 0, "chg_oi": 0}})
    for entry in option_chain_list:
        strike = entry["strike_price"]
        side = "CALL" if entry["option_type"] == "CE" else "PUT"
        combined[strike][side]["oi"] += entry.get("oi", 0)
        combined[strike][side]["chg_oi"] += entry.get("oich", 0)
    return combined


def print_option_chain_table(combined):
    print(f"\n{'Strike':<8} {'CALL_OI':<12} {'CALL_ChgOI':<12} | {'PUT_OI':<12} {'PUT_ChgOI':<12}")
    print("-" * 65)
    for strike in sorted(combined.keys()):
        call = combined[strike]["CALL"]
        put = combined[strike]["PUT"]
        print(f"{strike:<8} {call['oi']:<12} {call['chg_oi']:<12} | {put['oi']:<12} {put['chg_oi']:<12}")

def get_fyers_client():
    token = read_token()
    return fyersModel.FyersModel(client_id=client_id, token=token, is_async=False)

def get_option_chain_data(expiry=None):
    fyers = get_fyers_client()
    data = {
        "symbol": "NSE:NIFTYBANK-INDEX",  # correct symbol for BankNifty index
        "strikecount": 0,
        "timestamp": "",
    }
    if expiry:
        data["expiry"] = expiry

    response = fyers.option_chain(data=data)
    print("[DEBUG] Option Chain Raw Response:")
    print(response)
    
    if response.get("s") != "ok":
        print("[ERROR] Fyers returned an error:", response.get("message"))
        return []

    return response.get("data", {}).get("optionsChain", [])


def print_header():
    print("\nCALL OPTIONS                        Strike    PUT OPTIONS")
    print("-" * 70)

def format_option_data(data):
    if not data:
        return " " * 30
    return f"{data['ltp']:7.2f} {data['change_perc']:6.2f}% {data['volume']:7d} {data['oi']:7d}"

def print_row(strike, call_data, put_data):
    call_str = format_option_data(call_data) if call_data else " " * 30
    put_str = format_option_data(put_data) if put_data else " " * 30
    print(f"{call_str} {strike:8.2f} {put_str}")

def run_option_chain(return_data=False):
    fyers = get_fyers_client()

    # Get BankNifty Spot Price (Index)
    spot_data = fyers.quotes({"symbols": "NSE:NIFTYBANK-INDEX"})
    spot_ltp = spot_data["d"][0]["v"]["lp"]

    # Get BankNifty Futures Price (automatically uses current month)
    future_symbol = get_current_futures_symbol()
    future_data = fyers.quotes({"symbols": future_symbol})
    future_ltp = future_data["d"][0]["v"]["lp"]

    # Print both
    print(f"\n📊 BankNifty - Spot : {spot_ltp:.2f}      BankNifty - Current FUT ({future_symbol}) : {future_ltp:.2f}")

    # Use correct symbol for optionchain
    symbol = "NSE:NIFTYBANK-INDEX"

    # Get available expiries
    sample_data = {"symbol": symbol, "strikecount": 1}
    sample_response = fyers.optionchain(data=sample_data)

    if sample_response.get("s") != "ok":
        print(f"❌ Failed to get expiry list: {sample_response.get('message')}")
        return

    expiry_list = sample_response["data"].get("expiryData", [])
    if len(expiry_list) < 2:
        print("⚠️ Not enough expiry data available.")
        return

    expiry1 = expiry_list[0]["expiry"]
    expiry2 = expiry_list[1]["expiry"]
    print(f"\n📅 Expiries: {expiry_list[0]['date']} and {expiry_list[1]['date']}")

    # Fetch option chain for both expiries
    chain1 = fetch_option_chain_for_expiry(symbol, expiry1, fyers)
    chain2 = fetch_option_chain_for_expiry(symbol, expiry2, fyers)
    full_chain = chain1 + chain2

    print(f"\n🔄 Fetched {len(full_chain)} option contracts from both expiries.")

    # Process and display
    combined = combine_option_chain_data(full_chain)
    print_option_chain_table(combined)

    # Create a list to store the organized data
    organized_data = []
    
    all_strikes = set(combined.keys())
    
    for strike in sorted(all_strikes, reverse=True):  # reverse=True for descending order
        call_data = combined[strike]["CALL"]
        put_data = combined[strike]["PUT"]
        
        row = {
            'strike': strike,
            'call': {
                'oi': call_data['oi'],
                'chg_oi': call_data['chg_oi']  # This is the Change in OI
            },
            'put': {
                'oi': put_data['oi'], 
                'chg_oi': put_data['chg_oi']   # This is the Change in OI
            }
        }
        organized_data.append(row)
    
    if return_data:
        return organized_data
    
    # Print the option chain (original terminal output)
    print_header()
    call_options = {strike: combined[strike]["CALL"] for strike in all_strikes}
    put_options = {strike: combined[strike]["PUT"] for strike in all_strikes}
    for strike in sorted(all_strikes, reverse=True):  # reverse=True for descending order
        print_row(strike, call_options.get(strike), put_options.get(strike))

# Add this at the bottom of option_chain_fetcher.py

def fetch_and_combine_option_chain_data():
    spot_price = get_spot_price()  # Use NSE:NIFTYBANK-INDEX
    fut_price = get_futures_price()

    expiry_dates = get_expiry_dates()
    if len(expiry_dates) < 2:
        print("[ERROR] Less than 2 expiry dates available.")
        return spot_price, fut_price, []

    expiry1 = expiry_dates[0]["expiry"]
    expiry2 = expiry_dates[1]["expiry"]

    all_data = get_option_chain_data(expiry1) + get_option_chain_data(expiry2)
    chain = build_option_chain(all_data)

    return spot_price, fut_price, chain

def get_expiry_dates():
    fyers = get_fyers_client()
    data = {
        "symbol": "NSE:NIFTYBANK-INDEX",  # Correct symbol!
        "strikecount": 1,
        "timestamp": ""
    }

    res = fyers.optionchain(data)
    if res["s"] == "ok" and "data" in res and "expiryData" in res["data"]:
        return res["data"]["expiryData"]
    else:
        print("[ERROR] Expiry dates not found:", res)
        return []

def get_option_data_for_expiry(expiry_timestamp):

    fyers = fyersModel.FyersModel(
        client_id=client_id,
        token=read_token(),
        is_async=False,
        log_path=""
    )

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


def build_option_chain_data():
    expiry_dates = get_expiry_dates()
    if len(expiry_dates) < 2:
        print("[ERROR] Less than 2 expiry dates available.")
        return []

    exp1 = expiry_dates[0]
    exp2 = expiry_dates[1]

    print(f"\n📅 Expiries: {exp1['date']} and {exp2['date']}")

    chain1 = get_option_data_for_expiry(exp1["expiry"])
    chain2 = get_option_data_for_expiry(exp2["expiry"])

    combined = chain1 + chain2
    print(f"\n🔄 Fetched {len(combined)} option contracts from both expiries.\n")
    return combined

from collections import defaultdict

def build_option_chain(options_data):
    strike_map = defaultdict(lambda: {
        "CE_oi": 0,
        "CE_chg": 0,
        "PE_oi": 0,
        "PE_chg": 0
    })

    for opt in options_data:
        strike = opt.get("strike_price")
        option_type = opt.get("option_type")
        oi = opt.get("oi", 0)
        oich = opt.get("oich", 0)

        if option_type == "CE":
            strike_map[strike]["CE_oi"] += oi
            strike_map[strike]["CE_chg"] += oich
        elif option_type == "PE":
            strike_map[strike]["PE_oi"] += oi
            strike_map[strike]["PE_chg"] += oich

    # Sort by strike price for clean output
    sorted_data = []
    for strike in sorted(strike_map.keys()):
        entry = strike_map[strike]
        sorted_data.append({
            "strike": strike,
            "call_oi": entry["CE_oi"],
            "call_chg_oi": entry["CE_chg"],
            "put_oi": entry["PE_oi"],
            "put_chg_oi": entry["PE_chg"]
        })

    return sorted_data




