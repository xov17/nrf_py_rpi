#!/usr/bin/env python

#
# Central node alternately requests data from the two nodes
# Assumes that all three RPIs have OpenCV

from __future__ import print_function
import time
import hashlib
from RF24 import *
import RPi.GPIO as GPIO
import ast
import json
import pynrf24_wcam_new as nrf

from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np

import logging

logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s (%(threadName)-2s) %(message)s')


np.set_printoptions(threshold=np.inf)

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
            time_now = time.time()
            if (nrf.sendString(data_to_send)):
                print('Sent string!')
                nrf.radio.startListening()
                response = nrf.recvString()
                if (len(response) <= 32):
                    print('Reponse: {}'.format(response))
                else:
                    logging.debug('Reponse: {}'.format(response))
                time_received = time.time() - time_now
                print("Time Elapsed: {}".format(str(time_received)))
                # PROCESS THE SAME IMAGE TO COMPARE
                img = cv2.imread("Lenna.png")
                #rawCapture.truncate(0)
                win_size = (64, 128)
                img = cv2.resize(img, win_size)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                hog = cv2.HOGDescriptor()
                h = hog.compute(img)
                data_to_compare = json.dumps(h.tolist())
                list_to_compare = np.array(json.loads(data_to_compare))
                
                logging.debug("Data_to_compare:{}".format(response))
                if (data_to_compare == response):
                    print ("MATCH on same picture!")
                else:
                    print("May have small significant figure differences")
                recv_arr = np.array(json.loads(response))

                right = 0
                wrong = 0
                print ("Now comparing arrays)")
                # Compare h & recv_arr
                for x in range(len(list_to_compare)):
                    temp_comp = str(list_to_compare[x])
                    temp_comp = temp_comp[0:3]
                    temp_recv = str(recv_arr[x])
                    temp_recv = temp_recv[0:3]
                    if (temp_recv == temp_comp):
                        right = right + 1
                        logging.debug("Right on: \nlist_to_compare[{}]: {}\nrecv_arr[{}]: {}\n".format(x, list_to_compare[x], x, recv_arr[x]))
                    else:
                        wrong = wrong + 1
                        print("Wrong on: \nlist_to_compare[{}]: {}\nrecv_arr[{}]: {}\n".format(x, list_to_compare[x], x, recv_arr[x]))

                print ("Errors: {}".format(wrong))
                accuracy = (right/len(h))*100
                print ("Accuracy: {}%".format(accuracy))

        # ping to node 2
        elif (counter%2 == 0) and (nrf.found_nodes[1] == 1):
            nrf.radio.openWritingPipe(nrf.addr_central_wr[1])
            data_to_send = "REQ-DATA"
            print('Now sending to Node 2: {}'.format(data_to_send))
            time_now = time.time()
            if (nrf.sendString(data_to_send)):
                print('Sent string!')
                nrf.radio.startListening()
                response = nrf.recvString()
                print ('Reponse: {}'.format(response))
                time_received = time.time() - time_now
                print("Time Elapsed: {}".format(str(time_received)))

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
                ('Now sending to controller: {}'.format(data_to_send))
                logging.debug('The h: {}'.format(h))
                test_nparr = np.array(json.loads(data_to_send))
                logging.debug('Array ver: {} {}'.format(test_nparr, len(test_nparr)))

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
