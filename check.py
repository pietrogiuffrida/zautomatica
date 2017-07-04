#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from private import *
import xmlrpc.client
from datetime import datetime, timedelta

import logging
logging.basicConfig(
  format='%(asctime)s\t%(levelname)s\t%(message)s',
  filename='default.log',
  level=logging.INFO
  #level=logging.DEBUG
  )
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


logging.info('*'*20 + ' NUOVA ESECUZIONE ' + '*'*20)


server = xmlrpc.client.Server(url)
returnCode, token= server.acquire_token(user, password, pkey)

props = server.fetch_properties(token)
lcode = props[0]['lcode']

now = datetime.now()
prossimi3 = now + timedelta(days=7-now.isoweekday()+14)
delta = prossimi3 - now

data = {}
for i in range(delta.days + 1):
  cur = now + timedelta(days=i)
  resvs = server.fetch_reservations_day(token, lcode, cur.strftime('%d/%m/%Y'))
  data[cur] = resvs


# Chiudere
server.release_token(token)

logging.info('*'*20 + ' ESCO NORMALMENTE ' + '*'*20)
