import base64
import os
import datetime
import plaid
import json
import time
import pymysql
import pyodbc
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=./transactions.accdb;')
cursor = conn.cursor()


app = Flask(__name__)


# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = "5cb27f55fede9b00136ae9ea"
PLAID_SECRET = "9ab5a00f6556c64845e82324a1f422"
PLAID_PUBLIC_KEY = '03034c7d92532323912a23a416437c'
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = 'sandbox'
# PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# Link. Note that this list must contain 'assets' in order for the app to be
# able to create and retrieve asset reports.
PLAID_PRODUCTS = 'transactions'

client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2018-05-22')




@app.route('/')
def index():
  return render_template(
    'index.html',
    plaid_public_key=PLAID_PUBLIC_KEY,
    plaid_environment=PLAID_ENV,
    plaid_products=PLAID_PRODUCTS,
  )

@app.route('/home')
def home():
  return render_template(
    'home.html',
    plaid_public_key=PLAID_PUBLIC_KEY,
    plaid_environment=PLAID_ENV,
    plaid_products=PLAID_PRODUCTS,
  )

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    list = []
    adder = request.form['rating']
    if request.form['rating'] == 1:
        adder = -5
    if request.form['rating']==2;
        adder=-4
    if request.form['rating']==3:
        adder=0
    for row in cursor.execute("SELECT * FROM findata WHERE uID LIKE ?",(request.form['relation'])):
        temp = ('uID':row.uID, 'score':row.score+adder, 'tID':row.tID, 'aID';row.aID, 'tstat':row.tstat)
    cursor.execute("DELETE FROM findata WHERE uID LIKE ?",(request.form['relation']))
    for tup in temp:
        cursor.execute('''
                    INSERT INTO findata (uID,score,tID,aID,tstat) VALUES( ?, ?, ?, ?,?)
                  ''',(temp['uID'],temp['score'],temp['tID'],temp['aID'], temp['tstat']))
    conn.commit();
    dic = []
    for row in cursor.execute("SELECT findata.score, findata.aID FROM findata WHERE tstat LIKE '%0%'"):
        if not any(d['aID'] == row.aID for d in dic):
            dic.append({'aID':row.aID, 'rating':row.score, 'ratings':1})
        else:
            for thing in dic:
                if thing['aID'] == row.aID:
                    thing['ratings']+=1
    return render_template(
    'account.html',
    plaid_public_key=PLAID_PUBLIC_KEY,
    plaid_environment=PLAID_ENV,
    plaid_products=PLAID_PRODUCTS,
    mytrans=False,
    rating=True,
    ratings=dic,
  )

@app.route('/account')
def account():
    dic = []
    for row in cursor.execute("SELECT findata.score, findata.aID FROM findata WHERE tstat LIKE '%0%'"):
        if not any(d['aID'] == row.aID for d in dic):
            dic.append({'aID':row.aID, 'rating':row.score, 'ratings':1})
        else:
            for thing in dic:
                if thing['aID'] == row.aID:
                    thing['ratings']+=1
    return render_template(
    'account.html',
    plaid_public_key=PLAID_PUBLIC_KEY,
    plaid_environment=PLAID_ENV,
    plaid_products=PLAID_PRODUCTS,
    mytrans=False,
    rating=True,
    ratings=dic,
  )

@app.route('/mytrans')
def mytrans():
    
    return render_template(
    'account.html',
    plaid_public_key=PLAID_PUBLIC_KEY,
    plaid_environment=PLAID_ENV,
    plaid_products=PLAID_PRODUCTS,
    mytrans=True,
    transactions=transactions,
    
  )
access_token = None
transactions = None
# Exchange token flow - exchange a Link public_token for
# an API access_token
# https://plaid.com/docs/#exchange-token-flow
@app.route('/get_access_token', methods=['POST'])
def get_access_token():
  global access_token
  public_token = request.form['public_token']
  try:
    exchange_response = client.Item.public_token.exchange(public_token)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))

  pretty_print_response(exchange_response)
  access_token = exchange_response['access_token']
  return jsonify(exchange_response)

# Retrieve ACH or ETF account numbers for an Item
# https://plaid.com/docs/#auth
@app.route('/auth', methods=['GET'])
def get_auth():
  try:
    auth_response = client.Auth.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(auth_response)
  return jsonify({'error': None, 'auth': auth_response})

# Retrieve Transactions for an Item
# https://plaid.com/docs/#transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
  # Pull transactions for the last 30 days
  start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
  end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
  try:
    transactions_response = client.Transactions.get(access_token, start_date, end_date)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))
  pretty_print_response(transactions_response)
  store = []
  for trans in transactions_response['transactions']:
    data = trans['account_id']+": "+str(trans['amount'])
    dic = {"id":trans['name'], "value":str(trans['amount'])}
    store.append(dic)
    
    if trans['amount']>30:
          cursor.execute('''
                    INSERT INTO findata (uID,score,tID,aID,tstat) VALUES( ?, '3', ?, ?,'0')
                  ''',(transactions_response['accounts'][0]['account_id'],trans['transaction_id'],trans['account_id']))

  global transactions
  transactions = store
  conn.commit();
  
  return jsonify({'error': None, 'transactions': transactions_response})

# Retrieve Identity data for an Item
# https://plaid.com/docs/#identity
@app.route('/identity', methods=['GET'])
def get_identity():
  try:
    identity_response = client.Identity.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(identity_response)
  return jsonify({'error': None, 'identity': identity_response})

# Retrieve an Item's accounts
# https://plaid.com/docs/#accounts
@app.route('/accounts', methods=['GET'])
def get_accounts():
  try:
    accounts_response = client.Accounts.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(accounts_response)
  return jsonify({'error': None, 'accounts': accounts_response})


@app.route('/set_access_token', methods=['POST'])
def set_access_token():
  global access_token
  access_token = request.form['access_token']
  item = client.Item.get(access_token)
  return jsonify({'error': None, 'item_id': item['item']['item_id']})

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True))

def format_error(e):
  return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 5000))
