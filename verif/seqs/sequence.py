from pyuvm import *
import cocotb
import pyuvm

class test_one(uvm_sequence):
  async def body(self):
    seqr = ConfigDB().get(None, "", "SEQR")
    ##commented out now to stop the errors
    usb_host_seq   = 0 #USB_host_seq("usb_host_seq")
    usb_device_seq = 0 #USB_device_seq("usb_device_seq")
    usb_host_seq.start()
    usb_device_seq.start()
