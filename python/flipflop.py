import base64
import os
import datetime
import plaid
import json
import time
import random
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify


def flipflop(aID, uID, tID, value):
    newaID = checkdupes(aID)
    if newaID != null:
        cursor.execute('''
                        INSERT INTO findata (uID,score,tID,aID,tstat) VALUES(?, ?, ?, ?, ?))
                        ''', (newaID,random.randint(1,6),tID,newuID,random.randint(0,2)))
    

def checkdupes(checkID):
    transactions_response = client.Transactions.get(access_token, start_date, end_date)
    except plaid.errors.PlaidError as e:
        return jsonify(format_error(e))
    pretty_print_response(transactions_response)
    for trans in transactions_response:
        compareID = transactions_response['accounts'][0]['account_id']
        if compareID.equals(checkID):
            return null
        else
        compareID = trans['account_id']
        if compareID.equals(checkID):
            return null
        else
        return checkID