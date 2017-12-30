#!/usr/bin/python

"""
Mass erase over USART1 while boot0 is wired to VDD while powering up


See AN3155 for full usart protocol
http://www.st.com/content/ccc/resource/technical/document/application_note/51/5f/03/1e/bd/9b/45/be/CD00264342.pdf/files/CD00264342.pdf/jcr:content/translations/en.CD00264342.pdf
"""

import serial
from os import stat

print("1. Assuming serial port on host is: /dev/ttyUSB0")
print("2. Assuming correct Boot0 pin of the MCU is connected to VDD while powering up")
print("3. Assuming correct MCU.USART port (USART1) is being used.")
print('(Refer the AN3155 for further details)')
print "----------------------------------------------------------------"

# TODO: add an automated finder or take from user
s = serial.Serial()
s.port = "/dev/ttyUSB0"
s.baudrate = 115200
s.parity=serial.PARITY_EVEN
s.timeout = 2  # seconds
s.open()

if not s.is_open:
    print("Cannot open serial port control the connection")
    exit(-4)

print("Initializing connection")
s.write("\x7f")
if s.read() != "\x79":
	print("Cannot initialize connection with the MCU")
	exit(-1)
print("Connection initialized")

print "Initiating erase function..."
s.write("\x43\xbc")
if s.read() != "\x79":
	print("Cannot initiate erase functionality")
	exit(-2)

print("Calling erase function...")
s.write("\xff\x00")
if s.read() != "\x79":
	print("Something went wrong while erasing")
	exit(-3)

print("All flash is erased, bye")
