from django.core.management.base import BaseCommand
from django.db import connection
import time
import requests
import json

class Command(BaseCommand):
    help = "Update stock prices from Akbank API every 30 seconds."

    def handle(self, *args, **options):
        while True:
            self.update_all_prices()
            time.sleep(30)

    def update_all_prices(self):
        symbols = self.get_stock_symbols()
        for sym in symbols:
            try:
                price = self.fetch_price(sym)
                if price is not None:
                    self.update_stock_price(sym, price)
                    self.stdout.write(f"Updated {sym} price to {price}")
            except Exception as e:
                self.stderr.write(f"Error updating {sym}: {e}")

    def get_stock_symbols(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT symbol FROM stocks;")
            rows = cursor.fetchall()
        # rows will be list of tuples [(symbol1,), (symbol2,), ...]
        return [row[0] for row in rows]


    def fetch_price(self, symbol):
        url = f"https://yatirim.akbank.com/_vti_bin/AkbankYatirimciPortali/Hisse/Service.svc/AlSat/{symbol}.E.BIST"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        #print(f"DEBUG: Fetched data for {symbol} => {data}")

        # 'Data' is a JSON string like:
        # '[{"c":"AGHOL.E.BIST","last":10.71,"ask":10.71,"previousDayClose":10.7,"bid":10.7}]'
        raw_json_str = data.get("Data")
        if not raw_json_str:
            # If "Data" key is missing or empty, skip
            return None

        # Parse the inner JSON string
        parsed_list = json.loads(raw_json_str)
        # This should give you a list of dicts like:
        # [{"c": "AGHOL.E.BIST", "last": 10.71, "ask": 10.71, "previousDayClose": 10.7, "bid": 10.7}]

        if not parsed_list:
            return None

        # The "last" price should be here:
        price_info = parsed_list[0]
        price = price_info.get("last")
        #print(f"DEBUG: Extracted price for {symbol} => {price}")
        return price


    def update_stock_price(self, symbol, price):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE stocks SET price = %s WHERE symbol = %s",
                [price, symbol]
            )
