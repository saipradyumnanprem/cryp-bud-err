from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=256, blank=True)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    address = models.CharField(max_length=256, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    aadhaar = models.CharField(max_length=15, blank=True)
    pan = models.CharField(max_length=15, blank=True)
    tax_slab = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.CharField(max_length=30)
    api_key = models.CharField(max_length=256)
    secret_key = models.CharField(max_length=256)

    def __str__(self):
        return self.exchange
