# Example configuration file
# Copy this to config.py and add your actual tokens

import os

# Fyers API Token (from token.txt or environment variable)
FYERS_TOKEN = None  # Will be loaded from token.txt

# GitHub Token (can be set as environment variable)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', None)

# Alternative: Load from token.txt
def load_tokens():
    """Load tokens from token.txt file"""
    try:
        with open('token.txt', 'r') as f:
            lines = f.readlines()
            
        fyers_token = lines[0].strip() if len(lines) > 0 else None
        
        # Look for github_token line
        github_token = None
        for line in lines:
            if line.startswith('github_token='):
                github_token = line.split('=', 1)[1].strip()
                break
                
        return fyers_token, github_token
    except FileNotFoundError:
        print("token.txt not found. Please create it with your tokens.")
        return None, None

# Load tokens
FYERS_TOKEN, GITHUB_TOKEN = load_tokens()