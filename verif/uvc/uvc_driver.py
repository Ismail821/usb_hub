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
    self.low_speed_if    = lowspeed_if
    self.low_clock       = low_clock
    self.uvc_cfg         = uvc_cfg
    super().__init__(name, parent)
    self.logger   = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)
  
  def build_phase(self):
    self.ap = uvm_analysis_port("ap", self)
    self.logger.info("Creating Analysis port ap")


  def connect_phase(self):
    super().connect_phase()

  async def run_phase(self):
    # await FallingEdge(self.low_speed_if.dut.low_clock)
    self.logger.critical("Start of Driver, Waiting 1us to avoid Deadlock")
    await Timer(units='us', time=1)
    self.logger.critical("Done Waiting 1us, Now starting to get item")
    while True:
      self.low_item = USB_Hispeed_Data_Seq_Item("Driver_hi_item")
      self.logger.info("Waiting for sequence item")
      self.low_item = await self.seq_item_port.get_next_item()
      self.logger.info("Received sequence item, Starting transaction")
      self.start_transaction()

  async def start_transaction(self):
    await self.initialize_port()
    await self.sync_packets()
    await self.start_metadata_packet()
    await self.start_data_packet()

  async def initialize_port(self):
    await RisingEdge(self.low_clock)
    self.low_speed_if.d_minus = 1
    self.low_speed_if.d_plus  = 1
    #Whatever the Start signal condition is

  async def sync_packets(self):
    for i in range (4):
      await RisingEdge(self.low_clock)
      self.low_speed_if.d_minus = 0
      self.low_speed_if.d_plus  = 1
      await RisingEdge(self.low_clock)
      self.low_speed_if.d_minus = 1
      self.low_speed_if.d_plus  = 0
