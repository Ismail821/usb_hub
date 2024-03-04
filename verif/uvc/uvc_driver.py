from cocotb.triggers import RisingEdge, FallingEdge, Timer
from pyuvm import uvm_driver
from pyuvm import uvm_analysis_port
from pyuvm import UVMError
from verif.uvc.uvc_seq_item import USB_Hispeed_Data_Seq_Item, USB_Lowspeed_Data_Seq_Item
import logging

class USB_hispeed_driver(uvm_driver):

  def __init__(self, name, uvc_cfg, hi_speed_if, hi_clock, parent):
    self.hi_speed_if    = hi_speed_if
    self.hi_clock       = hi_clock
    self.uvc_cfg        = uvc_cfg
    super().__init__(name, parent)
    self.logger   = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)
  

  def connect_phase(self):
    super().connect_phase()

  async def run_phase(self):
    self.logger.info("Starting Hi speed Driver")
    # while True:
    #   # self.hi_item = USB_Hispeed_Data_Seq_Item("Driver_hi_item")
    #   self.logger.info("Waiting for sequence item")
    #   self.hi_item = await self.seq_item_port.get_next_item()
    #   self.logger.info("Received sequence item, Starting transaction")
    #   self.start_transaction()

  async def start_transaction(self):
    await self.initialize_port()
    await self.sync_packets()
    await self.start_metadata_packet()
    await self.start_data_packet()

  async def initialize_port(self):
    await RisingEdge(self.hi_clock)
    self.hi_speed_if.tx_minus = 1
    self.hi_speed_if.tx_plus  = 1
    #Whatever the Start signal condition is

  async def sync_packets(self):
    for i in range (4):
      await RisingEdge(self.hi_clock)
      self.hi_speed_if.tx_minus = 0
      self.hi_speed_if.tx_plus  = 1
      await RisingEdge(self.hi_clock)
      self.hi_speed_if.tx_minus = 1
      self.hi_speed_if.tx_plus  = 0


class USB_lowspeed_driver(uvm_driver):

  def __init__(self, name, uvc_cfg, lowspeed_if, low_clock, parent):
    self.low_speed_if = lowspeed_if
    self.low_clock    = low_clock
    self.uvc_cfg      = uvc_cfg
    self.name         = name
    super().__init__(name, parent)
    self.logger   = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)
  
  def build_phase(self):
    self.ap = uvm_analysis_port(self.name+"ap", self)
    self.logger.info("Creating Analysis port" + self.name + "ap")


  def connect_phase(self):
    super().connect_phase()

  async def run_phase(self):
    while True:
      self.low_item = USB_Hispeed_Data_Seq_Item("Driver_hi_item")
      self.logger.info("Waiting for sequence item")
      self.low_item = await self.seq_item_port.get_next_item()
      self.logger.info("Received sequence item, Starting transaction")
      await(self.start_transaction())
      self.seq_item_port.item_done()

  async def start_transaction(self):
    await self.initialize_port()
    await self.sync_packets()
    # await self.start_metadata_packet()
    # await self.start_data_packet()

  async def initialize_port(self):
    self.logger.debug("Initializing Port, Waiting for a Raising Edge of Clock")
    await RisingEdge(self.low_speed_if.dut.low_clock)
    self.logger.debug("Setting Port to SE1")
    self.low_speed_if.dut.device_d_minus.value[0] = 1
    self.low_speed_if.dut.device_d_plus.value[0]  = 1
    #Whatever the Start signal condition is

  async def sync_packets(self):
    for i in range (6):
      await RisingEdge(self.low_speed_if.dut.low_clock)
      self.logger.debug("Driving J in Low_clock")
      self.low_speed_if.dut.device_d_minus = 0
      self.low_speed_if.dut.device_d_plus  = 1
      await RisingEdge(self.low_speed_if.dut.low_clock)
      self.logger.debug("Driving k in Low_clock")
      self.low_speed_if.dut.device_d_minus = 1
      self.low_speed_if.dut.device_d_plus  = 0
    self.do_something
