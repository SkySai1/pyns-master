import datetime
import logging
import time
import uuid
import sys
import psycopg2
from back.functions import randomword
from hashlib import sha256
from sqlalchemy.engine.base import Engine
from sqlalchemy import CHAR, SmallInteger, TypeDecorator, engine, UUID, BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, ARRAY, exc, create_engine, delete, insert, select, or_, not_, update
from sqlalchemy.orm import declarative_base, Session, relationship
from flask_sqlalchemy import SQLAlchemy
from psycopg2.errors import UniqueViolation
# --- DB structure

Base = declarative_base()

def checkconnect(engine:engine.base.Engine, conf):
    try:
        engine.connect()
        Base.metadata.create_all(engine)
        return True
    except:
        logging.error("Fail to check database", exc_info=(logging.DEBUG >= logging.root.level))
        return False

def enginer(_CONF):
    try:  
        engine = create_engine(
            f"postgresql+psycopg2://{_CONF['DATABASE']['dbuser']}:{_CONF['DATABASE']['dbpass']}@{_CONF['DATABASE']['dbhost']}:{int(_CONF['DATABASE']['dbport'])}/{_CONF['DATABASE']['dbname']}",
            connect_args={'connect_timeout': 5},
            pool_pre_ping=True
        )
        if checkconnect(engine, _CONF) is True:
            logging.debug(f"Created new database engine {engine.url}")
            return engine
        else: raise Exception()
    except Exception as e:
        logging.critical(f"The database is unreachable", exc_info=(logging.DEBUG >= logging.root.level))
        sys.exit(1)

class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    role = Column(SmallInteger, default=1)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    telegram = Column(String(255), default=None)
    email = Column(String(255), default=None)
    active = Column(Boolean, default=True)
        
class Nodes(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True)
    node = Column(String(255), unique=True)

class DomainsList(Base):
    __tablename__ = "domains_list"
    id = Column(Integer, primary_key=True)
    fqdn = Column(String(255), nullable=False, unique=True)
    active = Column(Boolean, default=True)


class Domains(Base):  
    __tablename__ = "domains" 
    id = Column(BigInteger, primary_key=True)
    node = Column(String(255), ForeignKey('nodes.node', ondelete='cascade'), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)  
    domain = Column(String(255), ForeignKey('domains_list.fqdn', ondelete='cascade'), nullable=False) 
    status = Column(SmallInteger, nullable=False)
    result = Column(Text)
    message = Column(Text)
    auth = Column(String(255), default = None)

class ZonesList(Base):
    __tablename__ = "zones_list"
    id = Column(Integer, primary_key=True)
    fqdn = Column(String(255), nullable=False, unique=True)
    active = Column(Boolean, default=True)

class Zones(Base):
    __tablename__ = "zones"
    id = Column(BigInteger, primary_key=True)
    node = Column(String(255), ForeignKey('nodes.node', ondelete='cascade'), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)
    zone = Column(String(255), ForeignKey('zones_list.fqdn', ondelete='cascade'), nullable=False) 
    status = Column(Integer, nullable=False)
    serial = Column(Integer)
    message = Column(Text)

class FullResolve(Base): 
    __tablename__ = "fullresolve" 
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    node = Column(String(255), ForeignKey('nodes.node', ondelete='cascade'), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)
    zone = Column(String(255), nullable=False)  
    rtime = Column(Float)

class ShortResolve(Base):
    __tablename__ = "shortresolve" 
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    node = Column(String(255), ForeignKey('nodes.node', ondelete='cascade'), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)
    server = Column(String(255), nullable=False)  
    rtime = Column(Float)


class ServerList(Base):
    __tablename__ = "server_list"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    ip = Column(String(255), nullable=False, unique=True)
    tag = Column(String(255), nullable=False)

class Servers(Base):  
    __tablename__ = "servers" 
    id = Column(BigInteger, primary_key=True)
    node = Column(String(255), ForeignKey('nodes.node', ondelete='cascade'), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)  
    server = Column(String(255), ForeignKey('server_list.name', ondelete='cascade'), nullable=False) 
    status = Column(SmallInteger, nullable=False)
    message = Column(Text)

