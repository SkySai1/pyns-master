#!/home/dnspy/master/master/bin/python3
import sys
import os
import logging
from backend.accessdb import AccessDB, enginer
from flask import Flask, g, request, current_app, session
from flask_sqlalchemy import SQLAlchemy
from backend.functions import ThisNode
from backend.logger import logsetup
from initconf import getconf, loadconf

app = Flask(__name__)

@app.before_request
def pre_load():
    '''if "user_id" in session:
        g.user = db.session.get(session["user_id"])'''
    pass

@app.route('/')
def index():
    ua = request.headers.get('User-Agent')
    return '<h1>%s</h1>' % ua

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s!</h1>' %  (name)

@app.route('/t')
def test():
    r = 'Test'
    d = AccessDB.GetFromDomains(appdb)
    r = []
    for obj in d:
        row = obj[0]
        r.append((row.name, row.type, row.data))
    return r

def start():
    ThisNode.name = 'Master'
    logreciever = logsetup(CONF)
    engine = enginer(CONF)
    #db = AccessDB(engine, CONF)
    app.config['SQLALCHEMY_DATABASE_URI'] = engine.url
    global appdb
    appdb = SQLAlchemy(app)
    app.run('0.0.0.0',5380,debug=True)
    

if __name__ == "__main__":
    CONF = loadconf()
    start()