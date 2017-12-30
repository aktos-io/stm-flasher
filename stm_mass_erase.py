#Look AN3155 for full usart protocol
#http://www.st.com/content/ccc/resource/technical/document/application_note/51/5f/03/1e/bd/9b/45/be/CD00264342.pdf/files/CD00264342.pdf/jcr:content/translations/en.CD00264342.pdf

import serial
from os import stat

serial_desc = None

print("Assuming device mounted on:/dev/ttyUSB0")
print("Assuming correct boot mode is selected via boot pins")

#add an automated finder or take from user
serial_desc = serial.Serial("/dev/ttyUSB0",115200,parity=serial.PARITY_EVEN)
if serial_desc.is_open == False:
	print("Cannot open serial port control the connection")
	exit(-4)

print("Initializing connection")
serial_desc.write("\x7f")

ans = serial_desc.read()

if ans != "\x79":
	print("Cannot initialize connection, be sure you use correct usart port")
	exit(-1)

print("Connection initialized")

serial_desc.write("\x43\xbc")
ans = serial_desc.read()

if ans != "\x79":
	print("Cannot initiate erase functionality")
	exit(-2)

print("Erase function is called")

serial_desc.write("\xff\x00")
ans = serial_desc.read()
if ans != "\x79":
	print("Something went wrong while erasing")
	exit(-3)

print("All flash is erased, bye")

