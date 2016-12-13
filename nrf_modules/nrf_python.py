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
radio = RF24(17, 0)

# The write addresses of the peripheral nodes
addr_central_rd = [0xF0F0F0F0C1, 0xF0F0F0F0D1]

# The read addresses of the peripheral nodes
addr_central_wr = [0xF0F0F0F0AB, 0xF0F0F0F0BC]

# Not using inp for now
inp_role = 'none'

#Timeout in seconds for the controller to receive msg from node
timeout = 5

def config():
    radio.begin()
    radio.enableAckPayload()
    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.setRetries(5,15)
    radio.printDetails()


