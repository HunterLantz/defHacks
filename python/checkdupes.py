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

def checkdupes(checkID):
    for row in cursor.execute('SELECT findata.uID from findata'):
        compareID = row.uID
        if compareID.equals(checkID):
            return null
        else:
            for row in cursor.execute('SELECT findata.account_ID from findata'):
                compareID = row.account_ID
        if compareID.equals(checkID):
            return null
        else:
            return checkID
