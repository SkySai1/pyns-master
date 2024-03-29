#!/etc/nspy/master/venv/bin/python3
import logging
import os
import configparser
import re
import sys
import os, platform
import ipaddress

_OPTIONS ={
    'GENERAL': ['listen-ip', 'listen-port', 'timedelta', 'autouser'],
    'DATABASE': ['dbuser', 'dbpass', 'dbhost', 'dbport', 'dbname'],
    'LOGGING' : ['enable', 'keeping', 'pathway' , 'level', 'separate', 'maxsize','rotation']
}

def loadconf():
    try:
        if sys.argv[1:]:
            path = os.path.abspath(sys.argv[1])
            if os.path.exists(path):
                CONF, state = getconf(sys.argv[1]) # <- for manual start
            else:
                print('Missing config file at %s' % path)
        else:
            thisdir = os.path.dirname(os.path.abspath(__file__))
            CONF, state = getconf(thisdir+'/config.ini')
        if state is False:
            raise Exception()
        return CONF
    except:
        logging.critical('Error with manual start', exc_info=(logging.DEBUG >= logging.root.level))
        sys.exit(1)  

def getconf(path):
    config = configparser.ConfigParser()
    config.read(path)
    bad = []
    try:
        for section in _OPTIONS:
            for key in _OPTIONS[section]:
                if config.has_option(section, key) is not True: bad.append(f'Bad config file: missing key - {key} in {section} section')
        if bad: raise Exception("\n".join(bad))
        if checkconf(config) is True:
            return config, True
        else:
            return None, False
    except Exception as e:
        logging.critical(str(e))
        sys.exit(1)

def checkconf(CONF:configparser.ConfigParser):
    msg = []
    try:
        for s in CONF:
            for opt in CONF.items(s):
                try:
                    if opt[0] == 'listen-ip': ipaddress.ip_address(opt[1]).version == 4
                    if opt[0] == 'listen-port': int(opt[1])
                    if opt[0] == 'printstats': eval(opt[1])
                    if opt[0] == 'autouser': eval(opt[1])
                    if opt[0] == 'expire': float(opt[1])
                    if opt[0] == 'scale': float(opt[1])
                    if opt[0] == 'size': int(opt[1])
                    if opt[0] == 'enable': eval(opt[1])
                    if opt[0] == 'resolver' and opt[1] != '': ipaddress.ip_address(opt[1]).version == 4
                    if opt[0] == 'maxdepth': int(opt[1])
                    if opt[0] == 'timeout': float(opt[1])
                    if opt[0] == 'retry': int(opt[1])
                    if opt[0] == 'timesync': float(opt[1])
                    if opt[0] == 'keeping':
                        if opt[1] not in ['db', 'file', 'both']: raise Exception
                    if opt[0] == 'pathway':   
                        if not os.path.exists(opt[1]):
                            try:
                                os.mkdir(opt[1])
                            except:
                                msg.append(f"{s}: {opt[0]} = {opt[1]} <- dir do not exist")
                        elif not os.access(opt[1], os.R_OK):
                            msg.append(f"{s}: {opt[0]} = {opt[1]} <- dir without read access ")
                    if opt[0] == 'level':
                        if opt[1] not in ['debug', 'info', 'warning', 'error', 'critical']: raise Exception
                    if opt[0] == 'maxsize':
                        if not re.match('^[0-9]*[b|k|m|g]$', opt[1].lower()):raise Exception
                    if opt[0] == 'rotation': int(opt[1])
                    if opt[0] == 'download': eval(opt[1])
                    if opt[0] == 'upload': eval(opt[1])
                except:
                    msg.append(f"{s}: {opt[0]} = {opt[1]} <- bad statetement")
                    continue
        if not msg: 
            return True
        else:
            logging.basicConfig(format="%(asctime)s %(levelname)s at %(name)s:: %(message)s", force=True)
            log = logging.getLogger('CONFIG CHECK')
            for m in msg:
                log.critical(m)
            return False
    except Exception as e:
        logging.critical('bad config file, recreate it')
        return False


def createconf(where, what:configparser.ConfigParser):
    with open(where, 'w+') as f:
        what.write(f)

def deafultconf():
    if platform.system() == "Windows":
        hostname = platform.uname().node
    else:
        hostname = os.uname()[1]  # doesnt work on windows

    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
    DBHost = str(input('Input HOSTNAME of your Data Base:\n'))    
    DBUser = str(input('Input USER of your Data Base:\n'))
    DBPass = str(input('Input PASSWORD of your Data Base\'s user:\n'))
    DBName = str(input('Input BASENAME of your Data Base\n'))
    config['GENERAL'] = {
        'listen-ip': '127.0.0.2',
        'listen-port': 53,
        ";For mysql better keep timedelta as 0, for pgsql as your region timezone": None,
        'timedelta': 3,
        ";For auto creating zero super user ('admin'), in each start password will random = True":None,
        ";WARNING: logging level must set to INFO, password will send in there": None,
        'autouser': True
    }
    config['DATABASE'] = {
        'dbuser': DBUser,
        'dbpass': DBPass,
        'dbhost': DBHost,
        'dbport': 5432,
        'dbname': DBName,
    }
    config['LOGGING'] = {
        ";Enable logging = False|True": None,
        'enable': True, 
        ";Minimum level of log events = debug|info|warning|error|critical":None,
        'level': 'error',
        ";Log storage (in database or in file) = db|file|both": None,
        'keeping': 'both',
        "### Applying only with log keeping as in file or both ###":None, 
        ";Folder where is logfiles placing, actually while 'keeping' is file or both":None,
        'pathway': './logs/' , 
        ";Will separate log files by level = False|True":None, 
        'separate': True,
        ";Max size of each log file = 1048576B|1024K|1M|1G":None,
        'maxsize': '1M',
        ";Rotation, number of backup copies after reach maxsize = 5":None,
        'rotation': 5
    }
    return config

if __name__ == "__main__":
    here = f"{os.path.abspath('./')}/config.ini"
    if os.path.exists(here):
            while True:
                try:
                    y = str(input(f"{here} is exists, do you wanna to recreate it? (y/n)\n"))
                    if y == "n": sys.exit()
                    elif y == "y": break
                except ValueError:
                    pass
                except KeyboardInterrupt:
                    sys.exit()
    conf = deafultconf()
    createconf(here, conf)
    getconf(here)