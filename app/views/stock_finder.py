from django.shortcuts import render
from app.db import execute_query

def stock_finder_view(request):
    """
    Displays a form to filter stocks by field_of_work, min_value (calculated as price*number_of_shares),
    and shows sorting options. Demonstrates nested queries and raw SQL usage.
    """

    # 1) Fetch distinct field_of_work for the dropdown
    field_of_work_options = execute_query(
        "SELECT DISTINCT field_of_work FROM stocks WHERE field_of_work IS NOT NULL;",
        fetchall=True
    )
    # Convert to a list, e.g. ["Technology", "Finance", ...] (ignoring None)
    field_of_work_options = [row[0] for row in field_of_work_options if row[0]]

    # 2) Read filter/sort parameters from GET
    selected_field = request.GET.get('field_of_work')  # e.g. "Technology"
    min_value_str = request.GET.get('min_value')       # e.g. "5000000"
    sort_by = request.GET.get('sort_by')               # e.g. "value_of_company"
    order = request.GET.get('order')                   # e.g. "asc" or "desc"

    # 3) Build the SQL query with a **calculated column** for value_of_company
    #
    # We'll alias (price * number_of_shares) as `value_of_company`.
    # Also, for demonstration, we can still show a nested query in the WHERE
    # clause for the field_of_work condition.

    base_sql = """
        SELECT
            stock_id,
            symbol,
            name,
            field_of_work,
            price,
            number_of_shares,
            last_5_years_gain,
            last_52_weeks_high,
            (price * number_of_shares) AS value_of_company
        FROM stocks
        WHERE 1=1
    """

    # We'll store extra conditions in a list
    conditions = []
    params = []

    # 4) Filter by field_of_work if provided
    if selected_field and selected_field.strip():
        conditions.append("""
            field_of_work = (
                SELECT field_of_work
                FROM stocks
                WHERE field_of_work = %s
                LIMIT 1
            )
        """)
        params.append(selected_field.strip())

    # 5) Filter by min_value (which is price * number_of_shares)
    if min_value_str and min_value_str.strip():
        try:
            min_value = float(min_value_str)
            conditions.append("(price * number_of_shares) >= %s")
            params.append(min_value)
        except ValueError:
            pass  # ignore or handle invalid numeric input

    # Combine the conditions
    if conditions:
        base_sql += " AND " + " AND ".join(conditions)

    # 6) Sorting
    # Valid columns to sort by could include:
    # - value_of_company (our calculated alias)
    # - last_5_years_gain
    # - last_52_weeks_high
    valid_sort_columns = ['value_of_company', 'last_5_years_gain', 'last_52_weeks_high']

    if sort_by in valid_sort_columns:
        sort_order = "ASC"
        if order and order.lower() == 'desc':
            sort_order = "DESC"
        base_sql += f" ORDER BY {sort_by} {sort_order}"

    # 7) Execute the final SQL
    stocks = execute_query(base_sql, params, fetchall=True)
    # 'stocks' is now a list of tuples like:
    # (stock_id, symbol, name, field_of_work, price, number_of_shares, last_5_years_gain,
    #  last_52_weeks_high, value_of_company)

    context = {
        'field_of_work_options': field_of_work_options,
        'stocks': stocks,
        'selected_field': selected_field or "",
        'min_value': min_value_str or "",
        'sort_by': sort_by or "",
        'order': order or "",
    }

    return render(request, 'stock_finder.html', context)
