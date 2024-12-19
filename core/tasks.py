import requests, json
from celery import shared_task
from core.models import Stock

@shared_task
def update_stock_prices():
    stocks = Stock.objects.all()
    for stock in stocks:
        url = f"https://yatirim.akbank.com/_vti_bin/AkbankYatirimciPortali/Hisse/Service.svc/AlSat/{stock.symbol}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()  # This gives you the outer JSON object

            # 'Data' is a string containing JSON. We need to parse it again.
            data_str = data.get('Data', None)
            if data_str:
                # Parse the inner JSON string
                inner_data = json.loads(data_str)  # This should be a list of dicts
                if inner_data and isinstance(inner_data, list):
                    # Assuming you want the 'last' field from the first record
                    new_price = inner_data[0].get('last', None)
                    if new_price is not None:
                        stock.price = new_price
                        stock.save()
                    else:
                        print(f"No 'last' price found for {stock.symbol} in data: {inner_data}")
                else:
                    print(f"Unexpected structure in Data for {stock.symbol}: {inner_data}")
            else:
                print(f"No Data field found for {stock.symbol}: {data}")

        except requests.RequestException as e:
            print(f"Failed to update {stock.symbol}: {e}")
