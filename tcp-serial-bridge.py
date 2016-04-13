__author__ = 'ceremcem'

from aktos_dcs import *

class SerialPortBridge(SerialPortReader):
    def prepare(self):
        self.client = TcpClient(host="192.168.2.120",
                           port=22334,
                           receiver=self.on_socket_receive)
        self.client.line_ending = ""




    def on_socket_receive(self, data):
        print "Got following data from socket: ", repr(data)
        self.serial_write(data)

    def serial_read(self, data):
        print "From serial port: ", repr(data)
        self.client.socket_write(data)

    def on_connect(self):
        print ""
        print "[[ Device connected... ]]"
        print ""


    def on_disconnect(self):
        print ""
        print "[[ Device disconnected... ]]"
        print ""

    def cleanup(self):
        self.client.cleanup()


SerialPortBridge(port="/dev/ttyUSB0", baud=115200, format="8E1")
wait_all()
