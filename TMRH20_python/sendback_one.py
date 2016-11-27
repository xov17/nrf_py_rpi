#!/usr/bin/env python

#
# Central node alternately sends data to 2 different nodes
#

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

# The write addresses of the peripheral nodes
addr_central_rd = [0xF0F0F0F0A1, 0xF0F0F0F0B1]

# The read addresses of the peripheral nodes
addr_central_wr = [0xF0F0F0F0AA, 0xF0F0F0F0BB]


inp_role = 'none'


radio.begin()
radio.enableAckPayload()
radio.enableDynamicPayloads()
radio.setRetries(5,15)
radio.printDetails()

print(' ************ Role Setup *********** ')
while (inp_role !='0') and (inp_role !='1') and (inp_role !='2'):
    inp_role = str(input('Choose a role: Enter 0 for controller, 1 for node1, 2 for node2 CTRL+C to exit) '))



if (inp_role == '0'):
    print('Role: Controller, starting transmission')
    radio.openWritingPipe(addr_central_wr[0])
    radio.openReadingPipe(0, addr_central_rd[0])
    radio.openReadingPipe(1, addr_central_rd[1])
    # TODO: can insert up to 5 readng pipes
    role = "controller"

    counter = 0

elif (inp_role == '1'):
    print('Role: node1 to be accessed, awaiting transmission')
    radio.openWritingPipe(addr_central_rd[0])
    radio.openReadingPipe(0, addr_central_wr[0])
    role = "node"
    counter = 0
elif (inp_role == '2'):
    print('Role: node2 to be accessed, awaiting transmission')
    radio.openWritingPipe(addr_central_rd[1])
    radio.openReadingPipe(0,addr_central_wr[1])
    role = "node"
    counter = 0



radio.startListening()

while 1:
    if (role ==  "controller"):

        radio.stopListening()

        counter = counter + 1
        
        # ping to node 1
        if (counter%2 == 1):
            
            radio.openWritingPipe(addr_central_wr[0])

            data_to_send = str(counter) + ": ping to node 1"
            print('Now sending to Node 1: {}'.format(data_to_send))

            # Writing with auto-acks received
            if (radio.write(data_to_send)):
                if (not radio.available()):
                    print ('Got blank response')
                    
                    radio.startListening()
                    if (radio.available()):
                        result, pipeNo = radio.available_pipe()
                        length = radio.getDynamicPayloadSize()
                        received = radio.read(length)
                        print("From pipe #{}: {}".format(pipeNo, received.decode('utf-8')))

                else:
                    # possibly another pipe sent something
                    result, pipeNo = radio.available_pipe()
                    length = radio.getDynamicPayloadSize()
                    received = radio.read(length)
                    print('Error from pipe #{}: {}'.format(pipeNo, received.decode('utf-8')))

            else:
                # no ack received
                print('Sending failed')

        # ping to node 2
        elif (counter%2 == 0):
            radio.openWritingPipe(addr_central_wr[1])

            data_to_send = str(counter) + ": ping to node 2"
            print('Now sending to Node 2: {}'.format(data_to_send))

            # Writing with auto-acks received
            if (radio.write(data_to_send)):
                if (not radio.available()):
                    print ('Got blank response')
                else:
                    # possibly another pipe sent something
                    result, pipeNo = radio.available_pipe()
                    length = radio.getDynamicPayloadSize()
                    received = radio.read(length)
                    print('Error from pipe #{}: {}'.format(pipeNo, received.decode('utf-8')))
            else:
                # no ack received
                print('Sending failed')


    elif (role == "node"):

        if (radio.available()):
            counter = counter + 1
            result, pipeNo = radio.available_pipe()
            length = radio.getDynamicPayloadSize()
            received = radio.read(length)
            radio.stopListening()
            print('{}: {}'.format(counter, received.decode('utf-8')))
            data_sendback = str(countrer) + ": ACK from node"
            radio.write(data_sendback)
            radio.startListening()

