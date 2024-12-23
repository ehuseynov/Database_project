import requests
from django.utils import timezone
from app.db import execute_query, execute_insert_or_update
import json
import time
from django.utils import timezone
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = "Continuously fetch currency data from doviz.com every 30s."

    def handle(self, *args, **options):
        update_currencies_forever()  # never returns


def update_currencies_forever():
    """
    Continuously fetch currency data from doviz.com (returns a dict),
    parse the fiat currencies under data['C'],
    and update/insert into the 'currency' table.
    Runs forever with 30-second breaks.
    """

    url = "https://www.doviz.com/api/v12/converterItems"
    headers = {
        "Cookie": "userID=7e662d49-fa27-4d0a-a176-a369aba8405b; ...",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": "Bearer afd77f7c5336ceaed0967dbea846d833977053f9f21bb72d92174ddda3933a03",
        "Origin": "https://kur.doviz.com",
        "Referer": "https://kur.doviz.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Te": "trailers"
    }

    while True:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()  # This is a dict with 'error' and 'data' keys
                if isinstance(data, dict) and "data" in data:
                    # For fiat currencies, the relevant keys are under data["C"]
                    # sometimes nested at data["data"]["C"]
                    # Let's handle that carefully:

                    # Check if 'data' -> 'C' exists
                    if "C" in data["data"]:
                        c_data = data["data"]["C"]  # c_data is a dict of { "USD": {...}, "EUR": {...}, ... }

                        if isinstance(c_data, dict):
                            _update_currency_table(c_data)
                        else:
                            print("c_data is not a dict.", c_data)
                    else:
                        print("No 'C' key under data['data']. Full data:", data)
                else:
                    print("Data is not the expected dictionary format:", data)
            else:
                print(f"Failed to fetch data, HTTP status: {response.status_code}")
        except Exception as e:
            print("Error fetching currencies:", e)

        # Sleep for 30 seconds, then repeat
        time.sleep(30)

def _update_currency_table(c_dict):
    """
    c_dict is a dictionary like:
      {
        "USD": {"key": "USD", "code": "USD", "buying": 35.2129, "selling": 35.2192, ...},
        "EUR": {"key": "EUR", "code": "EUR", "buying": 36.6935, "selling": 36.7815, ...},
        ...
      }

    We'll store each currency in the 'currency' table using raw SQL.
    """
    now = timezone.now()

    for currency_symbol, info in c_dict.items():
        # e.g. currency_symbol = "USD", info = { "key": "USD", "buying": 35.2129, ...}
        if not isinstance(info, dict):
            continue  # skip anything unexpected

        # 'code' may be "USD" or similar
        currency_code = info.get("code") or currency_symbol
        # 'text' might be "USD", or a localized name, use whichever you want
        currency_name = info.get("text") or currency_code

        buying_val = info.get("buying")
        selling_val = info.get("selling")

        # Convert to float if not None
        try:
            buy_rate = float(buying_val) if buying_val is not None else 0.0
            sell_rate = float(selling_val) if selling_val is not None else 0.0
        except ValueError:
            buy_rate = 0.0
            sell_rate = 0.0

        if currency_code:
            sql = """
            INSERT INTO currency (currency_code, currency_name, buy_rate, sell_rate, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (currency_code)
            DO UPDATE
               SET currency_name = EXCLUDED.currency_name,
                   buy_rate      = EXCLUDED.buy_rate,
                   sell_rate     = EXCLUDED.sell_rate,
                   updated_at    = EXCLUDED.updated_at;
            """

            params = [currency_code, currency_name, buy_rate, sell_rate, now]
            execute_insert_or_update(sql, params)

    print("Fiat currencies from data['C'] updated successfully!")
