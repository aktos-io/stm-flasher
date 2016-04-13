from aktos_dcs import *
from stm_flasher import StmFlasher
from gevent.queue import Queue


class ConnectionHandler(TcpHandlerActor):
	
    def prepare(self):
        self.flasher = StmFlasher()
        self.flasher.setup_phy = self.setup_phy
        self.flasher.read_phy = self.read_phy
        self.flasher.write_phy = self.write_phy
        self.read_queue = Queue()
        
        
    def setup_phy(self):
        print "Setup the physical connection"
    
    def read_phy(self, count=1):
        chunk = ""
        while True:
            chunk += self.read_queue.get()
            print "Chunk: ", repr(chunk)
            if len(chunk) == count:
                break
                
        return chunk
    
    def write_phy(self, data):
        print "Sending : ", repr(data)
        self.socket_write(data)    
    
    def on_connect(self):
        print "there is a connection!", self.client_id
        print "Preparig to connect stm"
        self.flasher.setup_hardware()
        self.flasher.wait_setup_hardware()
        self.read_queue = Queue()
        self.flasher.upload_firmware('./ch.bin')
        if self.flasher.upload_successful():
            print "Upload is succesful"
        else:
            print "Problem while uploading firmware"
        
    def on_disconnect(self):
        print "client disconnected: ", self.client_id

    def socket_read(self, data):
        print "I got following data: ", repr(data)
        self.read_queue.put(data)

    def action(self):
        pass

print "Started TcpServer on port 1235"
#TcpServerActor(address='0.0.0.0', port=22334)
TcpServerActor(address='0.0.0.0', port=1235, handler=ConnectionHandler)
wait_all()
