#!/usr/bin/env python

#
# For if cannot OpenCV
#

from __future__ import print_function
import time
import hashlib
from RF24 import *
import RPi.GPIO as GPIO
import ast
import json

from picamera.array import PiRGBArray
from picamera import PiCamera
#import time
import cv2
import numpy as np


import logging

logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s (%(threadName)-2s) %(message)s')

np.set_printoptions(threshold=np.inf)

irq_gpio_pin = None

# Radio Number: GPIO number, SPI bus 0 or 1
radio = RF24(17, 0)

# Unique Identifier for this Node
# Controller/Node0 = 0
radioNumber = 0
# Node1 = 1
#radioNumber = 1

# The write addresses of the peripheral nodes
addr_central_rd = [0xF0F0F0F0C1, 0xF0F0F0F0D1]

# The read addresses of the peripheral nodes
addr_central_wr = [0xF0F0F0F0AB, 0xF0F0F0F0BC]


inp_role = 'none'

timeout = 5



def parsePacket(data_to_send):
    """
        Accepts string
        Returns list of 32 byte strings (if applicable)
        For sending packets
    """
    packet_list = []
    len_data = len(data_to_send)

    i = 0
    while (1):
        starting = i*32
        if (len_data <= 32):
            end = starting + len_data
            packet_list.append(data_to_send[starting:end])
            break
        else:
            end = starting + 32
            packet_list.append(data_to_send[starting:end])
            len_data = len_data - 32
        i = i + 1

    return packet_list

def sendString(data_to_send):
    """
        Description:
            Send string, will detect length of string and send this first. 
            Will also send md5 representation to ensure that the whole string sent was complete :))))
            (16 bytes only for 32 byte string!)
            Will signal end by sending END-SEND
        Inputs:
            Data_to_send: string
            Addr: address to send to
            pipe_read: pipe # to read from
        Return Values:
            Return 1 if sent, 0 if not
    """
    packet_list = []
    hash_orig = hashlib.md5()
    hash_orig.update(data_to_send)
    hash_orig_str = str(hash_orig.hexdigest())
    logging.debug('{}'.format(hash_orig_str))
    logging.debug('len: {}'.format(len(hash_orig_str)))
    packet_list = parsePacket(data_to_send)
    logging.debug('{}'.format(packet_list))
    for i in range(len(packet_list)):
        logging.debug('{}: {}'.format(i, packet_list[i]))
    joined_list = "".join(packet_list)
    logging.debug('{}'.format(joined_list))
    hash_joined = hashlib.md5()
    hash_joined.update(joined_list)
    hash_joined_str = str(hash_joined.hexdigest())
    logging.debug('{}'.format(hash_joined_str))
    logging.debug('{}'.format(len(hash_joined_str)))
    # Sending Command with retry til sent
    cmd_to_send = "SEND-STRING"
    print('Sending SEND-STRING command: {}'.format(cmd_to_send))
    while (1):
        if (radio.write(cmd_to_send)):
            if (not radio.available()):
                node_num = 99
                logging.debug('Sent START-NORMAL to {}'.format(node_num))
                break
            else:
                # possibly another pipe sent something
                result, pipeNo = radio.available_pipe()
                length = radio.getDynamicPayloadSize()
                received = radio.read(length)
                print('Error from pipe #{}: {}'.format(pipeNo, received.decode('utf-8')))
                return 0
                break


    # Sending hash with retry til sent
    hash_to_send = str(hash_orig.hexdigest())
    print('Sending hash: {}'.format(hash_to_send))
    while (1):
        if (radio.write(hash_to_send)):
            if (not radio.available()):
                node_num = 99
                logging.debug('Sent START-NORMAL to {}'.format(node_num))
                break
            else:
                # possibly another pipe sent something
                result, pipeNo = radio.available_pipe()
                length = radio.getDynamicPayloadSize()
                received = radio.read(length)
                print('Error from pipe #{}: {}'.format(pipeNo, received.decode('utf-8')))
                return 0
                break

    # Sending # of packets with retry til sent
    cmd_to_send = "P#:" + str(len(packet_list))
    print ('Sending # of packets: {}'.format(cmd_to_send))
    while (1):
        if (radio.write(cmd_to_send)):
            if (not radio.available()):
                logging.debug('Sent # of packets to {}'.format(node_num))
                break
            else:
                # possibly another pipe sent something
                result, pipeNo = radio.available_pipe()
                length = radio.getDynamicPayloadSize()
                received = radio.read(length)
                print('Error from pipe #{}: {}'.format(pipeNo, received.decode('utf-8')))
                return 0
                break
   
    # Sending packet list
    for i in range(len(packet_list)):
        # Writing with auto-acks received
        if (radio.write(packet_list[i])):
            if (not radio.available()):
                logging.debug('Got blank response')
            else:
                while (radio.available()):
                    #length = radio.getDynamicPayloadSize()
                    received_payload = radio.read(32)
                    logging.debug('Got auto-ack: {}'.format(received_payload.decode('utf-8')))
        else:
            # no ack received
            print('Sending failed')

    # Sending Command with retry til sent
    cmd_to_send = "END-SEND"
    print('Sending END-SEND command: {}'.format(cmd_to_send))
    while (1):
        if (radio.write(cmd_to_send)):
            if (not radio.available()):
                logging.debug('Sent START-NORMAL to {}'.format(node_num))
                break
            else:
                # possibly another pipe sent something
                result, pipeNo = radio.available_pipe()
                length = radio.getDynamicPayloadSize()
                received = radio.read(length)
                print('Error from pipe #{}: {}'.format(pipeNo, received.decode('utf-8')))
                return 0
                break

    #radio.flush_tx()
    return 1



