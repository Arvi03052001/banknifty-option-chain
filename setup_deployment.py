#!/usr/bin/env python3
"""
Setup script for BankNifty deployment
This script helps you configure GitHub token and test the setup
"""

import os
import sys
from github_storage import GitHubStorage

def setup_github_token():
    """Interactive setup for GitHub token"""
    print("🔧 GitHub Token Setup")
    print("=" * 50)
    
    print("\n1. Go to GitHub.com → Settings → Developer settings → Personal access tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Give it a name like 'BankNifty CSV Storage'")
    print("4. Select scope: 'repo' (Full control of private repositories)")
    print("5. Click 'Generate token' and copy it")
    
    token = input("\nPaste your GitHub token here: ").strip()
    
    if not token:
        print("❌ No token provided")
        return False
    
    # Read current token.txt
    try:
        with open('token.txt', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ token.txt file not found")
        return False
    
    # Update token.txt with GitHub token
    lines = content.split('\n')
    updated_lines = []
    token_added = False
    
    for line in lines:
        if line.startswith('# github_token='):
            updated_lines.append(f'github_token={token}')
            token_added = True
        else:
            updated_lines.append(line)
    
    if not token_added:
        updated_lines.append(f'\ngithub_token={token}')
    
    # Write back to file
    with open('token.txt', 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ GitHub token added to token.txt")
    return True

def test_github_connection():
    """Test GitHub connection"""
    print("\n🧪 Testing GitHub Connection")
    print("=" * 50)
    
    github = GitHubStorage()
    
    if not github.token:
        print("❌ No GitHub token found")
        return False
    
    print("✅ GitHub token loaded")
    
    # Test creating a repository
    repo_name = "banknifty-data-test"
    print(f"\n📁 Testing repository creation: {repo_name}")
    
    success, message = github.create_repository(repo_name, "Test repository for BankNifty data")
    
    if success:
        print(f"✅ {message}")
        
        # Test file upload
        print("\n📄 Testing file upload...")
        test_content = "timestamp,strike,call_oi,put_oi\n2024-01-01 09:15:00,50000,1000,2000\n"
        
        with open('test_upload.csv', 'w') as f:
            f.write(test_content)
        
        success, message = github.upload_csv_file('test_upload.csv', 'test/sample.csv')
        
        if success:
            print(f"✅ File upload successful: {message}")
        else:
            print(f"❌ File upload failed: {message}")
        
        # Clean up test file
        if os.path.exists('test_upload.csv'):
            os.remove('test_upload.csv')
        
    else:
        if "already exists" in message.lower():
            print(f"ℹ️ Repository already exists, that's fine!")
            github.set_repository(github.repo_owner or "your-username", repo_name)
        else:
            print(f"❌ Repository creation failed: {message}")
            return False
    
    return True

def check_deployment_files():
    """Check if all deployment files are present"""
    print("\n📋 Checking Deployment Files")
    print("=" * 50)
    
    required_files = [
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'start_services.py',
        'github_storage.py',
        'csv_backup_service.py',
        '.gitignore',
        'DEPLOYMENT_GUIDE.md'
    ]
    
    all_present = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_present = False
    
    return all_present

def main():
    """Main setup function"""
    print("🚀 BankNifty Deployment Setup")
    print("=" * 50)
    
    # Check deployment files
    if not check_deployment_files():
        print("\n❌ Some deployment files are missing!")
        print("Please run the deployment preparation script first.")
        return
    
    print("\n✅ All deployment files present")
    
    # Setup GitHub token
    print("\n" + "=" * 50)
    setup_choice = input("Do you want to setup GitHub token? (y/n): ").lower().strip()
    
    if setup_choice == 'y':
        if setup_github_token():
            # Test GitHub connection
            if test_github_connection():
                print("\n🎉 GitHub setup completed successfully!")
            else:
                print("\n❌ GitHub connection test failed")
        else:
            print("\n❌ GitHub token setup failed")
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Push your code to GitHub")
    print("2. Deploy on Render using the DEPLOYMENT_GUIDE.md")
    print("3. Your app will run 24/7 with automatic CSV backup!")
    print("\nFor detailed instructions, see DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()