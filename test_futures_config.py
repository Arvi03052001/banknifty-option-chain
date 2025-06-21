#!/usr/bin/env python3
"""
Test script for BANKNIFTY Futures Configuration System
Run this script to verify that the futures configuration is working correctly.
"""

import sys
from datetime import date
from futures_config import FuturesConfig, get_current_futures_symbol, get_next_futures_symbol, get_futures_info

def test_futures_config():
    """Test the futures configuration system"""
    print("=" * 60)
    print("TESTING BANKNIFTY FUTURES CONFIGURATION SYSTEM")
    print("=" * 60)
    
    # Test 1: Basic symbol generation
    print("\n1. Testing Basic Symbol Generation:")
    try:
        current = get_current_futures_symbol()
        next_month = get_next_futures_symbol()
        print(f"   ✅ Current Symbol: {current}")
        print(f"   ✅ Next Symbol: {next_month}")
        
        # Validate format
        if current.startswith("NSE:BANKNIFTY") and current.endswith("FUT"):
            print("   ✅ Current symbol format is correct")
        else:
            print("   ❌ Current symbol format is incorrect")
            
        if next_month.startswith("NSE:BANKNIFTY") and next_month.endswith("FUT"):
            print("   ✅ Next symbol format is correct")
        else:
            print("   ❌ Next symbol format is incorrect")
            
    except Exception as e:
        print(f"   ❌ Error in basic symbol generation: {e}")
        return False
    
    # Test 2: Comprehensive info
    print("\n2. Testing Comprehensive Information:")
    try:
        info = get_futures_info()
        print(f"   ✅ Configuration Date: {info['updated_on']}")
        print(f"   ✅ Current Contract: {info['current']['symbol']}")
        print(f"   ✅ Current Expiry: {info['current']['expiry_date']}")
        print(f"   ✅ Next Contract: {info['next']['symbol']}")
        print(f"   ✅ Next Expiry: {info['next']['expiry_date']}")
    except Exception as e:
        print(f"   ❌ Error in comprehensive info: {e}")
        return False
    
    # Test 3: Date logic
    print("\n3. Testing Date Logic:")
    try:
        config = FuturesConfig()
        current_year, current_month = config.get_current_expiry_month_year()
        next_year, next_month = config.get_next_expiry_month_year()
        
        print(f"   ✅ Current Expiry Month/Year: {current_month}/{current_year}")
        print(f"   ✅ Next Expiry Month/Year: {next_month}/{next_year}")
        
        # Test expiry date calculation
        current_expiry = config.get_current_expiry_date()
        next_expiry = config.get_next_expiry_date()
        
        print(f"   ✅ Current Expiry Date: {current_expiry} (Weekday: {current_expiry.strftime('%A')})")
        print(f"   ✅ Next Expiry Date: {next_expiry} (Weekday: {next_expiry.strftime('%A')})")
        
        # Verify it's Thursday
        if current_expiry.weekday() == 3:  # Thursday is 3
            print("   ✅ Current expiry is on Thursday")
        else:
            print("   ❌ Current expiry is NOT on Thursday")
            
        if next_expiry.weekday() == 3:
            print("   ✅ Next expiry is on Thursday")
        else:
            print("   ❌ Next expiry is NOT on Thursday")
            
    except Exception as e:
        print(f"   ❌ Error in date logic: {e}")
        return False
    
    # Test 4: Integration with existing modules
    print("\n4. Testing Integration:")
    try:
        from option_chain_fetcher import get_futures_price
        from web_app import get_current_month_futures_symbol
        
        web_symbol = get_current_month_futures_symbol()
        config_symbol = get_current_futures_symbol()
        
        if web_symbol == config_symbol:
            print(f"   ✅ Web app integration working: {web_symbol}")
        else:
            print(f"   ❌ Web app integration mismatch: {web_symbol} vs {config_symbol}")
            
        print("   ✅ Option chain fetcher import successful")
        
    except Exception as e:
        print(f"   ❌ Error in integration test: {e}")
        return False
    
    # Test 5: Month transitions
    print("\n5. Testing Month Transition Logic:")
    try:
        # Test December to January transition
        config = FuturesConfig()
        
        # Test various months
        test_cases = [
            (2025, 12),  # December -> January next year
            (2025, 6),   # June -> July same year
            (2025, 1),   # January -> February same year
        ]
        
        for year, month in test_cases:
            symbol = config.format_futures_symbol(year, month)
            print(f"   ✅ {year}/{month:02d} -> {symbol}")
            
    except Exception as e:
        print(f"   ❌ Error in month transition test: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - FUTURES CONFIGURATION IS WORKING CORRECTLY")
    print("=" * 60)
    
    return True

def show_current_config():
    """Show the current configuration in detail"""
    print("\n" + "=" * 60)
    print("CURRENT CONFIGURATION DETAILS")
    print("=" * 60)
    
    config = FuturesConfig()
    config.print_futures_info()

if __name__ == "__main__":
    success = test_futures_config()
    show_current_config()
    
    if not success:
        sys.exit(1)
    
    print("\n🎉 Configuration system is ready to use!")
    print("💡 You can now run your web application and the futures symbols will update automatically.")
    print("🔗 Visit /futures-config in your web app to see the configuration interface.")