def recvString():
    """
        Description:
            Will receive string based on anticipated length
            Will compile string
            Tiwala muna na di kailangan ng ordering haha
        Inputs:
            Address to read from
            Length of anticipated string
            md5 of anticipated string (16 bytes only for 32 byte string!)
        Return Values:
            Return string if properly received, if not, return Error Recv
    """
    # Waiting for SEND-STRING command
    counter = 0
    print ('Waiting for SEND-STRING')
    while (counter < 10):
        if (radio.available()):
            result, pipeNo = radio.available_pipe()
            length = radio.getDynamicPayloadSize()
            received = radio.read(length)
            logging.debug('{}: {}'.format(counter, received.decode('utf-8')))

            if (received.decode('utf-8') == "SEND-STRING"):
                radio.startListening()
                break
            else:
                counter = counter + 1
            radio.startListening()

    if (counter == 10):
        return "ERROR_RECV: Send-String did not receive"


    # Waiting for hash
    hash_received = ""
    counter = 0
    print ('Waiting for hash')
    while (counter < 10):
        if (radio.available()):
            result, pipeNo = radio.available_pipe()
            length = radio.getDynamicPayloadSize()
            received = radio.read(length)
            print('{}: {}'.format(counter, received.decode('utf-8')))
    
            if (len(received.decode('utf-8')) == 32):
                radio.startListening()
                break
            else:
                counter = counter + 1
            radio.startListening()
    if (counter == 10):
        return "ERROR_RECV: Hash did not receive"

    hash_received = received.decode('utf-8')
    # Waiting for # of packets
    counter = 0
    print ('Waiting for # of packets')
    while (counter < 10):
        if (radio.available()):
            result, pipeNo = radio.available_pipe()
            length = radio.getDynamicPayloadSize()
            received = radio.read(length)
            logging.debug('{}: {}'.format(counter, received.decode('utf-8')))
            received_data = received.decode('utf-8')
            if (received_data[0:3] == "P#:"):
                radio.startListening()
                break
            else:
                logging.debug("{}".format(received_data))
                counter = counter + 1
            radio.startListening()
    if (counter == 10):
        return "ERROR_RECV: # of Packets did not receive"

    packet_list = []
    num_packets = int(received_data[3:len(received_data)])
    # Receiving Packet List
    counter = 0
    print ('Waiting for packet list')
    limit = num_packets + 10
    while (counter < limit):
        if (radio.available()):

            result, pipeNo = radio.available_pipe()
            length = radio.getDynamicPayloadSize()
            received = radio.read(length)
            radio.stopListening()
            received_string = received.decode('utf-8')
            logging.debug('{}: {}'.format(counter, received_string))

            if (received_string == "END-SEND"):
                print ('Got END-SEND')
                break
            else:
                logging.debug("Appending to packet list")
                packet_list.append(received_string)
            counter = counter + 1
            radio.startListening()

    if (counter > num_packets):
        return "ERROR_RECV: Wrong number of packets"

    print ('{}'.format(packet_list))
    joined_list = "".join(packet_list)
    print ('{}'.format(joined_list))
    hash_joined = hashlib.md5()
    hash_joined.update(joined_list)
    hash_joined_str = str(hash_joined.hexdigest())
    if (hash_joined_str == hash_received):
        print ('match!')
        return joined_list
    else:
        return "ERROR_RECV: Wrong hash match"




radio.begin()
radio.enableAckPayload()
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.setRetries(5,15)
radio.printDetails()

