from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

CRYPTOCOMPARE_API_KEY = 'ee67c75d1b8879116e9502f34d5b1339fb9a3ecbc5df053eb0bc831ef1ef94d5'
ALPHA_VANTAGE_API_KEY = 'WXU067FHBWX7OXQM'

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/stock', methods=['GET'])
def stock():
    return render_template('stock.html')

@app.route('/result', methods=['POST'])
def result():
    tickerCode = request.form['stockSymbol']
    polygon_api_key = request.form['APIKey']
    from_date = datetime.now() - timedelta(days=7)
    to_date = datetime.now() - timedelta(days=1)
    
    polygon_url = f"https://api.polygon.io/v2/aggs/ticker/X:{tickerCode}USD/range/1/day/{from_date.strftime('%Y-%m-%d')}/{to_date.strftime('%Y-%m-%d')}?adjusted=true&sort=asc&apiKey={polygon_api_key}"
    cryptocompare_url = f"https://data-api.cryptocompare.com/index/cc/v1/historical/days?market=cadli&instrument={tickerCode}-USD&limit=7&api_key={CRYPTOCOMPARE_API_KEY}"
    
    polygon_response = requests.get(polygon_url)
    cryptocompare_response = requests.get(cryptocompare_url)

    if polygon_response.status_code == 200 and cryptocompare_response.status_code == 200:
        stockDataPolygon = polygon_response.json()
        stockDataCryptoCompare = cryptocompare_response.json()
        
        if "results" in stockDataPolygon and len(stockDataPolygon["results"]) > 0 and "Data" in stockDataCryptoCompare and len(stockDataCryptoCompare["Data"]) > 0:
            latestStockPricePolygon = stockDataPolygon["results"][-1]
            closingStockPricePolygon = latestStockPricePolygon["c"]
            volumePolygon = int(latestStockPricePolygon["v"])
            stockDatePolygon = datetime.fromtimestamp(float(latestStockPricePolygon["t"]) / 1000.0)

            # Calculate stock change percentage from CryptoCompare data
            latestStockDataCryptoCompare = stockDataCryptoCompare["Data"][-1]
            closingStockPriceCryptoCompare = latestStockDataCryptoCompare["CLOSE"]
            openingStockPriceCryptoCompare = stockDataCryptoCompare["Data"][0]["OPEN"]
            volumeCryptoCompare = int(latestStockDataCryptoCompare["VOLUME"])
            stockDateCryptoCompare = datetime.fromtimestamp(float(latestStockDataCryptoCompare["TIMESTAMP"]))

            stockChangePercent = ((closingStockPriceCryptoCompare - openingStockPriceCryptoCompare) / openingStockPriceCryptoCompare) * 100
            
            return render_template('stock_price.html', tCode=tickerCode,
                                   sPrice=f'USD {closingStockPricePolygon:,.2f}',
                                   cVolume=f'{volumePolygon:,}', dTime=stockDatePolygon,
                                   stockData=stockDataCryptoCompare["Data"], apiKey=polygon_api_key,
                                   stockChangePercent=stockChangePercent)
        else:
            error = "No results found for the given cryptocurrency."
            return render_template('stock.html', error=error)
    else:
        error = "Error fetching data from API."
        return render_template('stock.html', error=error)

@app.route('/buy_crypto', methods=['GET', 'POST'])
def buy_crypto():
    if request.method == 'POST':
        crypto_symbol = request.form['cryptoSymbol']
        amount = float(request.form['amount'])
        api_key = request.form['APIKey']
        
        # Fetch the latest price using Polygon.io
        url = f"https://api.polygon.io/v2/aggs/ticker/X:{crypto_symbol}USD/range/1/day/2023-01-09/2023-01-09?adjusted=true&sort=asc&apiKey={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                latestPrice = data["results"][-1]["c"]
                total_cost = latestPrice * amount
                
                # Implement buying logic here (e.g., saving to a database, calling another API, etc.)
                
                return render_template('transaction_result.html', symbol=crypto_symbol, price=latestPrice, amount=amount, total=total_cost, action="bought")
            else:
                error = "No results found for the given cryptocurrency."
                return render_template('buy_crypto.html', error=error)
        else:
            error = "Error fetching data from API."
            return render_template('buy_crypto.html', error=error)
    return render_template('buy_crypto.html')

@app.route('/sell_crypto', methods=['GET', 'POST'])
def sell_crypto():
    if request.method == 'POST':
        crypto_symbol = request.form['cryptoSymbol']
        amount = float(request.form['amount'])
        api_key = request.form['APIKey']
        
        # Fetch the latest price using Polygon.io
        url = f"https://api.polygon.io/v2/aggs/ticker/X:{crypto_symbol}USD/range/1/day/2023-01-09/2023-01-09?adjusted=true&sort=asc&apiKey={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                latestPrice = data["results"][-1]["c"]
                total_value = latestPrice * amount
                
                # Implement selling logic here (e.g., saving to a database, calling another API, etc.)
                
                return render_template('transaction_result.html', symbol=crypto_symbol, price=latestPrice, amount=amount, total=total_value, action="sold")
            else:
                error = "No results found for the given cryptocurrency."
                return render_template('sell_crypto.html', error=error)
        else:
            error = "Error fetching data from API."
            return render_template('sell_crypto.html', error=error)
    return render_template('sell_crypto.html')

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'POST':
        from_currency = request.form['fromCurrency']
        to_currency = request.form['toCurrency']
        amount = float(request.form['amount'])
        
        url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "Realtime Currency Exchange Rate" in data:
                exchange_rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
                converted_amount = amount * exchange_rate
                return render_template('convert_result.html', from_currency=from_currency, to_currency=to_currency,
                                       amount=amount, converted_amount=converted_amount, exchange_rate=exchange_rate)
            else:
                error = "Error fetching exchange rate."
                return render_template('convert.html', error=error)
        else:
            error = "Error fetching data from API."
            return render_template('convert.html', error=error)
    return render_template('convert.html')


@app.route('/services', methods=['GET'])
def services():
    return render_template('services.html')

if __name__ == '__main__':
    app.run(debug=True)
