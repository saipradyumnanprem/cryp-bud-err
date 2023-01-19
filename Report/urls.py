from django.urls import path
from . import views

urlpatterns = [
    #path('', views.home,name='home'),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('temp/', views.temp,name='temp'),
    path('wallet/', views.wallet,name='wallet'),
    path('tax/', views.tax,name='tax'),
    path('news/', views.news,name='news'),
    path('history/<str:coin_name>/', views.history,name='history'),
    path('coins/', views.list_of_coins,name='list_of_coins'),
    path('balances/', views.balances,name='balances'),
    path('test/',views.test,name="test"),
    #path('price/', views.price,name='price'),
    path('marketcap/', views.marketCap,name='marketcap'),
    path('exchanges/', views.exchanges,name='exchanges'),
    path('best-cryptos/', views.bestCryptos,name='best-cryptos'),
    path('crypto-news/', views.crypto_news,name='crypto-news'),
    path('price-recommend/', views.price_recommend,name='price_recommend'),
]
