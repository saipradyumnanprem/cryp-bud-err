from . import utils as ut
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
from django.views.generic import View
from django.template.loader import get_template
from django.http import FileResponse




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

def wallet(request):
    return render(request,"Report/wallet.html")


def gettrans():
    transactions_client=Client(API_KEY,API_SECRET)
    info = client.account_snapshot("SPOT")
    info=info["snapshotVos"][2]["data"]["balances"]
    transactions_data=[]
    for symbol in info:
        #try:
        try:
            transactions_data.append(sorted(transactions_client.get_my_trades(symbol=symbol["asset"]+"USDT"), key=lambda trade: trade['time'],reverse=True))
        except:
            try:
                transactions_data.append(sorted(transactions_client.get_my_trades(symbol=symbol["asset"]), key=lambda trade: trade['time'],reverse=True))
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
    return transactions_data

def transactions(request):

    transactions_data = gettrans()

    context = {
        'transactions_data': transactions_data
    }

    return render(request, "Report/transactions.html", context)


def tax(request):
    return render(request, "Report/tax.html")
def comparison(request):
    return render(request,"Report/price comparison.html")

class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        template = get_template('Report/taxreport.html')
        transactions_data = gettrans()

        context = {
            'transactions_data': transactions_data
        }

        html = template.render(context)
        pdf = ut.render_to_pdf('Report/taxreport.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" % ("12341231")
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

def tax_calculation():
    client=Client(API_KEY,API_SECRET)
    from datetime import datetime, timedelta

    trades = client.get_my_trades(symbol='BTCUSDT')

    # Initialize variables to keep track of capital gains and losses
    short_term_capital_gains = 0
    long_term_capital_gains = 0
    short_term_capital_losses = 0
    long_term_capital_losses = 0

    # Keep track of the purchase price and date of each coin
    purchase_prices = {}
    purchase_dates = {}

    # Define the cutoff for short-term vs long-term gains
    SHORT_TERM_CUTOFF = 365  # days

    for trade in trades:
        symbol = trade['symbol']
        qty = float(trade['qty'])
        price = float(trade['price'])
        is_buyer = trade['isBuyer']
        timestamp = trade['time']

        # If the trade is a buy, update the purchase price and date for the coin
        if is_buyer:
            purchase_prices[symbol] = price
            purchase_dates[symbol] = datetime.fromtimestamp(timestamp/1000)
        else:
            # If the trade is a sell, calculate the capital gain or loss
            purchase_price = purchase_prices.get(symbol, 0)
            purchase_date = purchase_dates.get(symbol, datetime.now())
            gain_loss = (price - purchase_price) * qty
            holding_period = (datetime.fromtimestamp(timestamp/1000) - purchase_date).days

            if holding_period <= SHORT_TERM_CUTOFF:
                if gain_loss > 0:
                    short_term_capital_gains += gain_loss
                else:
                    short_term_capital_losses += gain_loss
            else:
                if gain_loss > 0:
                    long_term_capital_gains += gain_loss
                else:
                    long_term_capital_losses += gain_loss
    total_tax=short_term_capital_gains+long_term_capital_gains
    capital=dict()
    capital["short_gains"]=short_term_capital_gains
    capital["long_gains"]=long_term_capital_gains
    capital["short_loss"]=short_term_capital_losses
    capital["long_loss"]=long_term_capital_losses
    capital["total_tax"]=total_tax
    return dict(capital)

def tax_report(request):
    transactions_data = gettrans()
    tax_data = tax_calculation()
    print(tax_data)
    context = {
        'transactions_data': transactions_data,
        'tax_data':tax_data
    }
    return render(request, "Report/tax_report.html",context)

def download_report(request):
    html = tax_report(request)
    response = HttpResponse(html, content_type='text/html')
    response['Content-Disposition'] = 'attachment; filename=Tax Report.html'
    return response

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
    test=Client(API_KEY,API_SECRET)
    binance_price = test.get_all_tickers()
    print(binance_price)
    
    #info=prices()

    response = requests.get(base_url + "/symbols/details/BTCUSD")
    #symbols = response.json()

    base_url = "https://api.gemini.com/v2"
    response = requests.get(base_url + "/ticker/btcusd")
    btc_data = response.json()
    print(btc_data)
    return JsonResponse(btc_data,safe=False)

def transactions_data(request):
    client=Client(API_KEY,API_SECRET)
    transactions_data = client.get_my_trades(symbol='BTCUSDT')
    transactions_data = sorted(transactions_data, key=lambda trade: trade['time'],reverse=True)
    return JsonResponse(transactions_data,safe=False)

def coinbase_price(request):
    url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    # Make a GET request to the API endpoint
    response = requests.get(url)
    # Get the JSON data from the response
    data = response.json()
    # Get the current price of Bitcoin in USD
    price = data['data']['amount']
    return JsonResponse(data,safe=False)