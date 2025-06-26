#!/usr/bin/env python3
"""
Script to update token.txt with new Fyers token while preserving GitHub token
"""

def update_token_file():
    """Update token.txt with new Fyers token"""
    
    print("🔄 Token File Updater")
    print("=" * 30)
    
    # Get new Fyers token
    new_fyers_token = input("🎫 Enter new Fyers token: ").strip()
    
    if not new_fyers_token:
        print("❌ No token provided. Exiting.")
        return
    
    # Read existing token.txt to preserve GitHub token
    github_token_line = ""
    try:
        with open("token.txt", "r") as f:
            content = f.read()
            lines = content.split('\n')
            for line in lines:
                if line.startswith('github_token='):
                    github_token_line = line
                    break
    except FileNotFoundError:
        print("⚠️ token.txt not found. Creating new file.")
    
    # Write updated token.txt
    try:
        with open("token.txt", "w") as f:
            f.write(new_fyers_token)
            if github_token_line:
                f.write(f"\n\n# GitHub Token for CSV file storage\n{github_token_line}")
        
        print("✅ Token updated successfully!")
        print("📁 Updated token.txt file")
        
        if github_token_line:
            print("🔗 GitHub token preserved")
        
        print("\n📋 Next Steps:")
        print("1. Test the token locally: python -c \"from token_manager import validate_token; validate_token()\"")
        print("2. Commit and push: git add token.txt && git commit -m \"Update Fyers token\" && git push")
        print("3. Or update FYERS_TOKEN environment variable in Render dashboard")
        
    except Exception as e:
        print(f"❌ Error updating token file: {e}")

if __name__ == "__main__":
    update_token_file()