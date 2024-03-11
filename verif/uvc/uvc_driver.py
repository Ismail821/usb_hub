from cocotb.triggers import RisingEdge, FallingEdge, Timer
from pyuvm import uvm_driver
from pyuvm import uvm_analysis_port
from pyuvm import UVMError
from verif.uvc.uvc_seq_item import USB_Hispeed_Data_Seq_Item, USB_Lowspeed_Data_Seq_Item
import logging
from verif.uvc.uvc_enums import *

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


class USB_lowspeed_device_driver(uvm_driver):

  def __init__(self, name, uvc_cfg, lowspeed_if, i, parent):
    self.low_speed_if = lowspeed_if
    self.uvc_cfg      = uvc_cfg
    self.name         = name
    super().__init__(name, parent)
    self.logger   = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)
    self.device_array = i
  
  def build_phase(self):
    self.ap = uvm_analysis_port(self.name+"ap", self)
    self.logger.info("Creating Analysis port" + self.name + "ap")
    self.logger.critical("My device value " + str(self.device_array))


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
    await RisingEdge(self.low_speed_if.dut.low_clock)
    if(self.low_item.req_type == request_type.WRITE):
      self.logger.info("Drive a request of type WRITE")
      self.low_speed_if.dut.dev_low_packet_state.value = DEBUG_PACKET.TOKEN_PKT_WRITE.value
      await self.start_token_packet()
      await self.start_data_packet()
      self.low_speed_if.dut.dev_low_packet_state.value = DEBUG_PACKET.DONE.value
    else:
      self.logger.info("Drive a request of type READ")
      self.low_speed_if.dut.dev_low_packet_state.value = DEBUG_PACKET.TOKEN_PKT_READ.value
      await self.start_token_packet()
      self.low_speed_if.dut.dev_low_packet_state.value = DEBUG_PACKET.DONE.value

  async def initialize_port(self):
    self.logger.debug("Initializing Port, Waiting for a Raising Edge of Clock")
    await RisingEdge(self.low_speed_if.dut.low_clock)
    self.logger.debug("Setting Port to SE1")
    self.low_speed_if.dut.device_d_minus.value  = 1
    self.low_speed_if.dut.device_d_plus.value   = 1

  async def sync_packets(self):
    for i in range (6):
      await RisingEdge(self.low_speed_if.dut.low_clock)
      self.logger.debug("Driving J in Low_clock")
      self.low_speed_if.dut.device_d_minus.value[0]  = 0
      self.low_speed_if.dut.device_d_plus.value[0]   = 1
      await RisingEdge(self.low_speed_if.dut.low_clock)
      self.logger.debug("Driving k in Low_clock")
      self.low_speed_if.dut.device_d_minus.value[0]  = 1
      self.low_speed_if.dut.device_d_plus.value[0]   = 0

  async def start_token_packet(self):
    self.logger.debug("Starting driving PID Bits")
    await self.start_pid_packet()
    self.logger.debug("done with driving PID Bits")
    self.low_item.pid.pop(0)
    self.logger.debug("Starting driving Address Bits ")
    await self.start_address_packet()
    self.logger.debug("done with driving Address Bits")

  async def start_pid_packet(self):
    await self.drive_signal(self.low_item.pid[0].value, 8)

  async def start_address_packet(self):
    if(self.low_item.address > 128):
      UVMError("Address is a 7 bit field Cannot be greater than 128")
    self.low_speed_if.dut.dev_low_packet_state.value = DEBUG_PACKET.ADDRESS_PACKET.value
    await self.drive_signal(self.low_item.address, 7)
    self.low_speed_if.dut.dev_low_packet_state.value = DEBUG_PACKET.CRC_PACKET.value
    # await self.drive_signal(self.low_item.crc[0].vaue, 5)

  async def start_data_packet(self):
    self.logger.debug("Starting driving PID Bits")
    self.low_speed_if.dut.dev_low_packet_state.value = DEBUG_PACKET.DATA_PACKET_PID.value
    await self.start_pid_packet()
    self.logger.debug("done with driving PID Bits")
    self.low_item.pid.pop(0)
    self.low_speed_if.dut.dev_low_packet_state.value = DEBUG_PACKET.DATA_PACKET_DATA.value
    self.logger.debug("Starting driving Data Bits ")
    await self.drive_signal(self.low_item.data, self.low_item.data_bytes)
    self.logger.debug("done with driving Data Bits")

  async def drive_signal(self, data, no_bits):
    def get_bit(value, n):
      int(value)
      str(value)
      # self.logger.debug("Get Bits: ", value)
      return ((value >> n & 1))

    value = value | 0xFF
    value = value & 0x01
    for i in range (no_bits):
      self.logger.debug("Starting to drive signal bit ["+ str(i) + "] = " + str(get_bit(data, i)))
      if(get_bit(data, i)):
        self.logger.debug(str(get_bit(self.low_speed_if.dut.device_d_plus.value[self.device_array],  0)))
        self.logger.debug("Device num = " + str(self.device_array))
        self.low_speed_if.dut.device_d_plus.value[self.device_array]    =  get_bit(self.low_speed_if.dut.device_d_plus.value[self.device_array],  0) & 1
        self.low_speed_if.dut.device_d_minus.value[self.device_array]   =  get_bit(self.low_speed_if.dut.device_d_minus.value[self.device_array], 0) & 1
      else:
        self.logger.debug(str(get_bit(self.low_speed_if.dut.device_d_plus.value[self.device_array],  0)))
        self.low_speed_if.dut.device_d_plus.value[self.device_array]    = ~get_bit(self.low_speed_if.dut.device_d_plus.value[self.device_array],  0) & 1
        self.low_speed_if.dut.device_d_minus.value[self.device_array]   = ~get_bit(self.low_speed_if.dut.device_d_minus.value[self.device_array], 0) & 1
      await RisingEdge(self.low_speed_if.dut.low_clock)

