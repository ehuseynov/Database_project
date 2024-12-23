from django.shortcuts import render, redirect
from app.db import execute_query, execute_insert_or_update

def profile_view(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    if request.method == 'POST':
        # Distinguish between editing profile, adding/removing favorite stock, or adding/removing favorite currency
        if 'update_profile' in request.POST:
            # User is submitting updated info
            name = request.POST.get('name')
            mail = request.POST.get('mail')
            new_password = request.POST.get('password')

            if new_password and new_password.strip():
                update_sql = """
                    UPDATE users
                    SET name = %s,
                        mail = %s,
                        password = %s,
                        updated_at = NOW()
                    WHERE user_id = %s
                """
                execute_insert_or_update(update_sql, [name, mail, new_password, user_id])
            else:
                update_sql = """
                    UPDATE users
                    SET name = %s,
                        mail = %s,
                        updated_at = NOW()
                    WHERE user_id = %s
                """
                execute_insert_or_update(update_sql, [name, mail, user_id])

            return redirect('profile')

        elif 'add_favorite_stock' in request.POST:
            stock_id = request.POST.get('stock_id')
            # Check if already in favorites
            existing_fav_sql = """
                SELECT favorite_id
                FROM favorites
                WHERE user_id = %s AND stock_id = %s
            """
            existing_fav = execute_query(existing_fav_sql, [user_id, stock_id], fetchone=True)

            if not existing_fav:
                insert_fav_sql = """
                    INSERT INTO favorites (user_id, stock_id) 
                    VALUES (%s, %s)
                """
                execute_insert_or_update(insert_fav_sql, [user_id, stock_id])

            return redirect('profile')

        elif 'remove_favorite_stock' in request.POST:
            fav_stock_id = request.POST.get('remove_stock_id')
            # Delete from favorites
            delete_fav_sql = """
                DELETE FROM favorites
                WHERE user_id = %s AND stock_id = %s
            """
            execute_insert_or_update(delete_fav_sql, [user_id, fav_stock_id])
            return redirect('profile')

        elif 'add_favorite_currency' in request.POST:
            currency_code = request.POST.get('currency_code')

            # Check if already in favorites
            exist_cur_sql = """
                SELECT favorite_currency_id
                FROM favorite_currency
                WHERE user_id = %s AND currency_code = %s
            """
            exist_cur = execute_query(exist_cur_sql, [user_id, currency_code], fetchone=True)

            if not exist_cur:
                insert_cur_sql = """
                    INSERT INTO favorite_currency (user_id, currency_code)
                    VALUES (%s, %s)
                """
                execute_insert_or_update(insert_cur_sql, [user_id, currency_code])

            return redirect('profile')

        elif 'remove_favorite_currency' in request.POST:
            fav_currency_code = request.POST.get('remove_currency_code')
            delete_cur_sql = """
                DELETE FROM favorite_currency
                WHERE user_id = %s AND currency_code = %s
            """
            execute_insert_or_update(delete_cur_sql, [user_id, fav_currency_code])
            return redirect('profile')

    # If GET, fetch user info and favorites
    user_sql = "SELECT user_id, username, name, mail FROM users WHERE user_id = %s"
    user_row = execute_query(user_sql, [user_id], fetchone=True)
    user_data = {
        'user_id': user_row[0],
        'username': user_row[1],
        'name': user_row[2],
        'mail': user_row[3]
    }

    # Favorite Stocks
    favorites_sql = """
        SELECT s.stock_id, s.symbol, s.name
        FROM favorites f
        JOIN stocks s ON f.stock_id = s.stock_id
        WHERE f.user_id = %s
    """
    favorite_stocks = execute_query(favorites_sql, [user_id], fetchall=True)

    # All Stocks (for adding favorites)
    all_stocks_sql = "SELECT stock_id, symbol, name FROM stocks"
    all_stocks = execute_query(all_stocks_sql, fetchall=True)

    # Favorite Currencies
    fav_cur_sql = """
        SELECT c.currency_code, c.currency_name, c.buy_rate, c.sell_rate
        FROM favorite_currency fc
        JOIN currency c ON fc.currency_code = c.currency_code
        WHERE fc.user_id = %s
    """
    favorite_currencies = execute_query(fav_cur_sql, [user_id], fetchall=True)

    # All Currencies (for adding new favorites)
    all_cur_sql = "SELECT currency_code, currency_name FROM currency"
    all_currencies = execute_query(all_cur_sql, fetchall=True)

    context = {
        'user': user_data,

        # Stocks
        'favorites': favorite_stocks,
        'all_stocks': all_stocks,

        # Currencies
        'favorite_currencies': favorite_currencies,
        'all_currencies': all_currencies,
    }

    return render(request, 'profile.html', context)
