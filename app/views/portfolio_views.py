from django.shortcuts import render, redirect
from app.db import execute_query, execute_insert_or_update
from decimal import Decimal

def portfolio_view(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('login')
    user_id = request.session['user_id']

    if request.method == 'POST':
        if 'buy_stock' in request.POST:
            # BUY stock: symbol, quantity, buy_price
            stock_id_str = request.POST.get('stock_id')
            quantity_str = request.POST.get('quantity')
            buy_price_str = request.POST.get('buy_price')

            if stock_id_str and quantity_str and buy_price_str:
                stock_id_val = int(stock_id_str)
                quantity_val = int(quantity_str)
                # Use Decimal for consistent monetary calculations
                buy_price_val = Decimal(buy_price_str)

                # Check if user already has a portfolio
                existing_portfolio = execute_query(
                    "SELECT portfolio_id, stock_id, quantity, price FROM portfolio WHERE user_id=%s;",
                    [user_id],
                    fetchone=True
                )

                if existing_portfolio:
                    pid, stock_ids, quantities, prices = existing_portfolio
                    stock_ids = list(stock_ids)
                    quantities = list(quantities)
                    prices = list(prices)  # each is likely Decimal from DB

                    if stock_id_val in stock_ids:
                        # Already in portfolio -> merge
                        idx = stock_ids.index(stock_id_val)
                        old_qty = Decimal(quantities[idx])
                        old_price = Decimal(prices[idx])

                        # New total quantity
                        new_qty = old_qty + quantity_val

                        # Weighted average:
                        #   total_cost_old = old_qty * old_price
                        #   total_cost_new = quantity_val * buy_price_val
                        #   new_avg_price  = (total_cost_old + total_cost_new) / (old_qty + quantity_val)
                        total_cost_old = old_qty * old_price
                        total_cost_new = Decimal(quantity_val) * buy_price_val
                        new_price = (total_cost_old + total_cost_new) / new_qty

                        quantities[idx] = int(new_qty)              # store back as int (or keep decimal if you prefer)
                        prices[idx] = new_price
                    else:
                        # Append new details if stock not in portfolio yet
                        stock_ids.append(stock_id_val)
                        quantities.append(quantity_val)
                        prices.append(buy_price_val)

                    # Update the arrays
                    execute_insert_or_update(
                        "UPDATE portfolio SET stock_id=%s, quantity=%s, price=%s WHERE portfolio_id=%s;",
                        [stock_ids, quantities, prices, pid]
                    )
                else:
                    # Create a new portfolio row
                    insert_sql = """
                        INSERT INTO portfolio (user_id, stock_id, quantity, price)
                        VALUES (%s, ARRAY[%s], ARRAY[%s], ARRAY[%s])
                    """
                    execute_insert_or_update(
                        insert_sql,
                        [user_id, stock_id_val, quantity_val, buy_price_val]
                    )

            return redirect('portfolio')

        elif 'sell_stock' in request.POST:
            # SELL stock: symbol, quantity
            stock_id_str = request.POST.get('sell_stock_id')
            quantity_str = request.POST.get('sell_quantity')

            if stock_id_str and quantity_str:
                stock_id_val = int(stock_id_str)
                quantity_val = int(quantity_str)

                existing_portfolio = execute_query(
                    "SELECT portfolio_id, stock_id, quantity, price FROM portfolio WHERE user_id=%s;",
                    [user_id],
                    fetchone=True
                )
                if existing_portfolio:
                    pid, stock_ids, quantities, prices = existing_portfolio
                    stock_ids = list(stock_ids)
                    quantities = list(quantities)
                    prices = list(prices)

                    if stock_id_val in stock_ids:
                        idx = stock_ids.index(stock_id_val)
                        current_quantity = quantities[idx]

                        if quantity_val >= current_quantity:
                            # Remove the entire position
                            stock_ids.pop(idx)
                            quantities.pop(idx)
                            prices.pop(idx)
                        else:
                            # Partial sell -> reduce quantity
                            new_qty = current_quantity - quantity_val
                            quantities[idx] = new_qty

                        # Update or delete the row
                        if stock_ids:
                            execute_insert_or_update(
                                "UPDATE portfolio SET stock_id=%s, quantity=%s, price=%s WHERE portfolio_id=%s;",
                                [stock_ids, quantities, prices, pid]
                            )
                        else:
                            execute_insert_or_update(
                                "DELETE FROM portfolio WHERE portfolio_id=%s;",
                                [pid]
                            )
            return redirect('portfolio')

    # Retrieve portfolio
    portfolio_row = execute_query(
        "SELECT stock_id, quantity, price FROM portfolio WHERE user_id=%s;",
        [user_id],
        fetchone=True
    )

    portfolio_data = []
    total_cost = Decimal('0.0')
    total_value = Decimal('0.0')
    total_gain = Decimal('0.0')

    if portfolio_row:
        stock_ids, quantities, prices = portfolio_row
        for s, q, p in zip(stock_ids, quantities, prices):
            q_dec = Decimal(q)
            p_dec = Decimal(p)

            # current_price from stocks table
            stock_info = execute_query(
                "SELECT symbol, name, price FROM stocks WHERE stock_id=%s;",
                [s],
                fetchone=True
            )
            if stock_info:
                symbol, name, current_price = stock_info
                current_price_dec = Decimal(current_price)

                row_cost = q_dec * p_dec
                row_value = q_dec * current_price_dec
                row_gain = row_value - row_cost

                total_cost += row_cost
                total_value += row_value
                total_gain += row_gain

                portfolio_data.append({
                    'stock_id': s,
                    'symbol': symbol,
                    'name': name,
                    'quantity': q,
                    'bought_price': p,
                    'current_price': current_price,
                    'row_cost': row_cost,
                    'row_value': row_value,
                    'row_gain': row_gain,
                })

    # For the SELL dropdown, only show the stocks in the user’s portfolio
    # We'll gather the unique stock_ids from the portfolio:
    sellable_stocks = []
    if portfolio_row:
        stock_ids, quantities, prices = portfolio_row
        # fetch symbol for each stock_id
        # Alternatively, you can do a single SQL query using unnest, but let's do a simple approach:
        for s in stock_ids:
            info = execute_query(
                "SELECT stock_id, symbol FROM stocks WHERE stock_id=%s;",
                [s],
                fetchone=True
            )
            if info:
                sellable_stocks.append(info)

    # For the BUY dropdown, we can still show all stocks:
    all_stocks = execute_query("SELECT stock_id, symbol FROM stocks;", fetchall=True)

    return render(request, 'portfolio.html', {
        'portfolio_data': portfolio_data,
        'all_stocks': all_stocks,         # for Buy form
        'sellable_stocks': sellable_stocks,  # for Sell form
        'total_cost': total_cost,
        'total_value': total_value,
        'total_gain': total_gain
    })
