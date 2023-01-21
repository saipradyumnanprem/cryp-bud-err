from concurrent.futures import process
from django.http import HttpResponse
from django.shortcuts import render
from binance.spot import Spot
from binance.client import Client
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup
from sympy import round_two
from Report.models import listOfCoins
import json, requests
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


#from django.http import HttpResponse
# Create your views here.
API_KEY=os.environ['binance_api']
API_SECRET=os.environ['binance_secret']

client = Spot(API_KEY,API_SECRET)
#client.API_URL = 'https://testnet.binance.vision/api'
#def home(request):
#    return render(request ,"Report/index.html")

def dashboard(request):
    return render(request,"Report/dashboard.html")

def temp(request):
    return render(request,"Report/temp.html")

def wallet(request):
    return render(request,"Report/wallet.html")

def transactions(request):
    transactions_client=Client(API_KEY,API_SECRET)
    info = client.account_snapshot("SPOT")
    info=info["snapshotVos"][2]["data"]["balances"]
    transactions_data=[]
    for symbol in info:
        #try:
        try:
            transactions_data.append(transactions_client.get_my_trades(symbol=symbol["asset"]+"USDT"))
        except:
            try:
                transactions_data.append(transactions_client.get_my_trades(symbol=symbol["asset"]))
            except:
                continue
        for data in transactions_data[-1]:
            data['value']=float(data['qty'])*float(data['price'])
            data['buySell']="Buy" if(data['isBuyer']) else "Sell"
            try:
                data['time']=datetime.fromtimestamp(int(data['time'])/1000)
                data['time']=data['time'].strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue
            #data['time']=data['time'].strftime("%Y-%m-%d %H:%M:%S")
        #except:
        #    print(symbol['asset'])
    context={
        'transactions_data':transactions_data
    }
    return render(request,"Report/transactions.html",context)

def tax(request):
    return render(request,"Report/tax.html")

def news(request):
    return render(request,"Report/crypto_news.html")

def history(request,coin_name=None):
    candlesticks=client.klines(coin_name+"USDT","1m")
    #candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Aug, 2022", "3 Jul, 2022")
    processed_candlesticks = []

    for data in candlesticks:
        candlestick = { 
            "time": (data[0] / 1000)+19800, 
            "open": data[1],
            "high": data[2], 
            "low": data[3], 
            "close": data[4]
        }
        processed_candlesticks.append(candlestick)
    
    return JsonResponse(processed_candlesticks,safe=False)
    #return HttpResponse('<h1>Hello world</h1>')
def list_of_coins(request):
    info = client.account_snapshot("SPOT")
    info=info["snapshotVos"][2]["data"]["balances"]
    processed_info=[]
    for data in info:
        processed_info.append(data["asset"])
        #modelObject=listOfCoins(coinName=data["asset"],priceUSD=0.0)
        #modelObject.save()
    return JsonResponse(processed_info,safe=False)

def prices():
    processed_info=list(listOfCoins.objects.values())
    info=[]
    print(len(processed_info))
    for data in processed_info:
        try:
            price=client.ticker_price(data["coinName"]+"USDT")["price"]
            info.append({"coinName":data["coinName"],"price":price})
        except:
            try:
                price=client.ticker_price(data["coinName"])["price"]
                info.append({"coinName":data["coinName"],"price":price})
            except:
                #print(data["coinName"])
                continue
    return info

def test(request):
    test=Client(API_KEY,API_SECRET)
    trades = test.get_my_trades(symbol='BTCUSDT')
    return JsonResponse(trades,safe=False)
    
def balances(request):
    info = client.account_snapshot("SPOT")["snapshotVos"][-2]["data"]["balances"]
    processed_info=[]
    for i in range(0,len(info)):
        data=info[i]
        if(float(data["free"])>0):
            try:
                data["value"]=float(data["free"])*float(client.ticker_price(data["asset"]+"USDT")["price"])
            except:
                data["value"]=-1
            try:
                data["original_Price"]=float(client.my_trades(symbol=data["asset"]+"USDT")[0]["price"])
                data["original_Value"]=float(data["free"])*float(data["original_Price"])
                data["ROI"]=round(((data["value"]-data["original_Value"])/data["original_Value"])*100,2)
                
            except:
                data["original_Price"]=0
                data["original_Value"]=0
                data["ROI"]=round(((data["value"]-data["original_Value"]))*100,2)
            processed_info.append(data)
    return JsonResponse(processed_info,safe=False)


def marketCap(request):
    market_cap__url="https://coinmarketcap.com/"
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
    try:
        page=requests.get(market_cap__url,headers=header)
        doc = BeautifulSoup(page.content, 'html.parser')
        coin_list = doc.find_all('tr')
        coin_list=list(coin_list)
    except:
        coin_list=[]
    return JsonResponse(str(coin_list[:11]),safe=False)



def bestCryptos(request):
    market_cap__url="https://coinmarketcap.com/best-cryptos/"
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
    try:
        page=requests.get(market_cap__url,headers=header)
        doc = BeautifulSoup(page.content, 'html.parser')
        coin_list = doc.find_all('tr')
        coin_list=list(coin_list)
        list_of_coins=[]
        list_of_coins.append(str(coin_list[:6]))
        list_of_coins.append(str(coin_list[11:17]))
        list_of_coins.append(str(coin_list[22:28]))
    except:
        coin_list=[]
    return JsonResponse(list_of_coins,safe=False)

def exchanges(request):
    market_cap__url="https://coinmarketcap.com/rankings/exchanges/"
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
    try:
        page=requests.get(market_cap__url,headers=header)
        doc = BeautifulSoup(page.content, 'html.parser')
        coin_list = doc.find_all('tr')
        coin_list=list(coin_list)
    except:
        coin_list=[]
    return JsonResponse(str(coin_list[:11]),safe=False)


def crypto_news(request):
    crypto_news_url="https://economictimes.indiatimes.com/newslist/82519373.cms"
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
    try:
        page=requests.get(crypto_news_url,headers=header)
        doc = BeautifulSoup(page.content, 'html.parser')
        selection_class= "eachStory"
        news_list = doc.find_all('div',{'class':selection_class})
        #news_list=list(news_list)
    except:
        news_list=[]
    return JsonResponse(str(news_list),safe=False)

def price_recommend(request):

    base_url = "https://api.gemini.com/v1"
    info=prices()

    response = requests.get(base_url + "/symbols/details/BTCUSD")
    symbols = response.json()

    base_url = "https://api.gemini.com/v2"
    response = requests.get(base_url + "/ticker/btcusd")
    btc_data = response.json()
    print(btc_data["close"])
    return JsonResponse(btc_data,safe=False)

def tax_calculation(request):
    client=Client(API_KEY,API_SECRET)
    trades = client.get_my_trades(symbol='BTCUSDT')
    return JsonResponse(trades,safe=False)

def transactions_data(request):
    client=Client(API_KEY,API_SECRET)
    transactions_data = client.get_my_trades(symbol='BTCUSDT')
    return JsonResponse(transactions_data,safe=False)