#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from private import *
import xmlrpc.client

server = xmlrpc.client.Server(url)
returnCode, token= server.acquire_token(user, password, pkey)

props = server.fetch_properties(token)
lcode = props[0]['lcode']


resvs = server.fetch_reservations_day(token, lcode, "15/07/2017")


# Chiudere
server.release_token(token)
