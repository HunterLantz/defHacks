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
    

