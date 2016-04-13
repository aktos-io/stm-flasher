#!/usr/bin/env python
# coding: utf-8

from aktos_dcs import *

class TerminalEmulator(SerialPortReader):
    def prepare(self):
        print "started terminal emulator..."
        print "-----------------------------"
        print self.ser
        self.line_endings = "\n"

    def on_disconnect(self):
        print ""
        print "[[ Device Physically Disconnected... ]]"
        print ""

    def on_connecting(self):
        print ""
        while True:
            print "[[ Waiting for Device to be physically connected... ]]"
            sleep(30)

    def on_connect(self):
        print ""
        print "[[ Device Physically Connected... ]]"
        print ""

    def serial_read(self, data):
        print "Got following data: ", repr(data)


TerminalEmulator(port="/dev/ttyUSB0", baud=115200, format="8E1")
wait_all()
