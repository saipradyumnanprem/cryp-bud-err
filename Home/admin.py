from django.contrib import admin
from .models import Profile, Wallet

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'address',
                    'phone_number', 'aadhaar', 'pan', 'tax_slab')


admin.site.register(Profile, ProfileAdmin)


class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'exchange', 'api_key', 'secret_key')


admin.site.register(Wallet, WalletAdmin)
