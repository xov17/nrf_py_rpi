
#TMRh20 2014 - Updated to work with optimized RF24 Arduino library


# Python version
# Example for efficient call-response using ack-payloads
#
# This example continues to make use of all the normal functionality of the radios including
# the auto-ack and auto-retry features, but allows ack-payloads to be written optionlly as well.
# This allows very fast call-response communication, with the responding radio never having to
# switch out of Primary Receiver mode to send back a payload, but having the option to switch to
# primary transmitter if wanting to initiate communication instead of respond to a commmunication.
#


from __future__ import print_function
import time
from RF24 import *
import RPi.GPIO as GPIO

irq_gpio_pin = None

radio = RF24(17, 0);
