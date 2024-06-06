from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import datetime, timedelta
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/stock', methods=['GET'])
def stock():
    return render_template('stock.html')

@app.route('/result', methods=['POST'])
def result():
    tickerCode = request.form['stockSymbol']
    api_key = request.form['APIKey']
    from_date = datetime.now() - timedelta(days=7)
    to_date = datetime.now() - timedelta(days=1)
    url = f"https://api.polygon.io/v2/aggs/ticker/X:{tickerCode}USD/range/1/day/{from_date.strftime('%Y-%m-%d')}/{to_date.strftime('%Y-%m-%d')}?adjusted=true&sort=asc&apiKey={api_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        stockData = response.json()
        if "results" in stockData and len(stockData["results"]) > 0:
            latestStockPrice = stockData["results"][-1]
            closingStockPrice = latestStockPrice["c"]
            volume = int(latestStockPrice["v"])
            stockDate = datetime.fromtimestamp(float(latestStockPrice["t"]) / 1000.0)
            return render_template('stock_price.html', tCode=tickerCode,
                                   sPrice=f'USD {closingStockPrice:,.2f}',
                                   cVolume=f'{volume:,}', dTime=stockDate)
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

@app.route('/services', methods=['GET'])
def services():
    return render_template('services.html')

if __name__ == '__main__':
    app.run(debug=True)
