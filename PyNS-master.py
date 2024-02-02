#!/home/dnspy/master/venv/bin/python3
import secrets
from datetime import datetime
from back.accessdb import AccessDB, enginer
from flask import Flask, flash, request, current_app, session, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from back.logger import logsetup
from initconf import getconf, loadconf
from back.forms import LoginForm, NewDomain, DomainForm, NewZone
from back.object import Domain, BadName, Zones
from back.functions import parse_list, domain_validate
from back.worker import add_object, edit_object, remove_object, switch_object
from psycopg2.errors import UniqueViolation

app = Flask(__name__)

@app.before_request
def pre_load():
    if "user_id" in session or True:
        pass
    elif request.form.get('action') == str(hash("login")):
        user = request.form.get('username')
        passwd = request.form.get('password')
        if user and passwd:
            appdb = app.config.get('DB')
            db = AccessDB(appdb.engine, CONF)
            user_id = db.get_userid(user, passwd)
            if user_id: 
                session.update(user_id = user_id[0])
                return redirect(request.url)
            else:
                flash('Пользователь не найден')
                return login()
    else:
        return login()
    pass

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html.j2'), 404

@app.errorhandler(405)
def page_not_found(e):
    return render_template('404.html.j2'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html.j2'), 500

@app.route('/login', methods=['GET','POST'])
def login():
    if "user_id" in session:
        return redirect('/')
    form = LoginForm()
    form.hidden_tag()
    return render_template('login.html.j2', action = hash("login"), form=form)

@app.route('/')
def index():
    ua = request.headers.get('User-Agent')
    return render_template('index.html.j2', ua = ua, current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s!</h1>' %  (name)

@app.route('/domains', methods=['GET','POST'])
def domains():
    appdb = app.config.get('DB')
    db = AccessDB(appdb.engine, CONF)
    data = db.get_domains()
    d_list = parse_list(data)
    form = NewDomain()
    if request.method == 'POST':
        return d_list
    else:
        return render_template(
            'domains.html.j2', 
            domains = d_list, 
            form = form, 
            new = Domain.hash_new,
            remove = Domain.hash_mv,
            edit = Domain.hash_edit,
            switch = Domain.hash_switch
        )

@app.route('/domains/<domain>/<action>', methods = ['POST'])
def domain_action(domain, action):
    try:
        id = int(domain)
        domain = None
    except:
        id = None
        if not domain: return '', 500
        if domain == '*': domain = None
        else: 
            domain = domain_validate(domain)
            if domain is BadName:
                return 'badname', 520

    if action == Domain.hash_new: return add_object(app, domain, 'd')
    elif action == Domain.hash_mv: return remove_object(app, id, 'd')
    elif action == Domain.hash_edit: return edit_object(app, domain, 'd') 
    elif action == Domain.hash_switch: return switch_object(app, domain, 'd')
    
    return '', 404


@app.route('/zones', methods=['GET','POST'])
def zones():
    appdb = app.config.get('DB')
    db = AccessDB(appdb.engine, CONF)
    data = db.get_zones()
    z_list = parse_list(data)
    form = NewZone()
    if request.method == 'POST':
        return z_list
    else:
        return render_template(
            'zones.html.j2', 
            zones = z_list, 
            form = form, 
            new = Zones.hash_new,
            remove = Zones.hash_mv,
            edit = Zones.hash_edit,
            switch = Zones.hash_switch
        )    

@app.route('/zones/<zone>/<action>', methods = ['POST'])
def zone_action(zone, action):
    try:
        id = int(zone)
        zone = None
    except:
        id = None
        if not zone: return '', 500
        if zone == '*': zone = None
        else: 
            zone = domain_validate(zone)
            if zone is BadName:
                return 'badname', 520

    if action == Zones.hash_new: return add_object(app, zone, 'z')
        
    elif action == Domain.hash_mv:
        db = AccessDB(app.config.get('DB').engine, CONF)
        result = db.remove_domains(id=id, fqdn=zone)
        if result:
            return [result]
        else:
            return '', 520
        
    elif action == Domain.hash_edit:
        if not zone: return 'empty', 520
        input = request.form.get('new')
        new = domain_validate(input)
        if not new: return 'badname', 520
        db = AccessDB(app.config.get('DB').engine, CONF)
        result = db.update_domain(new, id=id, fqdn=zone)
        if result:
            return [result]
        else:
            return '', 520
        
    elif action == Domain.hash_switch:
        db = AccessDB(app.config.get('DB').engine, CONF)
        state = request.form.get('state')
        result = db.switch_domain(state, id=id, fqdn=zone)
        if result:
            return [result]
        else:
            return '', 520
    
    return '', 404


@app.route('/t/<test>/')
def test(test=None):
    if not test: test = 'nope'
    return test

def start():
    logreciever = logsetup(CONF)
    engine = enginer(CONF)
    app.config['SECRET_KEY'] = secrets.token_hex()
    app.config['SQLALCHEMY_DATABASE_URI'] = engine.url
    app.config['DB'] = SQLAlchemy(app)
    app.config['CONF'] = CONF
    db = AccessDB(engine, CONF)

    Domain.setup()
    Zones.setup()

    if eval(CONF['GENERAL']['autouser']):
        db.create_zero_user()
    else:
        db.delete_user(id='-1')

    app.run('0.0.0.0',5380,debug=True)
    

if __name__ == "__main__":
    CONF = loadconf()
    start()