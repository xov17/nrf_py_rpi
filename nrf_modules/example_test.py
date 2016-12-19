#!/usr/bin/env python

#
# Central node alternately sends data to 2 different nodes
#

from __future__ import print_function
import time
import hashlib
from RF24 import *
import RPi.GPIO as GPIO
import ast
import json
import nrf_python


import logging

logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s (%(threadName)-2s) %(message)s')

from picamera.array import PiRGBArray
from picamera import PiCamera


#import time
import cv2
import numpy as np




np.set_printoptions(threshold=np.inf)

nrf_python.config()

inp_role, role = nrf_python.userDefineRoles()

got_msg = 0
startNormalOperation = 0

pipeNo = 0
result = 0

# detect live nodes
# retries 3 times 

nrf_python.findNodes()
if (role == "controller"):
    nrf_python.findNodes()
    nrf_python.sendStartNormal()
    
# Have now identified nodes from the side of the controller
# Responses of node
# Initialization of nodes
if (role == "node"):
    nrf_python.waitStartNormal()

# Main while loop
# Operation: 
# Controller sends REQ commands to nodes
# Nodes send data to controller
# Nodes wait again for req commands

# sending of controller
while 1:
    if (role ==  "controller"):

        nrf_python.radio.stopListening()

        counter = counter + 1
        
        # ping to node 1
        if (counter%2 == 1) and (found_nodes[0] == 1):
            
            nrf_python.radio.openWritingPipe(addr_central_wr[0])
            #time.sleep(1)
            data_to_send = "REQ-DATA"
            #data_to_send = "Someday we'll know, why I wasn't made for you"
            print('Now sending to Node 1: {}'.format(data_to_send))

            # Send send string
            if nrf_python.sendString(data_to_send):
                print('Sent string!')
                nrf_python.radio.startListening()
                response = nrf_python.recvString()
                print ('Reponse: {}'.format(response))
                rec_nparr = np.array(json.loads(response))
                print('Array ver: {} {}'.format(rec_nparr, len(rec_nparr)))
            else:
                print ('Did not send string')


        # ping to node 2
        elif (counter%2 == 0) and (nrf_python.found_nodes[1] == 1):
            nrf_python.radio.openWritingPipe(addr_central_wr[1])
            #time.sleep(1)
            data_to_send = "REQ-DATA"
            #data_to_send = "90 miles outside Chicago, can't stop driving, I don't know why. So many questions, I need an answer. Two years later, you're still on my mind."
            print('Now sending to Node 2: {}'.format(data_to_send))
            if (sendString(data_to_send)):
                print('Sent string!')
                nrf_python.radio.startListening()
                response = nrf_python.recvString()
                print ('Reponse: {}'.format(response))
                
            else:
                print ('Did not send string')
               


    elif (role == "node"):

        response = nrf_python.recvString()

        # Now send requested data
        if (response == "REQ-DATA"):
            print ("RECEIVED REQ-DATA")
            nrf_python.radio.stopListening()
            time.sleep(5)
            if (inp_role == '1'):
                #camera.capture(rawCapture, format = "bgr")
                #img = rawCapture.array
                img = cv2.imread("Lenna.png")
                #rawCapture.truncate(0)
                win_size = (64, 128)
                img = cv2.resize(img, win_size)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                hog = cv2.HOGDescriptor()
                h = hog.compute(img)
                data_to_send = json.dumps(h.tolist())
                #data_to_send = np.array_str(h)
                
                #data_to_send = str(h)
                #test_npparr = np.fromstring(data_to_send, np.uint8)
                #data_to_send = "Someday we'll know, why I wasn't made for you"
                ('Now sending to controller: {}'.format(data_to_send))
                logging.debug('The h: {}'.format(h))
                #test_nparr = ast.literal_eval(data_to_send)
                test_nparr = np.array(json.loads(data_to_send))
                logging.debug('Array ver: {} {}'.format(test_nparr, len(test_nparr)))
                #data_to_send = "Someday we'll know, why I wasn't made for you"
                
                if (nrf_python.sendString(data_to_send)):
                    print('Sent string!')
                else:
                    print ('Did not send string')
            elif (inp_role =='2'):
                data_to_send = "90 miles outside Chicago, can't stop driving, I don't know why. So many questions, I need an answer. Two years later, you're still on my mind."
                print('Now sending to controller: {}'.format(data_to_send))
                if (nrf_python.sendString(data_to_send)):
                    print('Sent string!')
                else:
                    print ('Did not send string')
            else:
                print ("Invalid inp_role")
        else:
            print ('Else: Received on Node: {}'.format(response))
        nrf_python.radio.startListening()
