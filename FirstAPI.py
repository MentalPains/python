from flask import Flask
import requests
import json

url = "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2024-05-06/2024-05-12?adjusted=true&sort=asc&apiKey=3ebtJqSgXiAu8qbMvFUF3IroIixrLSAt"

payload = {}
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

app = Flask(__name__)
@app.route("/")
def home():
    return response.text