print(' ************ Role Setup *********** ')
while (inp_role !='0') and (inp_role !='1') and (inp_role !='2'):
    inp_role = str(input('Choose a role: Enter 0 for controller, 1 for node1, 2 for node2 CTRL+C to exit) '))



if (inp_role == '0'):
    print('Role: Controller, starting transmission')
    # radio.openWritingPipe(addr_central_wr[0])
    radio.openReadingPipe(1, addr_central_rd[0])
    radio.openReadingPipe(2, addr_central_rd[1])
   
    time.sleep(1)
    # TODO: can insert up to 5 readng pipes
    role = "controller"

    counter = 0

elif (inp_role == '1'):
    # HAS OPENCV
    print('Role: node1 to be accessed, awaiting transmission')
    radio.openWritingPipe(addr_central_rd[0])
    radio.openReadingPipe(1, addr_central_wr[0])
     # set up camera
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)

    time.sleep(1)
    role = "node"
    counter = 0
elif (inp_role == '2'):
    print('Role: node2 to be accessed, awaiting transmission')
    radio.openWritingPipe(addr_central_rd[1])
    radio.openReadingPipe(1,addr_central_wr[1])
    time.sleep(1)
    role = "node"
    counter = 0

radio.startListening()

got_msg = 0
startNormalOperation = 0

pipeNo = 0
result = 0
# to accomodate for the 6 reading pipes/nodes
found_nodes = [0, 0, 0 ,0 ,0 ,0]

# detect live nodes
# retries 3 times 
if (role == "controller"):

    radio.stopListening()

    # test node 1
    radio.openWritingPipe(addr_central_wr[0])
    time.sleep(1)

    #radio.openReadingPipe(0, addr_central_rd[0])
    data_to_send = "Node 1 found by controller"
    print('Finding Node 1 w/ msg: {}'.format(data_to_send))

    # Writing with auto-acks received
    counter = 0
    while (counter < 3):
        time.sleep(1)
        radio.write(data_to_send)
        if (radio.txStandBy(2000)):
        #if (radio.write(data_to_send)):
            if (radio.available()):
                length = radio.getDynamicPayloadSize()
                received = radio.read(length)
                print('AP: {}: {}'.format(counter, received.decode('utf-8')))
                print ('Node 1 confirmed')
                found_nodes[0] = 1
                break
            #elif (not radio.isAckPayloadAvailable()):
            #    print ('Node 1 confirmed')
            else:
                # possibly another pipe sent something
                #result, pipeNo = radio.available_pipe()
                #length = radio.getDynamicPayloadSize()
                #received = radio.read(length)
                #print('Error from pipe #{}: {}'.format(pipeNo, #received.decode('utf-8')))
                #length = radio.getDynamicPayloadSize()
                #received = radio.read(length)
                #print('AP: {}: {}'.format(counter, received.decode('utf-8')))
                print('Sent Did not find node 1')
                found_nodes[0] = 0
                #radio.closeReadingPipe(0)
                counter = counter + 1
        else:
            # no ack received or error
            print('Did not find node 1')
            found_nodes[0] = 0
            counter = coutner + 1
            
    if (found_nodes[0] == 0):
        radio.closeReadingPipe(1)
  
    #time.sleep(2)
    # test node 2
    radio.openWritingPipe(addr_central_wr[1])
    time.sleep(1)
   
    #radio.openReadingPipe(1, addr_central_rd[1])
    data_to_send = "Node 2 found by controller"
    print('Finding Node 2 w/ msg: {}'.format(data_to_send))
    counter = 0
    # Writing with auto-acks received
    while (counter < 3):
        time.sleep(1)
        radio.write(data_to_send)
        if (radio.txStandBy(2000)):
        #if (radio.write(data_to_send)):
            if (radio.available()):
                length = radio.getDynamicPayloadSize()
                received = radio.read(length)
                print('AP: {}: {}'.format(counter, received.decode('utf-8')))
                print ('Node 2 confirmed')
                found_nodes[1] = 1
                break
            #elif (not radio.isAckPayloadAvailable()):
            #    print ('Node 2 confirmed')
            #    found_nodes[1] = 1
            else:
                # possibly another pipe sent something
                #result, pipeNo = radio.available_pipe()
                #length = radio.getDynamicPayloadSize()
                #received = radio.read(length)
                #print('Error from pipe #{}: {}'.format(pipeNo, received.decode('utf-8')))
                #radio.flush_tx()
                print('Sent but Did not find node 2')
                found_nodes[1] = 0
                counter = counter + 1
                #radio.closeReadingPipe(1)
        else:
            # no ack received or error 
            print('Did not find node 2')
            found_nodes[1] = 0
            counter = counter + 1
    
    if (found_nodes[1] == 0):
        radio.closeReadingPipe(2)

    # Send init messages from controller
    for node_num in range(len(found_nodes)):
        if found_nodes[node_num]:
            radio.openWritingPipe(addr_central_wr[node_num])
            #time.sleep(1) 
            #radio.flush_tx()
            #time.sleep(2)
            data_to_send = "START-NORMAL"
            print('Sending Init Cmd to Nodes: {}'.format(data_to_send))
            while (1):
                if (radio.write(data_to_send)):
                    if (not radio.available()):
                        print ('Sent START-NORMAL to {}'.format(node_num))
                        break
                    else:
                        # possibly another pipe sent something
                        result, pipeNo = radio.available_pipe()
                        length = radio.getDynamicPayloadSize()
                        received = radio.read(length)
                        print('Conf of START-NORMAL {}: {}'.format(pipeNo, received.decode('utf-8')))
                        break
