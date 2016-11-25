#!/usr/bin/env python

#
# Controller/Node0 pings Node1 
# 2 devices only
# Uses auto-ack and auto-retry
# Limit: 32 bytes

from __future__ import print_function
import time
from RF24 import *
import RPi.GPIO as GPIO

irq_gpio_pin = None

# Radio Number: GPIO number, SPI bus 0 or 1
radio = RF24(17,0)

# Unique Identifier for this Node 
# Controller/Node0 = 0
radioNumber = 0
# Node1 = 1
#radioNumber = 1

# Address[0] = writing pipe of controller (pipe 0)
# Address[1:5] = reading pipes of controller
address = [0xF0F0F0F0AA, 0xF0F0F0F0BB]

inp_role = 'none'


radio.begin()
radio.enableAckPayload()
radio.enableDynamicPayloads()
radio.setRetries(5,15)
radio.printDetails()

print(' ************ Role Setup *********** ')
while (inp_role !='0') and (inp_role !='1'):
    inp_role = str(input('Choose a role: Enter 0 for controller 1 for node to be accessed(CTRL+C to exit) '))

if (inp_role == '0'):
    print('Role: Controller, starting transmission')
    radio.openWritingPipe(address[0])
    radio.openReadingPipe(1,address[1])
    # TODO: can insert up to 5 readng pipes
    role = "controller"
else:
    print('Role: node to be accessed, awaiting transmission')
    radio.openWritingPipe(address[1])
    radio.openReadingPipe(1,address[0])
    role = "node"
    counter = 0


radio.startListening()

while 1:
    if (role ==  "controller"):

        radio.stopListening()

        data_to_send = "ping"
        print('Now sending: {}'.format(data_to_send))
        
        # Writing with auto-acks received
        if (radio.write(data_to_send)):
            if (not radio.available()):
                print ('Got blank response')
            else:
                while (radio.available()):
                    #length = radio.getDynamicPayloadSize()
                    received_payload = radio.read(1)
                    print('Got auto-ack: {}'.format(received_payload.decode('utf-8')))
                    
        else:
            # no ack received
            print('Sending failed')
        
        time.sleep(0.1)

    elif (role == "node"):
        if (radio.available()):
            result, pipeNo = radio.available_pipe()
            length = radio.getDynamicPayloadSize()
            received = radio.read(length)
            print('{}: {}'.format(counter, received.decode('utf-8')))
            counter = counter + 1
            ack_payload = counter
            #ack_payload = str(counter)
            #ack_payload = str(counter) + ": got it"
            print('ack_payload: {}'.format(ack_payload))
            radio.writeAckPayload(pipeNo, ack_payload)
            radio.startListening()
            

