from cocotb.triggers import Join, Combine, RisingEdge, FallingEdge
from pyuvm import uvm_sequence
from pyuvm import ConfigDB
import random
import cocotb
import pyuvm
import logging
from verif.uvc.uvc_seq_item import USB_Lowspeed_Data_Seq_Item
from verif.uvc.uvc_seq_item import USB_Hispeed_Data_Seq_Item
from verif.uvc.uvc_seqs     import uvc_sequence

class USB_main_seq(uvm_sequence):
  """
  USB_main_seq: The Main sequence that is started for all the Tests, This Sequence decides on
  what subsequence sequences to start based on the Testcases. This way the testcase just, needs
  to specify the Testcase based on which we can select the sequences
  """

  async def body(self):
    self.logger = logging.getLogger("Main_Sequence")
    self.logger.setLevel(logging.DEBUG)
    self.logger.info("Starting Sequence")
    testcase     = ConfigDB().get(None,"", "Test_case")
    self.logger.info("ConfigDB Retrieved: Test_case = " + str(testcase))
    self.logger.info("Searching for Testcase :%s", testcase)

    if (str(testcase) == "test_one"):
      self.logger.critical("Starting Matching Testcase sequence: %s", testcase)
      current_seq  = USB_test_one("one_seq")
    elif(str(testcase) == "test_all"):
      self.logger.critical("Starting Matching Testcase sequence: %s", testcase)
      current_seq  = USB_test_all("test_all_seq")
    else:
      ConfigDB().set(None, "", "Number_of_devices", 1)
      self.logger.info("No Matching Testcase %s", testcase)
      self.logger.fatal("No valid Testcase Proveded %s", testcase)
    self.logger.info("Body: Starting Sequence " + current_seq.get_name())
    await current_seq.start()
    self.logger.critical("Main sequence Ended")
    # self.do_something

class USB_test_one(uvm_sequence):
  """
  USB_test_one seq, Initiates any one (Currently 0) of the Device and 'only' the 
  lowspeed port of the Host side This should be used like a really basic test for bringup
  This needs to be modified to pick any random device. 
  """
  def __init__(self, name):
    self.logger = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)
    super().__init__(name)
  
  async def body(self):
    self.logger.info("ConfigDB retrieving Sequencers: Host_low_seqr")
    host_low_seqr     = ConfigDB().get(None, "", "Host_low_seqr")
    self.logger.info("ConfigDB retrieving Sequencers: Device_seqr_0")
    device_low_seqr   = ConfigDB().get(None, "", "Device_seqr_0")
    host_low_seq      = USB_low_seq("host_low_seq", 0)
    host_low_seq.host = 1
    device_seq0       = USB_low_seq("device_seq0", 0)
    self.logger.info("Starting host side lowspeed Sequence")
    host_low_seq_task      = cocotb.start_soon(host_low_seq.start(host_low_seqr))
    self.logger.info("Starting Device side lowspeed Sequence")
    device_low_seq_task    = cocotb.start_soon(device_seq0.start(device_low_seqr))
    self.logger.info("All Sequences Started, Waiting for them to finish")
    # while True:
    #   if(cocotb.simulator.get_sim_time == 100):
    #     break
    await(Combine(host_low_seq_task, device_low_seq_task))
    self.logger.info("All Sequences Completed, Sequences ending Soon")

class USB_test_all(uvm_sequence):
  """
  USB_test_all sequence, Initiates all the Device sequences and initiates both the 
  Hi speed and Low speed Sequence for the Host.
  """
  def __init__(self, name):
    self.logger = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)
    super().__init__(name)

  async def body(self):
    self.logger.info("ConfigDB retrieving Sequencers: Host_seqrs")
    host_hi_seqr      = ConfigDB().get(None, "", "Host_hi_seqr")
    host_low_seqr     = ConfigDB().get(None, "", "Host_low_seqr")
    number_of_devices = int(ConfigDB().get(None, "", "number_of_devices"))
    device_low_seqr_a = [ConfigDB().get(None, "", "Device_seqr_"+str(i)) for i in range (number_of_devices)]
    
    host_hi_seq   = USB_hi_seq("usb_host_hi_seq")
    host_low_seq  = USB_low_seq("usb_host_low_seq", 0)
    device_seq_a  = [USB_low_seq("usb_device_seq"+str(i), i) for i in range (number_of_devices)]

    host_hi_seq_task =  cocotb.start_soon(host_hi_seq.start(host_hi_seqr))
    host_low_seq_task = cocotb.start_soon(host_low_seq.start(host_low_seqr))
    device_seq_task_a = [cocotb.start_soon(device_seq_a[i].start(device_low_seqr_a[i])) for i in range (number_of_devices)]
    await (Combine(host_hi_seq_task, host_low_seq_task, *device_seq_task_a))

class USB_hi_seq(uvc_sequence):

  logger = logging.getLogger("hi_Sequence")
  logger.setLevel(logging.DEBUG)
  def __init__(self, name):
    super().__init__(name)
    self.logger.debug("init Hi_seq Body")
    self.name = name

  async def body(self):
    self.logger.info("Entering Body")
    for i in range (0):
      hi_seq_item = USB_Hispeed_Data_Seq_Item("req_hi_item")
      hi_seq_item.randomize()
      self.logger.info("Sequence item randomized: TID: 0x%x ", hi_seq_item.transaction_id)
      await self.start_item(hi_seq_item)
      await self.finish_item(hi_seq_item)
      self.logger.info("Sequence item Sent: %s", hi_seq_item.transaction_id)
    self.logger.info("Done generating sequence loops")

class USB_low_seq(uvc_sequence):

  host = 1
  def __init__(self, name, device_number):
    super().__init__(name=name)
    self.logger = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)
    self.name = name
    self.device_number = device_number

  async def body(self):
    self.logger.info("Entering Body")
    if(self.host==1):
      for i in range(1):
        low_seq_item  = USB_Lowspeed_Data_Seq_Item(name=self.name+"_item"+str(i))
        self.logger.critical("Sequence Starting item \"" + low_seq_item.name + "\" %s", low_seq_item)
        low_seq_item.randomize(host=self.host)
        low_seq_item.device_number = self.device_number
        await self.start_item(low_seq_item)
        self.logger.info("Sequence item randomized: TID: 0x%0x", low_seq_item.transaction_id)
        self.logger.critical("Sequence finished sequence.start_item")
        await self.finish_item(low_seq_item)
        # self.get_response()
        self.logger.info("Sequence item Sent: 0x%0x", low_seq_item.transaction_id)
        self.logger.debug("Waiting for a Random amount of time")
        await self.wait_low_clock(random.randint(5,20))
      self.logger.info("Done generating sequence loops")

