#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# global limit 580 calls in 3600

import os
from time import sleep
from private import *
import xmlrpc.client
from datetime import datetime, timedelta

import logging
logging.basicConfig(
  format='%(asctime)s\t%(levelname)s\t%(message)s',
  #filename='default.log',
  #level=logging.INFO
  level=logging.DEBUG
  )

logging.info('*'*20 + ' NUOVA ESECUZIONE ' + '*'*20)

now = datetime.now()

if os.path.exists('disponibilita.json'):
  disponibilita = json.load(open('disponibilita.json'))
  disponibilita = disponibilita['next']
else:
  sleep(2)
  disponibilita = datetime.now()


if disponibilita < now:
  delay = disponibilita - now
  logging.error('Eccessiva frequenza, aspetta {}'.format(delay.seconds))


calls = 1
server = xmlrpc.client.Server(url)
returnCode, token = server.acquire_token(user, password, pkey)

props = server.fetch_properties(token)
lcode = props[0]['lcode']


past = now + timedelta(days=7-now.isoweekday()-14)
future = now + timedelta(days=7-now.isoweekday()+14)

resvs = server.fetch_reservations(token, lcode, past.strftime('%d/%m/%Y'), future.strftime('%d/%m/%Y'))
calls += 1
sleep(5)

for i in resvs:
  i['dfrom'] = datetime.fromtimestamp(i['dfrom'])
  i['dto'] = datetime.fromtimestamp(i['dto'])


data = {}
delta = future - past
for d in range(delta.days + 1):

  cur = past + timedelta(days=d)
  data[cur.strftime('%d/%m/%Y')] = {'resvs': 0}

  logging.debug(cur)

  for i in resvs:
    if i['dfrom'] >= cur <= i['dto']:
      data[cur.strftime('%d/%m/%Y')]['resvs'] += 1
      logging.debug(i['rcode'])
      print(cur, i['rcode'])



for i in range(delta.days + 1):

  cur = yesterday + timedelta(days=i)
  scur = cur.strftime('%d/%m/%Y')
  data[scur] = {}

  logging.debug('Arrivato a {}'.format(scur))

  resvs = server.fetch_reservations_day(token, lcode, scur)
  calls += 1

  if len(resvs) == 2 and resvs[0] in [-1, -21]:
    logging.warning('token scaduto {}'.format(calls))
    break

  data[scur]['resvs'] = resvs

  if cur <= now:

    logging.debug('Cheking revenues {}'.format(scur))

    rev = 0
    for res in resvs:
      invoices = server.fetch_invoices(token, lcode, res['rcode'])

      if len(invoices) == 2 and invoices[0] in [-1, -21]:
        logging.warning('token scaduto {}'.format(calls))
        break

      for invoice in invoices:
        logging.debug(invoice)
        rev += invoice['concepts']['tt_invoice']

      sleep(2)

    data[scur]['invoices'] = rev

  sleep(3)



# Chiudere
server.release_token(token)

logging.info('*'*20 + ' ESCO NORMALMENTE ' + '*'*20)