class USB_lowspeed_host_driver(uvm_driver):

  def __init__(self, name, uvc_cfg, lowspeed_if, i, parent):
    self.low_speed_if = lowspeed_if
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
    await RisingEdge(self.low_speed_if.dut.low_clock)
    if(self.low_item.req_type == request_type.WRITE):
      self.logger.info("Drive a request of type WRITE")
      self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.TOKEN_PKT_WRITE.value
      await self.start_token_packet()
      await self.start_data_packet()
      self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.DONE.value
    else:
      self.logger.info("Drive a request of type READ")
      self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.TOKEN_PKT_READ.value
      await self.start_token_packet()
      self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.DONE.value

  async def initialize_port(self):
    self.logger.debug("Initializing Port, Waiting for a Raising Edge of Clock")
    await RisingEdge(self.low_speed_if.dut.low_clock)
    self.logger.debug("Setting Port to SE1")
    self.low_speed_if.dut.host_d_minus.value = 1
    self.low_speed_if.dut.host_d_plus.value  = 1
    #Whatever the Start signal condition is

  async def sync_packets(self):
    for i in range (6):
      await RisingEdge(self.low_speed_if.dut.low_clock)
      self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.SYNC_PACKET.value
      self.logger.debug("Driving J in Low_clock")
      self.low_speed_if.dut.host_d_minus.value = 0
      self.low_speed_if.dut.host_d_plus.value  = 1
      await RisingEdge(self.low_speed_if.dut.low_clock)
      self.logger.debug("Driving k in Low_clock")
      self.low_speed_if.dut.host_d_minus.value = 1
      self.low_speed_if.dut.host_d_plus.value  = 0

  async def start_token_packet(self):
    self.logger.debug("Starting driving PID Bits")
    await self.start_pid_packet()
    self.logger.debug("done with driving PID Bits")
    self.low_item.pid.pop(0)
    self.logger.debug("Starting driving Address Bits ")
    await self.start_address_packet()
    self.logger.debug("done with driving Address Bits")

  async def start_pid_packet(self):
    await self.drive_signal(self.low_item.pid[0].value, 8)

  async def start_address_packet(self):
    if(self.low_item.address > 128):
      UVMError("Address is a 7 bit field Cannot be greater than 128")
    self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.ADDRESS_PACKET.value
    await self.drive_signal(self.low_item.address, 7)
    self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.CRC_PACKET.value
    # await self.drive_signal(self.low_item.crc[0].vaue, 5)

  async def start_data_packet(self):
    self.logger.debug("Starting driving PID Bits")
    self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.DATA_PACKET_PID.value
    await self.start_pid_packet()
    self.logger.debug("done with driving PID Bits")
    self.low_item.pid.pop(0)
    self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.DATA_PACKET_DATA.value
    self.logger.debug("Starting driving Data Bits ")
    await self.drive_signal(self.low_item.data, self.low_item.data_bytes)
    self.logger.debug("done with driving Data Bits")

  async def drive_signal(self, data, no_bits):
    def get_bit(value, n):
      int(value)
      str(value)
      # self.logger.debug("Get Bits: ", value)
      return ((value >> n & 1) != 0)

    for i in range (no_bits):
      self.logger.debug("Starting to drive signal bit ["+ str(i) + "]" + str(get_bit(data, i)))
      if(get_bit(data, i)):
        self.low_speed_if.dut.host_d_plus.value   =  get_bit(self.low_speed_if.dut.host_d_plus.value,  0) & 1
        self.low_speed_if.dut.host_d_minus.value  =  get_bit(self.low_speed_if.dut.host_d_minus.value, 0) & 1
      else:
        self.low_speed_if.dut.host_d_plus.value   = ~get_bit(self.low_speed_if.dut.host_d_plus.value,  0) & 1
        self.low_speed_if.dut.host_d_minus.value  = ~get_bit(self.low_speed_if.dut.host_d_minus.value, 0) & 1
      await RisingEdge(self.low_speed_if.dut.low_clock)