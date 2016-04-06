import serial
import struct 
from os import stat

serial_desc = None
is_connected = False
command_set = {"ack": "\x79",
               "nack":"\x1F",
               "init":"\x7F",
               "get": "\x00\xFF",
               "get_version": "\x01\xFE",
               "get_id": "\x02\xFD",
               "read_mem": "\x11\xEE",
               "go": "\x21\xDE",
               "write_mem": "\x31\xCE",
               "erase": "\x43\xBC",
               "extended_erase": "\x44\xBB",
               "w_protect": "\x63\x9C",
               "w_unprotect": "\x73\x8C",
               "r_protect": "\x82\x7D",
               "r_unprotect": "\x92\x6D",
               "255": "\xFF\x00",
               "mass erase": "\xFF\xFF\x00"}


def return_hex(data):
    return lambda x:"".join([hex(ord(c))[2:].zfill(2) for c in x])

#TODO: review this function 
def calc_checksum(package):
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

def open_port():
    global serial_desc
    print("Assuming device mounted on:/dev/ttyUSB0")
    
    #add an automated finder or take from user
    serial_desc = serial.Serial("/dev/ttyUSB0",115200,parity=serial.PARITY_EVEN)
    if serial_desc.is_open == False:
        print("Cannot open serial port control the connection please.")

def init_connection():
    
    open_port()
    serial_desc.write(command_set["init"])

    ans = serial_desc.read()
    if ans == command_set["ack"]:
        print("Connected to device.\n")
        is_connected = True
    elif ans == command_set["nack"]:
        print("Cannot connected to device check BOOT configuration and reset device")
        serial_desc.close()
    else:
        print("Unexpected answer, closing port. Check connections.")
        serial_desc.close()

def get_ID():
    serial_desc.write(command_set["get_id"])
    ans = serial_desc.read()
    if ans == command_set["nack"]:
        print("Something went wrong please try again")
        return
    #if it's not nack then it's ack
    
    toRead = serial_desc.read() #learn how many bytes to read
    device_id = serial_desc.read(2)
    serial_desc.read()#last ack means nothing
    
    print("ID of device is " + device_id.encode("hex"))
    return

def read_memory():
    print("Reading entire flash memory and write it to dump.bin")
    fd = open("dump.bin", "wb")
    #careful it's just for F030X4
    # TODO: Get id and decide the address by id 
    start_address = 0x08000000
    end_address   = 0x08004000
    current_address = start_address
    
    while current_address < end_address:
        serial_desc.write(command_set["read_mem"])
        ans = serial_desc.read()
        if ans == command_set["nack"]:
            print("Check if read protection off.")
            return
        #else its ack then
        serial_desc.write(struct.pack(">i",current_address))#send address
        serial_desc.write(calc_checksum(current_address))#and it's checksum
        
        ans = serial_desc.read()#wait for ack
        #print("ack to address " + ans.encode("hex"))
        if ans == command_set["nack"]:
            #maybe data corrupted, try again
            pass
        serial_desc.write(command_set["255"])
        serial_desc.read()#ack to size
        #print("waiting for data")
        #wait for 256 bytes of data
        data = serial_desc.read(256)
        #print("received data " + data.encode("hex"))
        #check this
        fd.write(data)
        current_address += 256
        print(hex(current_address))
    fd.close()
    
def global_erase():
    print("Mass erasing")
    serial_desc.write(command_set["extended_erase"])
    ans = serial_desc.read()#ack to erase
    if ans == command_set["nack"]:
        print("Somethin went wrong while mass erasing")
        return
        
    serial_desc.write(command_set["mass erase"])
    serial_desc.read()#unimportant ack
    print("Done.")

def flash_and_verify():
    #TODO: add decoders for hex elf etc.
    file_path = input('Please enter path to .bin file to flash between quote marks("")\n')
    print file_path
    try:
        file_length = stat(file_path).st_size 
        fd = open(file_path, "rb")
        print("Starting to flash")
        #address for just stm32f0
        start_address = 0x08000000
        end_address   = 0x08004000
        current_address = start_address
        
        while current_address < end_address and fd.tell() < file_length:
            print("Writing to " + str(hex(current_address)))
            serial_desc.write(command_set["write_mem"])
            ans = serial_desc.read()
            if ans == command_set["nack"]:
                print("Protection may be active, cannot write")
                #TODO: try to deactivate protection
                return
            
            serial_desc.write(struct.pack(">i",current_address))#address
            serial_desc.write(calc_checksum(current_address))#and it's checksum
            
            ans = serial_desc.read()#ack of address
            if ans == command_set["nack"]:
                #maybe address got corrupted while transmitting, try again
                pass
            
            #try to read 256 bytes
            data_buffer = fd.read(256)
            
            #if readed data bytes are not multiple of 4 then make it be
            if len(data_buffer) % 4 != 0:
                data_buffer += (4 - len(data_buffer)) * '\x00'
                
            data_buffer = chr(len(data_buffer) - 1) + data_buffer
            checksum = calc_checksum(data_buffer)
            data_buffer = data_buffer + checksum
            serial_desc.write(data_buffer)
            print(serial_desc.read())#last ack
            current_address += 256
    finally:
        fd.close()
        #TODO: add verify
    

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
