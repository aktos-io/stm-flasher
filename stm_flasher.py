import serial
import struct 
from os import stat

from aktos_dcs import *


class StmCommand():
    ack = "\x79"
    nack = "\x1F"
    init = "\x7F"
    get = "\x00\xFF"
    get_version = "\x01\xFE"
    get_id = "\x02\xFD"
    read_mem = "\x11\xEE"
    go = "\x21\xDE"
    write_mem = "\x31\xCE"
    erase = "\x43\xBC"
    extended_erase = "\x44\xBB"
    w_protect = "\x63\x9C"
    w_unprotect = "\x73\x8C"
    r_protect = "\x82\x7D"
    r_unprotect = "\x92\x6D"
    hex255 = "\xFF\x00"
    mass_erase = "\xFF\xFF\x00"

class StmFlasher(object):

    def __init__(self):
        object.__init__(self)
        self.is_connected = False
        self.firmware_file = "ch.bin"
        self.downloaded_firmware = "dump.bin"
        self.upload_progress_ended = Barrier()
        
        
    def setup_phy(self):  
        self.setup_local_uart()
        
    def read_phy(self, count=1):
        return self.ser.read(count)
    
    def write_phy(self, data):
        self.ser.write(data)

    def close_phy(self):
        try:
            self.ser.close()
        except:
            pass

    def setup_local_uart(self, port="/dev/ttyUSB0"):
        self.ser = None
        print("Assuming device mounted on: %s" % port)

        #add an automated finder or take from user
        self.ser = serial.Serial("/dev/ttyUSB0",115200,parity=serial.PARITY_EVEN)
        if self.ser.isOpen() == False:
            raise Exception("Cannot open serial port control the connection please.")



    def setup_hardware(self, phy_layer="uart"):
        """
        :param phy_layer:
            physical layer can be one of "uart", "can", "spi"
        :return:
        """
        print "Manually setup the hardware: "
        print " 0. Make physical layer connection over %s" % phy_layer
        self.setup_phy()
        print " 1. Set `HIGH` the `Boot0` pin"
        print " 2. Send a negative pulse to `NRST` pin (`LOW` for a while, then `HIGH`)"

    def wait_setup_hardware(self):
        while True:
            print "Type 'ready' when ready: "
            i = raw_input()
            if i == "ready\n":
                break
            sleep(0)

    def upload_firmware(self, file_path=None):
        if file_path is not None:
            self.firmware_file = file_path
        self.init_connection()
        self.flash_firmware(self.firmware_file)

    def upload_successful(self, timeout=0):
        success = self.upload_progress_ended.wait(timeout)
        return success

    def verify_firmware(self, file_path=None):
        if file_path is not None:
            self.firmware_file = file_path

        firmware_size = stat(self.firmware_file).st_size
        print "Reading %d bytes of flash..." % firmware_size
        self.download_firmware(size=firmware_size)
        import filecmp
        return filecmp.cmp(self.firmware_file, self.downloaded_firmware)

    def download_firmware(self, file_path=None, size=None):
        if file_path is not None:
            self.downloaded_firmware = file_path
        return self.read_memory(size)

    def return_hex(data):
        return lambda x:"".join([hex(ord(c))[2:].zfill(2) for c in x])

    #TODO: review this function
    def calc_checksum(self, package):
        if type(package) == int:
            #this is xor checksum
            checksum = 0
            while package != 0:
                checksum = checksum ^ (package & 0xFF)
                package = package>>8
        elif type(package) == str:
            checksum = 0
            for c in package:
               checksum = checksum ^ ord(c)

        return struct.pack(">B",checksum)


    def init_connection(self):

        self.write_phy(StmCommand.init)

        ans = self.read_phy()
        if ans == StmCommand.ack:
            print("Connected to device.\n")
            is_connected = True
        elif ans == StmCommand.nack:
            print("Cannot connected to device check BOOT configuration and reset device")
            self.close_phy()
        else:
            print("Unexpected answer, closing port. Check connections.")
            self.close_phy()

    def get_ID(self):
        self.write_phy(StmCommand.get_id)
        ans = self.read_phy()
        if ans == StmCommand.nack:
            print("Something went wrong please try again")
            return
        #if it's not nack then it's ack

        toRead = self.read_phy() #learn how many bytes to read
        device_id = self.read_phy(2)
        self.read_phy()#last ack means nothing

        print("ID of device is " + device_id.encode("hex"))
        return

    def read_memory(self, size=None):
        fd = open(self.downloaded_firmware, "wb")
        #careful it's just for F030X4
        # TODO: Get id and decide the address by id
        size = size if size is not None else 0x4000

        start_address = 0x08000000
        end_address = start_address + size

        current_address = start_address

        max_chunk_size = 256
        last_chunk_size = size % max_chunk_size
        while current_address < end_address:

            if last_chunk_size > 0:
                if current_address + last_chunk_size == end_address:
                    print "this is last chunk"
                    max_chunk_size = last_chunk_size
                    
            self.write_phy(StmCommand.read_mem)
            ans = self.read_phy()
            if ans == StmCommand.nack:
                print("Check if read protection off.")
                return
            #else its ack then
            self.write_phy(struct.pack(">i",current_address))#send address
            self.write_phy(self.calc_checksum(current_address))#and it's checksum

            ans = self.read_phy()#wait for ack
            #print("ack to address " + ans.encode("hex"))
            if ans == StmCommand.nack:
                #maybe data corrupted, try again
                pass
            self.write_phy(StmCommand.hex255)
            self.read_phy()#ack to size
            #print("waiting for data")
            #wait for 256 bytes of data
            data = self.read_phy(max_chunk_size)
            #print("received data " + data.encode("hex"))
            #check this
            fd.write(data)
            current_address += max_chunk_size
            print(hex(current_address))
        fd.close()

    def global_erase(self):
        print("Mass erasing")
        self.write_phy(StmCommand.extended_erase)
        ans = self.read_phy()#ack to erase
        if ans == StmCommand.nack:
            print("Somethin went wrong while mass erasing")
            return

        self.write_phy(StmCommand.mass_erase)
        self.read_phy()#unimportant ack
        print("Done.")

    def flash_firmware(self, file_path):
        #TODO: add decoders for hex elf etc.
        file_length = stat(file_path).st_size
        with open(file_path, "rb") as fd:
            print("Starting to flash")
            #address for just stm32f0
            start_address = 0x08000000
            end_address   = 0x08004000
            current_address = start_address

            while current_address < end_address and fd.tell() < file_length:
                print("Writing to " + str(hex(current_address)))
                self.write_phy(StmCommand.write_mem)
                ans = self.read_phy()
                if ans == StmCommand.nack:
                    print("Protection may be active, cannot write")
                    #TODO: try to deactivate protection
                    return

                self.write_phy(struct.pack(">i", current_address))#address
                self.write_phy(self.calc_checksum(current_address))#and it's checksum

                ans = self.read_phy()#ack of address
                if ans == StmCommand.nack:
                    #maybe address got corrupted while transmitting, try again
                    pass

                #try to read 256 bytes
                data_buffer = fd.read(256)

                #if readed data bytes are not multiple of 4 then make it be
                if len(data_buffer) % 4 != 0:
                    data_buffer += (4 - len(data_buffer)) * '\x00'

                data_buffer = chr(len(data_buffer) - 1) + data_buffer
                checksum = self.calc_checksum(data_buffer)
                data_buffer = data_buffer + checksum
                self.write_phy(data_buffer)
                print(self.read_phy())#last ack
                current_address += 256

            self.upload_progress_ended.go()


if __name__ == "__main__":
    def print_menu():
        print("""
            0)Exit
            1)Init Connection
            2)Send Get command
            3)Get Version and Read Protection
            4)Get ID
            5)Read Memory
            6)Global Erase
            7)Write to Flash
            """)
        return raw_input()

    while True:
        selection = print_menu()
        if selection == "1":
            init_connection()

        if selection == "2":
            pass
        elif selection == "3":
            pass
        elif selection == "4":
            get_ID()
        elif selection == "5":
            read_memory()
        elif selection == "6":
            global_erase()
        elif selection == "7":
            flash_and_verify()
        elif selection == "0":
            serial_desc.close()
            break