class GeoBase(Base):
    __tablename__ = "geobase"
    id = Column(BigInteger, primary_key=True)
    ip = Column(String(255), nullable=False, unique = True)
    latitude = Column(Float) # <- First value in coordinates
    longitude = Column(Float) # <- Second value in coordinates
    country = Column(String(255))
    city = Column(String(255))

class GeoState(Base):  
    __tablename__ = "geostate" 
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    node = Column(String(255), ForeignKey('nodes.node', ondelete='cascade'), nullable=False)
    ip = Column(String(255), ForeignKey('geobase.ip', ondelete='cascade'), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)  
    domain = Column(String(255), nullable=False)
    state = Column(SmallInteger, nullable=False)
    result = Column(Text)

class Logs(Base):
    __tablename__ = "logs"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    node = Column(String(255), ForeignKey('nodes.node', ondelete='cascade'), nullable=False)
    ts = Column(DateTime(timezone=True), nullable=False)
    level = Column(String(255), nullable = False)
    object = Column(String(255), nullable = False)
    message = Column(Text)  




class AccessDB:

    def __init__(self, engine:engine, _CONF):
        self.engine = engine
        self.conf = _CONF
        self.timedelta = int(_CONF['GENERAL']['timedelta'])
        self.c = Session(engine)
        logging.debug(f"Initialize new database connect '{engine.url}'")
    
    def drop(self):
        logging.error('Database is lost connection')
        self.c.rollback()
    
    def create_zero_user(self):
        try:
            rawpass = randomword(10)
            password = sha256(rawpass.encode()).hexdigest()
            with Session(self.engine) as conn:
                id = conn.execute(select(Users.id).filter(Users.id == -1)).fetchone()
                if id:
                    stmt = update(Users).filter(Users.id == -1).values(password = password)
                else:
                    stmt = insert(Users).values(
                        id = -1,
                        role = 0,
                        name = 'admin',
                        password = password
                    )
                conn.execute(stmt)
                conn.commit()
                logging.info('AUTOUSER IS ENABLED. Current admin passwords is \'%s\'' % rawpass)
        except Exception as e:
            logging.error('Create zero user into database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return None

    def get_userid(self, user:str, rawpass:str):
        try:
            password = sha256(rawpass.encode()).hexdigest()
            with Session(self.engine) as conn:
                stmt = select(Users.id).filter(Users.name == user, Users.password == password)
                return conn.execute(stmt).fetchone()
        except Exception as e:
            logging.error('Fail to get user data from database', exc_info=(logging.DEBUG >= logging.root.level))
            return None   

    def delete_user(self, id:str=None, email:str=None, name:str=None):
        if id or email or name:
            try:
                where = []
                if id: where.append(Users.id == id)
                if email: where.append(Users.email == email)
                if name: where.append(Users.name == name)
                with Session(self.engine) as conn:
                    stmt = delete(Users).filter(*where)
                    conn.execute(stmt)
                    conn.commit()
            except Exception as e:
                logging.error('Fail to delete user from database', exc_info=(logging.DEBUG >= logging.root.level))
                return None

    def get_domains(self, id:str=None, fqdn:str=None):
        try:
            where = []
            if id: where.append(DomainsList.id == id)
            if fqdn: where.append(DomainsList.fqdn == fqdn)
            with Session(self.engine) as conn:
                result = conn.execute(select(DomainsList).filter(*where).order_by(DomainsList.fqdn)).fetchall()
                return result
        except Exception as e:
            logging.error('Get domains list from database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return None
        
    def new_domain(self, fqdn:str):
        try:
            
            with Session(self.engine) as conn:
                if conn.execute(select(DomainsList).filter(DomainsList.fqdn == fqdn)).fetchone():
                    return UniqueViolation
                stmt = insert(DomainsList).values(fqdn = fqdn).returning(DomainsList)
                data = conn.scalars(stmt).fetchmany()
                conn.commit()
                for obj in data:
                    return obj.id, obj.fqdn
                return None, None
        except Exception as e:
            logging.error('Add domain into database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return ''
    
    def remove_domains(self, id:str=None, fqdn:str=None):
        try:
            where = []
            if id: where.append(DomainsList.id == id)
            if fqdn: where.append(DomainsList.fqdn == fqdn)
            with Session(self.engine) as conn:
                stmt = delete(DomainsList).filter(*where).returning(DomainsList.id)
                result = conn.scalars(stmt).one()
                conn.commit()
                return result
        except Exception as e:
            logging.error('Remove domain list in database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return None
              
    def update_domain(self, new:str, id:int=None, fqdn:str=None):
        try:
            where = []
            if id: where.append(DomainsList.id == id)
            if fqdn: where.append(DomainsList.fqdn == fqdn)
            with Session(self.engine) as conn:
                stmt = update(DomainsList).filter(*where).values(fqdn = new).returning(DomainsList.fqdn)
                result = conn.scalars(stmt).one_or_none()
                conn.commit()
                return result
        except Exception as e:
            logging.error('Update domains in database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return False
             
    def switch_domain(self, state:bool|str, id:int=None, fqdn:str=None):
        try:
            if state.lower() == "true": state = True
            elif state.lower() == "false": state = False
            where = []
            if id: where.append(DomainsList.id == id)
            if fqdn: where.append(DomainsList.fqdn == fqdn)
            with Session(self.engine) as conn:
                stmt = update(DomainsList).filter(*where).values(active = state)
                conn.execute(stmt)
                conn.commit()
                return True
        except Exception as e:
            logging.error('Switch domains in database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return False      

    def get_geobase(self):
        try:
            with Session(self.engine) as conn:
                result = conn.execute(select(GeoBase)).fetchall()
                return result
        except Exception as e:
            logging.error('Get geobase from database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return None
    
    def get_zones(self, id:str=None, fqdn:str=None):
        try:
            where = []
            if id: where.append(ZonesList.id == id)
            if fqdn: where.append(ZonesList.fqdn == fqdn)
            with Session(self.engine) as conn:
                result = conn.execute(select(ZonesList).filter(*where).order_by(ZonesList.fqdn)).fetchall()
                return result
        except Exception as e:
            logging.error('Get zones list from database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return None


    def new_zone(self, fqdn:str):
        try:
            
            with Session(self.engine) as conn:
                if conn.execute(select(ZonesList).filter(ZonesList.fqdn == fqdn)).fetchone():
                    return UniqueViolation
                stmt = insert(ZonesList).values(fqdn = fqdn).returning(ZonesList)
                data = conn.scalars(stmt).fetchmany()
                conn.commit()
                for obj in data:
                    return obj.id, obj.fqdn
                return None, None
        except Exception as e:
            logging.error('Add zone into database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return ''

    def remove_zone(self, id:str=None, fqdn:str=None):
        try:
            where = []
            if id: where.append(ZonesList.id == id)
            if fqdn: where.append(ZonesList.fqdn == fqdn)
            with Session(self.engine) as conn:
                stmt = delete(ZonesList).filter(*where).returning(ZonesList.fqdn)
                result = conn.scalars(stmt).one()
                conn.commit()
                return result
        except Exception as e:
            logging.error('Remove zone from zonelist in database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return None

    def update_zone(self, new:str, id:int=None, fqdn:str=None):
        try:
            where = []
            if id: where.append(ZonesList.id == id)
            if fqdn: where.append(ZonesList.fqdn == fqdn)
            with Session(self.engine) as conn:
                stmt = update(ZonesList).filter(*where).values(fqdn = new).returning(ZonesList.fqdn)
                result = conn.scalars(stmt).one_or_none()
                conn.commit()
                return result
        except Exception as e:
            logging.error('Update zone in database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return False

    def switch_zone(self, state:bool|str, id:int=None, fqdn:str=None):
        try:
            if state.lower() == "true": state = True
            elif state.lower() == "false": state = False
            where = []
            if id: where.append(ZonesList.id == id)
            if fqdn: where.append(ZonesList.fqdn == fqdn)
            with Session(self.engine) as conn:
                stmt = update(ZonesList).filter(*where).values(active = state)
                conn.execute(stmt)
                conn.commit()
                return True
        except Exception as e:
            logging.error('Switch zone in database is fail', exc_info=(logging.DEBUG >= logging.root.level))
            return False   
