from django.core.management.base import BaseCommand
from core.models import Stock

class Command(BaseCommand):
    help = 'Load stocks from a text file and insert them into the database'

    def handle(self, *args, **options):
        file_path = 'core/data/symbols.txt'
        with open(file_path, 'r') as f:
            symbols = [line.strip() for line in f if line.strip()]

        for symbol in symbols:
            # Create the stock if not exists. Just symbol and name initially.
            # You may want to fetch the name from somewhere or default to symbol as name.
            Stock.objects.get_or_create(
                symbol=symbol,
                defaults={'name': symbol, 'price': 0.00, 'field_of_work': 'Unknown'}
            )

        self.stdout.write(self.style.SUCCESS("Stocks loaded successfully from symbols.txt"))