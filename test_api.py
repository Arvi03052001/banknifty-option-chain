#!/usr/bin/env python3
"""
Test script to verify Fyers API is working correctly
"""

from config import config
from fyers_apiv3 import fyersModel
import json

def test_fyers_api():
    """Test Fyers API connection and responses"""
    
    print("🧪 Testing Fyers API Connection")
    print("=" * 40)
    
    # Print configuration
    print(f"📋 Configuration:")
    print(f"   Client ID: {config.CLIENT_ID}")
    print(f"   Secret ID: {config.SECRET_ID[:8]}...")
    print(f"   Redirect URI: {config.REDIRECT_URI}")
    print(f"   Token: {config.fyers_token[:50] if config.fyers_token else 'None'}...")
    print()
    
    if not config.fyers_token:
        print("❌ No Fyers token found!")
        print("   Run: python get_new_token.py")
        return
    
    # Create Fyers client
    try:
        fyers = fyersModel.FyersModel(
            client_id=config.CLIENT_ID,
            token=config.fyers_token,
            is_async=False,
            log_path=""
        )
        print("✅ Fyers client created successfully")
    except Exception as e:
        print(f"❌ Failed to create Fyers client: {e}")
        return
    
    # Test 1: Get BankNifty spot price
    print("\n🧪 Test 1: BankNifty Spot Price")
    try:
        response = fyers.quotes({"symbols": "NSE:NIFTYBANK-INDEX"})
        print(f"   Raw response: {json.dumps(response, indent=2)}")
        
        if response and response.get("s") == "ok" and "d" in response and response["d"]:
            spot_price = response["d"][0]["v"]["lp"]
            print(f"   ✅ BankNifty Spot: {spot_price}")
        else:
            print(f"   ❌ Invalid response format")
            print(f"   Response keys: {list(response.keys()) if response else 'None'}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Get BankNifty futures price
    print("\n🧪 Test 2: BankNifty Futures Price")
    try:
        from futures_config import get_current_futures_symbol
        futures_symbol = get_current_futures_symbol()
        print(f"   Futures symbol: {futures_symbol}")
        
        response = fyers.quotes({"symbols": futures_symbol})
        print(f"   Raw response: {json.dumps(response, indent=2)}")
        
        if response and response.get("s") == "ok" and "d" in response and response["d"]:
            futures_price = response["d"][0]["v"]["lp"]
            print(f"   ✅ BankNifty Futures: {futures_price}")
        else:
            print(f"   ❌ Invalid response format")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get option chain sample
    print("\n🧪 Test 3: Option Chain Sample")
    try:
        response = fyers.optionchain(data={
            "symbol": "NSE:NIFTYBANK-INDEX",
            "strikecount": 1
        })
        print(f"   Raw response keys: {list(response.keys()) if response else 'None'}")
        print(f"   Status: {response.get('s') if response else 'None'}")
        
        if response and response.get("s") == "ok":
            print(f"   ✅ Option chain API working")
            if "data" in response:
                data = response["data"]
                print(f"   Data keys: {list(data.keys()) if data else 'None'}")
                if "expiryData" in data:
                    expiries = data["expiryData"]
                    print(f"   ✅ Found {len(expiries)} expiries")
                    for i, exp in enumerate(expiries[:2]):
                        print(f"      Expiry {i+1}: {exp.get('date', 'Unknown')}")
        else:
            print(f"   ❌ Option chain failed: {response.get('message') if response else 'No response'}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Test completed!")

if __name__ == "__main__":
    test_fyers_api()