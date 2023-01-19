from django.db import models

# Create your models here.
class listOfCoins(models.Model):
    coinName=models.CharField(max_length=150)
    priceUSD=models.DecimalField(max_digits=25,decimal_places=20)
