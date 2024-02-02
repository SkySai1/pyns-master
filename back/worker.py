
from back.accessdb import AccessDB
from flask import Flask, request
from psycopg2.errors import UniqueViolation
from back.functions import domain_validate
from back.object import Domain, Zones


def add_object(app:Flask, fqdn, otype:str):
    db = AccessDB(app.config.get('DB').engine, app.config.get('CONF'))
    if not fqdn: return 'empty', 520
    if otype.lower() == 'd': 
        result = db.new_domain(fqdn)
        obj = Domain
    elif otype.lower() == 'z': 
        result = db.new_zone(fqdn)
        obj = Zones

    if result and type(result) is tuple:
        return {
            "object": result[1],
            "id": result[0],
            "remove": obj.hash_mv,  
            "edit": obj.hash_edit, 
            "switch": obj.hash_switch}
    elif result is UniqueViolation:
        return 'exist', 520
    else: 
        return 'fail', 520

def remove_object(app:Flask, id, otype:str):
    db = AccessDB(app.config.get('DB').engine, app.config.get('CONF'))
    if otype.lower() == 'd':  result = db.remove_domains(id)
    elif otype.lower() == 'z':  result = db.remove_zone(id)
    if result:
        return [result]
    else:
        return '', 520

def edit_object(app:Flask, fqdn:str, otype:str):
    if not fqdn: return 'empty', 520
    input = request.form.get('new')
    new = domain_validate(input)
    if not new: return 'badname', 520
    db = AccessDB(app.config.get('DB').engine, app.config.get('CONF'))
    if otype.lower() == 'd': result = db.update_domain(new, fqdn=fqdn)
    elif otype.lower() == 'z':  result = db.remove_zone(new, fqdn=fqdn)
    if result:
        return [result]
    else:
        return '', 520

def switch_object(app:Flask, fqdn:str, otype:str):
    db = AccessDB(app.config.get('DB').engine, app.config.get('CONF'))
    state = request.form.get('state')
    if otype.lower() == 'd': result = db.switch_domain(state, fqdn=fqdn)
    elif otype.lower() == 'z': result = db.switch_zone(state, fqdn=fqdn)
    if result:
        return [result]
    else:
        return '', 520       