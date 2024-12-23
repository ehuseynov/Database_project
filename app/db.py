from django.db import connection

def execute_query(query, params=None, fetchone=False, fetchall=False):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()

def execute_insert_or_update(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
