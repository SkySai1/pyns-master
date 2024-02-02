import secrets

class BadName(Exception): ...

class Domain:
    hash_new = None
    hash_mv = None
    hash_edit = None
    hash_switch = None

    def setup():
        Domain.hash_new = secrets.token_hex()
        Domain.hash_mv = secrets.token_hex()
        Domain.hash_edit = secrets.token_hex()
        Domain.hash_switch = secrets.token_hex()

class Zones:
    hash_new = None
    hash_mv = None
    hash_edit = None
    hash_switch = None

    def setup():
        Zones.hash_new = secrets.token_hex()
        Zones.hash_mv = secrets.token_hex()
        Zones.hash_edit = secrets.token_hex()
        Zones.hash_switch = secrets.token_hex()