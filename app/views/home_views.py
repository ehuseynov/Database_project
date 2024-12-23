from django.shortcuts import render
from app.db import execute_query

def home_view(request):
    # Fetch top 5 stocks from the database
    # For simplicity, assume top 5 main stocks have IDs 1 to 5, or some criteria
    stocks = execute_query("SELECT symbol, name, price FROM stocks LIMIT 5;", fetchall=True)
    
    # Fetch currencies (e.g. USD, EUR)
    currencies = execute_query("SELECT currency_name, exchange_rate_to_turkish_lira FROM currency;", fetchall=True)

    # If the user is logged in, fetch the user's favorite stocks
    favorites = []
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        favorites_sql = """
            SELECT s.symbol, s.name, s.price
            FROM favorites f
            JOIN stocks s ON f.stock_id = s.stock_id
            WHERE f.user_id = %s
        """
        favorites = execute_query(favorites_sql, [user_id], fetchall=True)

    return render(request, 'home.html', {
        'stocks': stocks,
        'currencies': currencies,
        'favorites': favorites
    })
