#!/usr/bin/env python
# -*- coding: utf-8 -*-

# global limit 580 calls in 3600

import os
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
from collections import Counter
import logging

from lib import *
#from private import *
#from config import *

def loadData(nodelay=False):

  from config import min_delay, disponibilita_path
  from private import pkey, email, user, password, url

  # Today and now!
  now = datetime.now()


  # Verifico che il delay sia stato rispettato
  status = checkDelay(now, disponibilita_path, delay=min_delay)


  # In caso contrario esco immediatamente
  if status == 1:

    if nodelay == True:
      logging.warning('NO DELAY TRUE!')

    else:
      logging.error('Report ZAK non dispobibile')
      return ''


  logging.info('Loading ZAK')

  # Configuro la connessione
  server, lcode, token = initConnection(url, user, password, pkey)


  # Definisco il perimetro termporale: da 2 we nel passato a 2 we nel futuro, a prescindere dal wod corrente
  #past = now + timedelta(days= 7 - now.isoweekday() - 14)
  past = now
  future = now + timedelta(days= 7 - now.isoweekday() + 14)


  # Scarico le prenotazioni
  reservations = server.fetch_reservations(token, lcode, past.strftime('%d/%m/%Y'), future.strftime('%d/%m/%Y'))

  # Chiudo la connessione
  server.release_token(token)


  # Eseguo il parsing delle date
  reservations = parseDates(reservations)


  # Itero e calcolo
  data = {}
  delta = future - past
  for d in range(delta.days + 1):

    # Per ciascuno fra i giorni presi in considerazione
    cur = past + timedelta(days=d)
    cur_as_string = cur.strftime('%Y/%m/%d')

    logging.debug(cur_as_string)

    correnti = [i for i in reservations if i['dfrom'] <= cur < i['dto']]
    adults = sum([i.get('adults', 0) for i in correnti])
    childs = sum([i.get('children', 0) for i in correnti])
    revenues = sum([i['roomspricing'][0]['price'] for i in correnti])
    room_type = Counter([i['roomspricing'][0]['type'].split('_')[1] for i in correnti])
    #rcodes = [i['rcode'] for i in correnti]

    values = {
      'date': cur,
      'reservations': len(correnti),
      'adults': adults,
      'childs': childs,
      'revenues': revenues,
      #'rcodes': rcodes
      }
    values.update(room_type)

    data[cur_as_string] = values

  # Metto in tabella salvo ed esco
  df = pd.DataFrame(list(data.values()))
  df.fillna(0, inplace=True)
  df.sort_values('date', inplace=True)
  df.date = df.date.apply(lambda x: x.strftime('%d/%m'))

  columns = ["date", "reservations", "Borgo", "Villa", "adults", "childs", "revenues",]
  return df.to_html(index=False, columns=columns, border=0)



if __name__ == "__main__":

  logging.info('-'*5 + ' ZAK ON ' + '-'*5)

  loadData()

  logging.info('-'*5 + ' ZAK OFF ' + '-'*5)
