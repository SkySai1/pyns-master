import datetime
import logging
import time

def getnow(delta, rise):
    '''
    *delta* is timedelta of timezone \n
    *rise* is seconds which need to add to current time
    '''
    try:
        offset = datetime.timedelta(hours=delta)
        tz = datetime.timezone(offset)
        now = datetime.datetime.now(tz=tz)
        return now + datetime.timedelta(0,rise) 
    except:
        logging.error('Making date is fail', exc_info=(logging.DEBUG >= logging.root.level))

class ThisNode:
    id = None
    name = None