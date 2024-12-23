Before starting run to create required tables and insert some data:
	psql -U user -d database -p 5432 -h localhost -f app/sql/schema.sql      


To run server these commands should run simultaneusly:
	python manage.py update_currencies
	python manage.py update_prices
	python manage.py runserver  

Moreover, do not forget to edit database from stockviewer/settings.py