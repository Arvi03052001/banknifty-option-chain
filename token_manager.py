from fyers_apiv3 import fyersModel
import config
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(BASE_DIR, "token.txt")


def save_access_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_access_token():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError("Access token not found. Please authenticate first.")
    with open(TOKEN_FILE, "r") as f:
        return f.read().strip()

def generate_auth_url():
    session = fyersModel.SessionModel(
        client_id=config.CLIENT_ID,
        secret_key=config.SECRET_ID,
        redirect_uri=config.REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code"
    )
    return session.generate_authcode()

def exchange_code_for_token(auth_code):
    session = fyersModel.SessionModel(
        client_id=config.CLIENT_ID,
        secret_key=config.SECRET_ID,
        redirect_uri=config.REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code"
    )
    session.set_token(auth_code)
    response = session.generate_token()
    access_token = response.get("access_token")
    if access_token:
        save_access_token(access_token)
    return response

def get_fyers_client():
    access_token = load_access_token()
    fyers = fyersModel.FyersModel(
        client_id=config.CLIENT_ID,
        token=access_token,
        log_path="./"
    )
    return fyers

def read_token():
    try:
        with open("token.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("token.txt not found. Please login first.")
        return None

def validate_token():
    token = read_token()
    if not token:
        print("[✖] No token found.")
        return

    fy = fyersModel.FyersModel(client_id=config.CLIENT_ID, token=token, log_path="")
    res = fy.quotes({"symbols": "NSE:NIFTYBANK-INDEX"})
    print("[DEBUG] Token validation result:", res)



