#!/usr/bin/env python3
"""
Script to generate a new Fyers access token
Run this locally when your token expires
"""

from token_manager import generate_auth_url, exchange_code_for_token, validate_token
import webbrowser

def get_new_fyers_token():
    """Interactive script to get new Fyers token"""
    
    print("🔑 Fyers Token Generator")
    print("=" * 40)
    
    # Step 1: Generate auth URL
    print("\n📋 Step 1: Generate Authorization URL")
    try:
        auth_url = generate_auth_url()
        print(f"✅ Authorization URL generated:")
        print(f"🔗 {auth_url}")
        
        # Try to open in browser
        try:
            webbrowser.open(auth_url)
            print("🌐 Opening URL in your default browser...")
        except:
            print("⚠️ Could not open browser automatically. Please copy the URL above.")
        
    except Exception as e:
        print(f"❌ Error generating auth URL: {e}")
        return
    
    # Step 2: Get authorization code
    print("\n📋 Step 2: Get Authorization Code")
    print("1. Login to Fyers in the opened browser")
    print("2. Authorize the application")
    print("3. Copy the authorization code from the redirect URL")
    print("   (Look for 'auth_code=' in the URL)")
    
    auth_code = input("\n🔑 Enter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided. Exiting.")
        return
    
    # Step 3: Exchange code for token
    print("\n📋 Step 3: Exchange Code for Access Token")
    try:
        response = exchange_code_for_token(auth_code)
        
        if response.get("s") == "ok":
            access_token = response.get("access_token")
            print("✅ Token generated successfully!")
            print(f"🎫 Access Token: {access_token}")
            
            # Save to token.txt
            with open("token.txt", "w") as f:
                # Read existing content to preserve GitHub token
                try:
                    with open("token.txt", "r") as rf:
                        existing_content = rf.read()
                        if "github_token=" in existing_content:
                            # Extract GitHub token line
                            lines = existing_content.split('\n')
                            github_line = [line for line in lines if line.startswith('github_token=')]
                            if github_line:
                                f.write(f"{access_token}\n\n{github_line[0]}")
                            else:
                                f.write(access_token)
                        else:
                            f.write(access_token)
                except:
                    f.write(access_token)
            
            print("💾 Token saved to token.txt")
            
            # Step 4: Validate token
            print("\n📋 Step 4: Validate Token")
            validate_token()
            
        else:
            print(f"❌ Error getting token: {response}")
            
    except Exception as e:
        print(f"❌ Error exchanging code for token: {e}")

if __name__ == "__main__":
    get_new_fyers_token()