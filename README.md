# Description

This library is used to upload/download firmware to/from STM32Fx microcontrollers 
via UART port, which automatically allows in circuit programming of daisy chained 
microcontrollers. 

# Usage 

Programming over local computer and over TCP/IP connection is allowed.

In order to upload firmware over a serial port in localhost, use `flash-over-serial.py`. 

In order to upload firmware over TCP/IP via a simple transparent serial-tcp bridge, run `flash-over-tcp.py`. 

`tcp-serial-bridge.py` is a simple transparent bridge application that is added for testing/debugging purposes.


# References

http://www.st.com/web/en/resource/technical/document/application_note/CD00264342.pdf
