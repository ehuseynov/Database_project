from django.shortcuts import render, redirect
from app.db import execute_query, execute_insert_or_update

from django.shortcuts import render, redirect
from app.db import execute_query, execute_insert_or_update

def profile_view(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    if request.method == 'POST':
        # Distinguish between editing profile vs. adding a favorite
        if 'update_profile' in request.POST:
            # User is submitting updated info via the form
            name = request.POST.get('name')
            mail = request.POST.get('mail')
            new_password = request.POST.get('password')  # from the password field

            if new_password and new_password.strip():
                # Update name, mail, and password
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
                # Update name and mail only, leave password unchanged
                update_sql = """
                    UPDATE users
                    SET name = %s,
                        mail = %s,
                        updated_at = NOW()
                    WHERE user_id = %s
                """
                execute_insert_or_update(update_sql, [name, mail, user_id])

            # Redirect to the same page to avoid accidental re-submission
            return redirect('profile')

        elif 'add_favorite' in request.POST:
            # User wants to add a favorite stock
            stock_id = request.POST.get('stock_id')

            # Check if this favorite already exists
            existing_fav_sql = """
                SELECT favorite_id
                FROM favorites
                WHERE user_id = %s AND stock_id = %s
            """
            existing_fav = execute_query(existing_fav_sql, [user_id, stock_id], fetchone=True)

            if not existing_fav:
                # Insert new favorite
                insert_fav_sql = """
                    INSERT INTO favorites (user_id, stock_id)
                    VALUES (%s, %s)
                """
                execute_insert_or_update(insert_fav_sql, [user_id, stock_id])

            return redirect('profile')

    # If GET, just fetch user info for display
    user_sql = "SELECT user_id, username, name, mail FROM users WHERE user_id = %s"
    user_row = execute_query(user_sql, [user_id], fetchone=True)
    user_data = {
        'user_id': user_row[0],
        'username': user_row[1],
        'name': user_row[2],
        'mail': user_row[3]
    }

    # Fetch user’s favorite stocks
    favorites_sql = """
        SELECT s.stock_id, s.symbol, s.name
        FROM favorites f
        JOIN stocks s ON f.stock_id = s.stock_id
        WHERE f.user_id = %s
    """
    favorite_stocks = execute_query(favorites_sql, [user_id], fetchall=True)

    # Fetch all stocks to populate the dropdown
    all_stocks_sql = "SELECT stock_id, symbol, name FROM stocks"
    all_stocks = execute_query(all_stocks_sql, fetchall=True)

    context = {
        'user': user_data,
        'favorites': favorite_stocks,
        'all_stocks': all_stocks
    }

    return render(request, 'profile.html', context)
