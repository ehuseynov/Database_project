from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    symbol = models.CharField(max_length=20, unique=True)  # Increased from 10 to 20
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    field_of_work = models.CharField(max_length=255, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    ipo_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_today = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_5_years_gain = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    last_52_weeks_high = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"



class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'stock')


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)  # referencing Stock
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    url = models.URLField()
    published_at = models.DateTimeField()
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True, blank=True) # referencing Stock
    source = models.CharField(max_length=255, blank=True, null=True)

class Currency(models.Model):
    currency_code = models.CharField(max_length=10, primary_key=True)
    currency_name = models.CharField(max_length=100)
    exchange_rate_to_usd = models.DecimalField(max_digits=10, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)

