__author__ = 'ceremcem'

import time

from stm_flasher import StmFlasher

flasher = StmFlasher()
print "Preparig to connect stm"
flasher.setup_hardware()
flasher.wait_setup_hardware()
flasher.upload_firmware('./ch.bin')
if flasher.upload_successful():
  print "Upload is succesful"
else:
  print "Problem while uploading firmware"

print "sleeping before verify"
time.sleep(3)
if flasher.verify_firmware():
    print "Successfully verified"
else:
    print "Verification is failed!"

