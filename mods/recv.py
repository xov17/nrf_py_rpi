#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example program to receive packets from the radio link
#

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from lib_nrf24 import NRF24
import time
import spidev



pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio2 = NRF24(GPIO, spidev.SpiDev())
radio2.begin(0, 17)

radio2.setRetries(15,15)

radio2.setPayloadSize(32)
radio2.setChannel(0x60)
radio2.setDataRate(NRF24.BR_2MBPS)
radio2.setPALevel(NRF24.PA_MIN)

radio2.setAutoAck(True)
radio2.enableDynamicPayloads()
radio2.enableAckPayload()

radio2.openWritingPipe(pipes[0])
radio2.openReadingPipe(1, pipes[1])

radio2.startListening()
radio2.stopListening()

radio2.printDetails()

radio2.startListening()

c=1
while True:
    akpl_buf = [c,1, 2, 3,4,5,6,7,8,9,0,1, 2, 3,4,5,6,7,8]
    pipe = [0]
    print "before sleep"
    while not radio2.available(pipe):
        time.sleep(10000/1000000.0)

    print "after sleep"
    recv_buffer = []
    radio2.read(recv_buffer, radio2.getDynamicPayloadSize())
    print ("Received:")
    print (recv_buffer)
    recv_buffer_str = ''.join(map(chr, recv_buffer))
    recv_list = map(chr, recv_buffer)
    print recv_buffer_str
    print recv_list

    if recv_buffer_str[0] == '!':
        new_list = ""
        list = 1

    if list == 1:
        new_list += recv_buffer_str
        if recv_buffer_str[len(recv_buffer_str)-1] == '?':
            print "New list:" +  new_list
            list = 0
    c = c + 1
    radio2.writeAckPayload(1, akpl_buf, len(akpl_buf))
    print ("Loaded payload reply:"),
    print (akpl_buf)

