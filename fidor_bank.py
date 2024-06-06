from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from requests.auth import HTTPBasicAuth
import requests
import json

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = '5ede13d54bc4c709c1c88725ab64dbbc'

# client_id and client_secret details are from the FIDOR portal.
client_id = "b34bfbe882e5edda"
client_secret = "5ede13d54bc4c709c1c88725ab64dbbc"

authorization_base_url = 'https://apm.tp.sandbox.fidorfzco.com/oauth/authorize'
token_url = 'https://apm.tp.sandbox.fidorfzco.com/oauth/token'
redirect_url = 'http://localhost:5000/callback'

@app.route('/', methods=["GET"])
@app.route('/index', methods=["GET"])
def default():
    try:
        # Step 1: User Application Authorization
        fidor = OAuth2Session(client_id, redirect_url=redirect_url)
        authorization_url, state = fidor.authorization_url(authorization_base_url)
        # State is used to prevent CSRF, keep this for later.
        session['oauth_state'] = state
        print("authorization URL is =" + authorization_url)
        return redirect(authorization_url)
    except KeyError:
        print("Key error in default - returning to index")
        return redirect(url_for('default'))

@app.route("/callback", methods=["GET"])
def callback():
    try:
        # Step 2: Retrieving an access token.
        fidor = OAuth2Session(state=session['oauth_state'])
        authorizationCode = request.args.get('code')
        body = 'grant_type=authorization_code&code=' + authorizationCode + \
               '&redirect_url=' + redirect_url + '&client_id=' + client_id
        auth = HTTPBasicAuth(client_id, client_secret)
        token = fidor.fetch_token(token_url, auth=auth, code=authorizationCode, body=body, method='POST')

        # Save the token and fetch protected resources
        session['oauth_token'] = token
        return redirect(url_for('.services'))
    except KeyError:
        print("Key error in callback - returning to index")
        return redirect(url_for('default'))

@app.route("/services", methods=["GET"])
def services():
    try:
        token = session['oauth_token']
        url = "https://api.tp.sandbox.fidorfzco.com/accounts"
        headers = {
            'Accept': "application/vnd.fidor.de;version=1;text/json",
            'Authorization': "Bearer " + token["access_token"]
        }

        response = requests.request("GET", url, headers=headers)
        print("Response status code:", response.status_code)
        print("Response text:", response.text)

        if response.status_code == 200:
            customersAccount = json.loads(response.text)
            print("customersAccount:", customersAccount)
            if 'data' in customersAccount and len(customersAccount['data']) > 0:
                customerDetails = customersAccount['data'][0]
                if 'customers' in customerDetails and len(customerDetails['customers']) > 0:
                    customerInformation = customerDetails['customers'][0]
                    session['fidor_customer'] = customersAccount
                    return render_template('services.html', fID=customerInformation["id"],
                                           fFirstName=customerInformation["first_name"], fLastName=customerInformation["last_name"],
                                           fAccountNo=customerDetails["account_number"], fBalance=(customerDetails["balance"] / 100))
                else:
                    print("No customer details found")
            else:
                print("No account data found")
        else:
            print("Error fetching data from API:", response.text)
        return render_template('services.html', error="No customer details found")
    except KeyError:
        print("Key error in services - returning to index")
        return redirect(url_for('default'))

@app.route("/bank_transfer", methods=["GET"])
def transfer():
    try:
        customersAccount = session['fidor_customer']
        customerDetails = customersAccount['data'][0]

        return render_template('internal_transfer.html', fFIDORID=customerDetails["id"],
                               fAccountNo=customerDetails["account_number"], fBalance=(customerDetails["balance"] / 100))
    except KeyError:
        print("Key error in bank_transfer - returning to index")
        return redirect(url_for('.index'))

@app.route("/process", methods=["POST"])
def process():
    if request.method == "POST":
        token = session['oauth_token']
        customersAccount = session['fidor_customer']
        customerDetails = customersAccount['data'][0]

        fidorID = customerDetails['id']
        custEmail = request.form['customerEmailAdd']
        transferAmt = int(float(request.form['transferAmount']) * 100)
        transferRemarks = request.form['transferRemarks']
        transactionID = request.form['transactionID']

        url = "https://api.tp.sandbox.fidorfzco.com/internal_transfers"

        payload = json.dumps({
            "account_id": fidorID,
            "receiver": custEmail,
            "external_uid": transactionID,
            "amount": transferAmt,
            "subject": transferRemarks
        })

        headers = {
            'Accept': "application/vnd.fidor.de; version=1,text/json",
            'Authorization': "Bearer " + token["access_token"],
            'Content-Type': "application/json"
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        print("process=" + response.text)

        transactionDetails = json.loads(response.text)
        return render_template('transfer_result.html', fTransactionID=transactionDetails["id"],
                               custEmail=transactionDetails["receiver"], fRemarks=transactionDetails["subject"],
                               famount=(float(transactionDetails["amount"]) / 100),
                               fRecipientName=transactionDetails["recipient_name"])

if __name__ == '__main__':
    app.run(debug=True)
