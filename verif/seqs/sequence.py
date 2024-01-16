from cocotb.triggers import Join, Combine
from pyuvm import uvm_sequence
from pyuvm import ConfigDB
from verif import *
import cocotb
import pyuvm
import logging
from verif.uvc.uvc_seq_item import USB_Lowspeed_Data_Seq_Item

logger = logging.getLogger()

class USB_main_seq(uvm_sequence):
  """
  USB_main_seq: The Main sequence that is started for all the Tests, This Sequence decides on
  what subsequence sequences to start based on the Testcases. This way the testcase just, needs
  to specify the Testcase
  """
  async def body(self):
    testcase     = ConfigDB().get(None,"", "Test_case")
    if (testcase == "test_one"):
      ConfigDB().set(None, "", "Number_of_devices", 0)
      logger.info("Starting Testcase sequence: %s", testcase)
      current_seq  = USB_test_one(testcase)
    else:
      ConfigDB().set(None, "", "Number_of_devices", 1)
      logger.fatal("No valid Testcase Proveded %s", testcase)
    current_seq.start()


class USB_test_one(uvm_sequence):
  """
  USB_test_one seq, Initiates any one (Currently 0) of the Device and 'only' the 
  lowspeed port of the Host side This should be used like a really basic test for bringup
  This needs to be modified to pick any random device. 
  """
  async def body(self):
    host_low_seqr     = ConfigDB().get(None, "", "Host_Low_Seqr")
    device_low_seqr   = ConfigDB().get(None, "", "Device_Low_Seqr0")
    host_low_seq      = USB_low_seq("host_low_seq")
    device_seq0       = USB_low_seq("device_seq")
    host_low_seq.start(host_low_seqr)
    device_seq0.start(device_low_seqr)

class USB_test_all(uvm_sequence):
  """
  USB_test_all sequence, ***WIP*** Initiates all the Sequence Device sequences and initiates both the 
  Hi speed and Low speed Sequence for the Host.
  ISMAIL TO_DO: make the device sequence into an array
  """
  async def body(self):
    host_hi_seqr      = ConfigDB().get(None, "", "Host_Hi_Seqr")
    host_low_seqr     = ConfigDB().get(None, "", "Host_Low_Seqr")
    device_low_seqr   = ConfigDB().get(None, "", "Device_Low_Seqr0")
    
    host_hi_seq   = USB_hi_seq("usb_host_hi_seq")
    host_low_seq  = USB_low_seq("usb_host_low_seq")
    device_seq0   = USB_low_seq("usb_device_seq")

    host_hi_seq.start(host_hi_seqr)
    host_low_seq.start(host_low_seqr)
    device_seq0.start(device_low_seqr)

class USB_hi_seq(uvm_sequence):

  def __init__(self, name):
    self.name = name
    super.__init__(name)

  async def body(self):
    for i in range (10):
      hi_seq_item = USB_Lowspeed_Data_Seq_Item("Host_req_hi_item")
      hi_seq_item.randomize()
      await self.start_item(hi_seq_item)
      await self.finish_item(hi_seq_item)

class USB_low_seq(uvm_sequence):

  def __init__(self, name):
    self.name = name
    super().__init__(name=name)

  async def body(self):
    for i in range(10):
      low_seq_item  = USB_Lowspeed_Data_Seq_Item(name=self.name+"_seq_item")
      low_seq_item.randomize()
      await self.start_item(low_seq_item)
      await self.finish_item(low_seq_item)

