#!/usr/bin/env python3
"""
Script to update Fyers app configuration
Run this to fix the "invalid appId" error
"""

import os

def update_fyers_config():
    """Update Fyers app configuration"""
    
    print("🔧 Fyers App Configuration Updater")
    print("=" * 40)
    print()
    print("📋 You need to get these details from Fyers Developer Portal:")
    print("   🌐 https://myapi.fyers.in/")
    print("   📁 Go to 'My Apps' section")
    print()
    
    # Get current values
    current_client_id = "XA46287-100"
    current_secret = "your_secret_key_here"
    current_redirect = "https://trade.fyers.in/api-login/redirect-to-app"
    
    print(f"📊 Current Configuration:")
    print(f"   Client ID: {current_client_id}")
    print(f"   Secret: {current_secret}")
    print(f"   Redirect URI: {current_redirect}")
    print()
    
    # Get new values
    print("🔑 Enter your correct Fyers app details:")
    print()
    
    new_client_id = input("📱 App ID (Client ID): ").strip()
    if not new_client_id:
        print("❌ Client ID is required!")
        return
    
    new_secret = input("🔐 Secret Key: ").strip()
    if not new_secret:
        print("❌ Secret Key is required!")
        return
    
    new_redirect = input(f"🔗 Redirect URI [{current_redirect}]: ").strip()
    if not new_redirect:
        new_redirect = current_redirect
    
    print()
    print("📝 New Configuration:")
    print(f"   Client ID: {new_client_id}")
    print(f"   Secret: {new_secret}")
    print(f"   Redirect URI: {new_redirect}")
    print()
    
    confirm = input("✅ Update configuration? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Configuration update cancelled.")
        return
    
    # Update config.py file
    try:
        # Read current config.py
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Replace the values
        content = content.replace(
            "self.CLIENT_ID = os.getenv('FYERS_CLIENT_ID', 'XA46287-100')",
            f"self.CLIENT_ID = os.getenv('FYERS_CLIENT_ID', '{new_client_id}')"
        )
        content = content.replace(
            "self.SECRET_ID = os.getenv('FYERS_SECRET_ID', 'your_secret_key_here')",
            f"self.SECRET_ID = os.getenv('FYERS_SECRET_ID', '{new_secret}')"
        )
        content = content.replace(
            f"self.REDIRECT_URI = os.getenv('FYERS_REDIRECT_URI', '{current_redirect}')",
            f"self.REDIRECT_URI = os.getenv('FYERS_REDIRECT_URI', '{new_redirect}')"
        )
        
        # Write updated config.py
        with open('config.py', 'w') as f:
            f.write(content)
        
        print("✅ Configuration updated successfully!")
        print()
        print("📋 Next Steps:")
        print("1. 🧪 Test locally: python get_new_token.py")
        print("2. 📤 Push to Git: git add config.py && git commit -m \"Update Fyers config\" && git push")
        print("3. 🌐 Update Render environment variables:")
        print(f"   - FYERS_CLIENT_ID: {new_client_id}")
        print(f"   - FYERS_SECRET_ID: {new_secret}")
        print(f"   - FYERS_REDIRECT_URI: {new_redirect}")
        print()
        print("🎯 After updating Render env vars, your app will restart automatically!")
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")

if __name__ == "__main__":
    update_fyers_config()