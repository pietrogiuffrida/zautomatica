#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import logging
from datetime import datetime, timedelta

import sys
if sys.version_info.major == 3:
  import xmlrpc.client as xmlrpclib
else:
  import xmlrpclib

def saveNow(disponibilita, disponibilita_path):
  out = open(disponibilita_path, 'w')
  json.dump(disponibilita, out)
  out.close()


def checkDelay(now, disponibilita_path, delay=60):

  # Legge dal file di configurazione la data dell'ultima esecuzione
  # Se il file di configurazione non esiste assume che si tratti del primo run
  # La data last_run maggiorata del delay deve essere inferiore o uguale alla data now
  # Se la condizione è verificata la data now viene assuna come nuova last_run

  pattern_date = '%Y%m%d%H%M'

  if not os.path.exists(disponibilita_path):
    disponibilita = {'last_run': now.strftime(pattern_date)}
    saveNow(disponibilita, disponibilita_path)
    return 0

  disponibilita = json.load(open(disponibilita_path, 'r'))
  last_run = datetime.strptime(disponibilita['last_run'], pattern_date)

  logging.debug('Last run {}'.format(last_run))

  next_run = last_run + timedelta(minutes=delay)
  logging.debug('Next run {}'.format(next_run))

  if next_run > now:
    delay = next_run - now
    logging.error('Eccessiva frequenza di richieste a ZAK, aspetta {} minutes'.format(round(delay.seconds / 60)))
    return 1

  disponibilita['last_run'] = now.strftime(pattern_date)
  saveNow(disponibilita, disponibilita_path)

  return 0


def initConnection(url, user, password, pkey):

  #server = xmlrpc.client.Server(url)
  server = xmlrpclib.Server(url)
  returnCode, token = server.acquire_token(user, password, pkey)

  props = server.fetch_properties(token)
  lcode = props[0]['lcode']

  return server, lcode, token


def parseDates(reservations):
  for i in reservations:
    i['dfrom'] = datetime.fromtimestamp(i['dfrom'])
    i['dto'] = datetime.fromtimestamp(i['dto'])
    i['created'] = datetime.fromtimestamp(i['created'])
  return reservations
