import requests
import json
import os
from pathlib import Path

# URL of your Django application
BASE_URL = 'http://localhost:8000'
TOKEN_URL = f'{BASE_URL}/api/token/'
REFRESH_URL = f'{BASE_URL}/api/token/refresh/'
API_URL = f'{BASE_URL}/api/threads/'

# Path to store the token file
TOKEN_FILE = Path.home() / '.termos_token'

def save_tokens(access_token, refresh_token):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'access': access_token, 'refresh': refresh_token}, f)

def load_tokens():
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None

def get_new_access_token(refresh_token):
    response = requests.post(REFRESH_URL, data={'refresh': refresh_token})
    if response.status_code == 200:
        tokens = response.json()
        save_tokens(tokens['access'], tokens.get('refresh', refresh_token))
        return tokens['access']
    return None

def ensure_auth():
    tokens = load_tokens()
    if not tokens:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        response = requests.post(TOKEN_URL, data={'username': username, 'password': password})
        if response.status_code == 200:
            tokens = response.json()
            save_tokens(tokens['access'], tokens['refresh'])
            print("Authentication successful!")
        else:
            print(f"Authentication failed. Status code: {response.status_code}")
            return None
    
    access_token = tokens['access']
    
    # Attempt to use the access token
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(API_URL, headers=headers)
    
    if response.status_code == 401:  # Token has expired
        print("Access token expired. Refreshing...")
        new_access_token = get_new_access_token(tokens['refresh'])
        if new_access_token:
            return new_access_token
        else:
            print("Refresh failed. Please log in again.")
            os.remove(TOKEN_FILE)
            return ensure_auth()
    
    return access_token

def get_authenticated_headers():
    access_token = ensure_auth()
    if not access_token:
        raise Exception("Authentication failed")
    return {'Authorization': f'Bearer {access_token}'}

def logout():
    if TOKEN_FILE.exists():
        os.remove(TOKEN_FILE)
        print("Logged out successfully. Tokens removed.")
    else:
        print("No active session found.")