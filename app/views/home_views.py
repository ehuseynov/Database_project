from django.shortcuts import render
from app.db import execute_query

def home_view(request):
    # Fetch top 5 stocks from the database (by largest market value)
    stocks = execute_query("""
        SELECT symbol, name, price 
        FROM stocks
        ORDER BY (number_of_shares * price) DESC
        LIMIT 5;
    """, fetchall=True)
    
    # If the user is logged in, fetch the user's favorite stocks and favorite currencies
    favorites_stocks = []
    favorite_currencies = []
    if 'user_id' in request.session:
        user_id = request.session['user_id']

        # Favorite Stocks
        favorites_sql = """
            SELECT s.symbol, s.name, s.price
            FROM favorites f
            JOIN stocks s ON f.stock_id = s.stock_id
            WHERE f.user_id = %s
        """
        favorites_stocks = execute_query(favorites_sql, [user_id], fetchall=True)

        # Favorite Currencies
        fav_currencies_sql = """
            SELECT c.currency_code, c.currency_name, c.buy_rate, c.sell_rate
            FROM favorite_currency fc
            JOIN currency c ON fc.currency_code = c.currency_code
            WHERE fc.user_id = %s
        """
        favorite_currencies = execute_query(fav_currencies_sql, [user_id], fetchall=True)

    return render(request, 'home.html', {
        'stocks': stocks,
        'favorites': favorites_stocks,        # favorite stocks
        'favorite_currencies': favorite_currencies
    })