# Have now identified nodes from the side of the controller
# Responses of node
# Initialization of nodes
counter = 0
ack_start = 0
if (role == "node"):
    print ('Waiting for START-NORMAL')
    ack_payload = "1st Ack Payload from " + str(inp_role)
    radio.writeAckPayload(1, ack_payload)
    while (1):
        if (ack_start == 1):
            ack_payload = "2nd Ack Payload from " + str(inp_role)
            radio.writeAckPayload(1, ack_payload)
            ack_start = 0
        if (radio.available()):
            result, pipeNo = radio.available_pipe()
            length = radio.getDynamicPayloadSize()
            received = radio.read(length)
            logging.debug('{}: {}'.format(counter, received.decode('utf-8')))
            if (received.decode('utf-8') == "START-NORMAL"):
                print ('Received START-NORMAL')
                break
            radio.startListening()
            ack_start = 1

# Main while loop
# Operation: 
# Controller sends REQ commands to nodes
# Nodes send data to controller
# Nodes wait again for req commands

# sending of controller
while 1:
    if (role ==  "controller"):

        radio.stopListening()

        counter = counter + 1
        
        # ping to node 1 HAS OPENCV
        if (counter%2 == 1) and (found_nodes[0] == 1):
            
            radio.openWritingPipe(addr_central_wr[0])
            #time.sleep(1)
            data_to_send = "REQ-DATA"
            #data_to_send = "Someday we'll know, why I wasn't made for you"
            print('Now sending to Node 1: {}'.format(data_to_send))

            # Send send string
            if (sendString(data_to_send)):
                print('Sent string!')
                radio.startListening()
                response = recvString()
                print ('Reponse: {}'.format(response))

                # PROCESS THE SAME IMAGE TO COMPARE
                img = cv2.imread("Lenna.png")
                #rawCapture.truncate(0)
                win_size = (64, 128)
                img = cv2.resize(img, win_size)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                hog = cv2.HOGDescriptor()
                h = hog.compute(img)
                data_to_compare = json.dumps(h.tolist())

                if (data_to_comare == response):
                    print ("MATCH on same picture!")
                else:
                    print("Was not a match")

                #print "Errors: ", i, " lines"
                #print "Accuracy: ", float(((3780-i)/3780)*100), " percent"
            else:
                print ('Did not send string')


        # ping to node 2 JUST RECEIVES DATA
        elif (counter%2 == 0) and (found_nodes[1] == 1):
            radio.openWritingPipe(addr_central_wr[1])
            #time.sleep(1)
            data_to_send = "REQ-DATA"
            #data_to_send = "90 miles outside Chicago, can't stop driving, I don't know why. So many questions, I need an answer. Two years later, you're still on my mind."
            print('Now sending to Node 2: {}'.format(data_to_send))
            if (sendString(data_to_send)):
                print('Sent string!')
                radio.startListening()
                response = recvString()
                print ('Reponse: {}'.format(response))
                
            else:
                print ('Did not send string')
               


    elif (role == "node"):

        response = recvString()

        # Now send requested data
        if (response == "REQ-DATA"):
            print ("RECEIVED REQ-DATA")
            radio.stopListening()
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
                
                if (sendString(data_to_send)):
                    print('Sent string!')
                else:
                    print ('Did not send string')
            elif (inp_role =='2'):
                data_to_send = "90 miles outside Chicago, can't stop driving, I don't know why. So many questions, I need an answer. Two years later, you're still on my mind."
                print('Now sending to controller: {}'.format(data_to_send))
                if (sendString(data_to_send)):
                    print('Sent string!')
                else:
                    print ('Did not send string')
            else:
                print ("Invalid inp_role")
        else:
            print ('Else: Received on Node: {}'.format(response))
        radio.startListening()