from token_manager import generate_auth_url, exchange_code_for_token
from data_fetcher import get_profile, get_market_data
from option_chain_fetcher import run_option_chain
from token_manager import validate_token
from token_manager import exchange_code_for_token, save_access_token
validate_token()

# STEP 1: Only once – login and get token
def login_flow():
    url = generate_auth_url()
    print("\nLogin to Fyers using this URL:")
    print(url)

    # Assume this happens after login step and auth_code is received
    auth_code = input("Paste auth code: ")
    response = exchange_code_for_token(auth_code)

    if response.get("access_token"):
        access_token = response["access_token"]
        print("[✔] Token generated and saved.")
        print("[DEBUG] Token used in main.py:", access_token)
    else:
        print("[✖] Failed to get access token:", response)

# STEP 2: Use token to fetch data
def run_data():
    print("\n1. Get Profile + Futures LTP")
    print("2. Build BankNifty Option Chain")
    choice = input("Choose (1/2): ").strip()
    
    if choice == "1":
        print("\n[✔] Profile:")
        print(get_profile())

        print("\n[✔] BankNifty Futures Price:")
        print(get_market_data("NSE:BANKNIFTY25JUNFUT"))

    elif choice == "2":
        run_option_chain()
        
if __name__ == "__main__":
    choice = input("\n1. Login to Fyers\n2. Fetch Data\nSelect (1/2): ").strip()
    if choice == "1":
        login_flow()
    else:
        run_data()



