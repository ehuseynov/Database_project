import requests
import time

def fetch_currency_data():
    # Example: Get USD and EUR to TRY
    # Replace with a real API endpoint and your API key
    response = requests.get("https://api.exchangerate.host/latest?base=TRY")
    data = response.json()
    # Extract needed currencies
    return {
        'USD': data['rates']['USD'],
        'EUR': data['rates']['EUR']
    }

def fetch_stock_data(symbols):
    # Example API (replace with Akbank’s or any real one you have):
    # Assume endpoint: https://api.akbank.com/stocks?symbols=...
    # This is a placeholder
    response = requests.get("https://api.example.com/stocks", params={"symbols": ",".join(symbols)})
    return response.json()  # assume returns a JSON with price, volume, etc.
