import logging
import random, string
import re

from back.object import BadName

def randomword(length) -> str:
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def parse_list(rawdata):
   if rawdata:
      data = []
      for obj in rawdata:
         row = obj[0]
         data.append([row.fqdn, row.id, row.active])
      return data
   return []

def domain_validate(input:str):
   try:
      input = input.lower().encode('idna').decode().rstrip('.')
      if len(input) > 255 or len(input) < 1: raise BadName
      for label in input.split('.'):
         if len(label) > 64: raise BadName
         if not re.match(r'^[a-z0-9]', label[0]): raise BadName
         for l in label:
            if not re.match(r'[a-z]|[0-9]|\-', l): raise BadName
      input = input.encode().decode('idna')
      return input + '.'
   except:
      logging.debug(f"{input} is a bad DNS name", exc_info=(logging.DEBUG >= logging.root.level))
      return BadName

