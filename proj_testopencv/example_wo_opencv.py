#!/usr/bin/env python

#
# Central node alternately requests data from the two nodes
# For the node without opencv to run

from __future__ import print_function
import time
import hashlib
from RF24 import *
import RPi.GPIO as GPIO
import ast
import json
import pynrf24 as nrf


import logging

logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s (%(threadName)-2s) %(message)s')



nrf.config()

inp_role, role = nrf.userDefineRoles()

got_msg = 0
startNormalOperation = 0

pipeNo = 0
result = 0

# detect live nodes
# retries 3 times 
if (role == "controller"):
    nrf.findNodes()
    nrf.sendStartNormal()
# Have now identified nodes from the side of the controller
# Responses of node
# Initialization of nodes
if (role == "node"):
    nrf.waitStartNormal()

# Main while loop
# Operation:
# Controller sends REQ commands to nodes
# Nodes send data to controller
# Nodes wait again for req commands

counter = 0
# sending of controller
while 1:
    if (role ==  "controller"):

        nrf.radio.stopListening()

        counter = counter + 1

        # ping to node 1
        if (counter%2 == 1) and (nrf.found_nodes[0] == 1):
            nrf.radio.openWritingPipe(nrf.addr_central_wr[0])
            data_to_send = "REQ-DATA"
            print('Now sending to Node 1: {}'.format(data_to_send))

            # Send send string
            if nrf.sendString(data_to_send):
                print('Sent string!')
                nrf.radio.startListening()
                response = nrf.recvString()
                print ('Reponse: {}'.format(response))
            else:
                print ('Did not send string')


        # ping to node 2
        elif (counter%2 == 0) and (nrf.found_nodes[1] == 1):
            nrf.radio.openWritingPipe(nrf.addr_central_wr[1])
            data_to_send = "REQ-DATA"
            print('Now sending to Node 2: {}'.format(data_to_send))
            if (nrf.sendString(data_to_send)):
                print('Sent string!')
                nrf.radio.startListening()
                response = nrf.recvString()
                print ('Reponse: {}'.format(response))

            else:
                print ('Did not send string')

    elif (role == "node"):

        response = nrf.recvString()

        # Now send requested data
        if (response == "REQ-DATA"):
            print ("RECEIVED REQ-DATA")
            nrf.radio.stopListening()
            time.sleep(5)
            if (inp_role == '1'):
                
                data_to_send = "Node 1 with no OpenCV data"
                ('Now sending to controller: {}'.format(data_to_send))
                logging.debug('The h: {}'.format(h))
              
                if (nrf.sendString(data_to_send)):
                    print('Sent string!')
                else:
                    print ('Did not send string')
            elif (inp_role =='2'):
                data_to_send = "90 miles outside Chicago, can't stop driving, I don't know why. So many questions, I need an answer. Two years later, you're still on my mind."
                print('Now sending to controller: {}'.format(data_to_send))
                if (nrf.sendString(data_to_send)):
                    print('Sent string!')
                else:
                    print ('Did not send string')
            else:
                print ("Invalid inp_role")
        else:
            print ('Else: Received on Node: {}'.format(response))
        nrf.radio.startListening()
