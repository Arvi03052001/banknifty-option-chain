#!/usr/bin/env python3
"""
Test script for futures_details route to verify error fixes
"""

import sys
import os
from datetime import date, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_futures_details_route():
    """Test the futures_details route with different scenarios"""
    try:
        from web_app import app
        
        print("=" * 60)
        print("TESTING FUTURES DETAILS ROUTE")
        print("=" * 60)
        
        with app.test_client() as client:
            # Test 1: Today's date (might be holiday)
            print("\n1. Testing today's date:")
            response = client.get('/futures-details')
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Route accessible")
            else:
                print("   ❌ Route failed")
                return False
            
            # Test 2: Yesterday's date
            yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"\n2. Testing yesterday's date ({yesterday}):")
            response = client.get(f'/futures-details?date={yesterday}')
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Date parameter working")
            else:
                print("   ❌ Date parameter failed")
                return False
            
            # Test 3: A week ago
            week_ago = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
            print(f"\n3. Testing week ago date ({week_ago}):")
            response = client.get(f'/futures-details?date={week_ago}')
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Week ago date working")
            else:
                print("   ❌ Week ago date failed")
                return False
            
            # Test 4: Invalid date format
            print(f"\n4. Testing invalid date format:")
            response = client.get(f'/futures-details?date=invalid-date')
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Invalid date handled gracefully")
            else:
                print("   ❌ Invalid date not handled")
                return False
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - FUTURES DETAILS ROUTE IS WORKING")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_futures_details_route()
    
    if success:
        print("\n🎉 Futures details route is ready!")
        print("💡 You can now:")
        print("   - Visit /futures-details in your web browser")
        print("   - Select any date using the date picker")
        print("   - View historical futures data")
        print("   - Use quick date buttons for easy navigation")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)