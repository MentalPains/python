from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
import json  # Ensure this import is included

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/stock', methods=['GET'])
def stock():
    return render_template('stock.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    error = None
    data = None
    if request.method == "POST":
        tickerCode = request.form['stockSymbol']
        api_key = request.form['APIKey']
        from_date = datetime.now() - timedelta(days=7)  # 7 days ago
        to_date = datetime.now() - timedelta(days=1)   # 1 day ago
        url = "https://api.polygon.io/v2/aggs/ticker/" + tickerCode + "/range/1/day/" + from_date.strftime("%Y-%m-%d") + "/" + to_date.strftime("%Y-%m-%d") + "?apiKey=" + api_key

        payload = {}
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response)
        stockData = json.loads(response.text)
        resultsCount = int(stockData["resultsCount"])
        latestStockPrice = stockData["results"][resultsCount-1]
        closingStockPrice = latestStockPrice["c"]
        volume = int(latestStockPrice["v"])
        stockDate = datetime.fromtimestamp(float(latestStockPrice["t"])/1000.0)

    return render_template('stock_price.html',tCode=tickerCode,
            sPrice= 'USD (:0,.2f)'.format(closingStockPrice),
            cVolume='{:0,.0f}'.format(volume) ,dTime=stockDate)
    
    