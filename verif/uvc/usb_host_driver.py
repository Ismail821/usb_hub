from cocotb.triggers import RisingEdge
from cocotb.binary import *
from pyuvm import uvm_driver
from pyuvm import uvm_analysis_port
from pyuvm import UVMError
from verif.uvc.uvc_seq_item import USB_Hispeed_Data_Seq_Item, USB_Lowspeed_Data_Seq_Item
import logging
import cocotb
from verif.uvc.uvc_enums import *

class USB_hispeed_driver(uvm_driver):

  def __init__(self, name, uvc_cfg, hi_speed_if, hi_clock, parent):
    super().__init__(name, parent)
    self.hi_speed_if    = hi_speed_if
    self.hi_clock       = hi_clock
    self.uvc_cfg        = uvc_cfg
    self.name           = name
    self.logger   = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)
  

  def connect_phase(self):
    super().connect_phase()

  async def run_phase(self):
    self.logger.info("Starting Hi speed Driver")
    while True:
      # self.hi_item = USB_Hispeed_Data_Seq_Item("Driver_hi_item")
      self.logger.info("Waiting for sequence item")
      self.hi_item = await self.seq_item_port.get_next_item()
      self.logger.info("Received sequence item, Starting transaction")
      self.start_transaction()

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

class USB_lowspeed_host_driver(uvm_driver):

  NUM_DEVICES = 1

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
    await self.reset_all_devices()
    while True:
      self.hi_item = USB_Lowspeed_Data_Seq_Item("Driver_hi_item")
      self.logger.info("Waiting for sequence item")
      self.hi_item = await self.seq_item_port.get_next_item()
      if((self.hi_item is USB_Lowspeed_Data_Seq_Item)):
        self.logger.error("Received a sequence item not of the Type USB_Lowspeed_Data_Sequence_item")
        self.logger.error("%s", vars(self.hi_item))
        raise Exception
        # cocotb.raise.ValueError()
      self.logger.info("Received sequence item with TID = %0d, %s",   self.hi_item.transaction_id, vars(self.hi_item))
      await(self.start_transaction())
      self.seq_item_port.item_done()

  async def start_transaction(self):
    await self.initialize_port()
    await self.sync_packets()
    await RisingEdge(self.low_speed_if.dut.low_clock)
    if(self.hi_item.req_type == request_type.WRITE):
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
    await self.drive_signal(0b10000001,8)
    # for i in range (6):
    #   await RisingEdge(self.low_speed_if.dut.low_clock)
    #   self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.SYNC_PACKET.value
    #   self.logger.debug("Driving J in Low_clock")
    #   self.low_speed_if.dut.host_d_minus.value = 0
    #   self.low_speed_if.dut.host_d_plus.value  = 1
    #   await RisingEdge(self.low_speed_if.dut.low_clock)
    #   self.logger.debug("Driving k in Low_clock")
    #   self.low_speed_if.dut.host_d_minus.value = 1
    #   self.low_speed_if.dut.host_d_plus.value  = 0

  async def start_token_packet(self):
    self.logger.debug("Starting driving PID Bits")
    await self.start_pid_packet()
    self.logger.debug("done with driving PID Bits")
    self.hi_item.pid.pop(0)
    self.logger.debug("Starting driving Address Bits ")
    await self.start_address_packet()
    self.logger.debug("done with driving Address Bits")

  async def start_pid_packet(self):
    self.logger.debug("Starting to Drive PID for device %d, value = 0x%0x", self.hi_item.device_number, self.hi_item.pid[0].value)
    await self.drive_signal(self.hi_item.pid[0].value, 8)

  async def start_address_packet(self):
    if(self.hi_item.address > 128):
      UVMError("Address is a 7 bit field Cannot be greater than 128")
    self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.ADDRESS_PACKET.value
    self.logger.debug("Starting to Drive Address Packet with Address = 0x%0x", self.hi_item.address)
    await self.drive_signal(self.hi_item.address, 7)
    self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.CRC_PACKET.value
    # await self.drive_signal(self.hi_item.crc[0].vaue, 5)

  async def start_data_packet(self):
    self.logger.debug("Starting driving PID Bits")
    self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.DATA_PACKET_PID.value
    await self.start_pid_packet()
    self.logger.debug("done with driving PID Bits")
    self.hi_item.pid.pop(0)
    self.low_speed_if.dut.host_low_packet_state.value = DEBUG_PACKET.DATA_PACKET_DATA.value
    self.logger.debug("Starting driving Data Bits ")
    await self.drive_signal(self.hi_item.data, self.hi_item.data_bytes)
    self.logger.debug("done with driving Data Bits")

  async def drive_signal(self, data, no_bits):
    def get_bit(value, n):
      return (value >> n & 1)

    self.low_speed_if.dut.host_d_plus.value   =  0
    self.low_speed_if.dut.host_d_minus.value  =  1
    await RisingEdge(self.low_speed_if.dut.low_clock)
    self.low_speed_if.dut.host_d_plus.value   =  1
    self.low_speed_if.dut.host_d_minus.value  =  0
    await RisingEdge(self.low_speed_if.dut.low_clock)
    for i in range (no_bits):
      self.logger.debug("Starting to drive signal bit [%0d] = %1b", i, + get_bit(data, i))
      if(get_bit(data, i) == 0):
        self.low_speed_if.dut.host_d_plus.value   = self.low_speed_if.dut.host_d_plus.value  ^ 0b1
        self.low_speed_if.dut.host_d_minus.value  = self.low_speed_if.dut.host_d_minus.value ^ 0b1
      await RisingEdge(self.low_speed_if.dut.low_clock)
    self.low_speed_if.dut.host_d_plus.value   =  0
    self.low_speed_if.dut.host_d_minus.value  =  0
    await RisingEdge(self.low_speed_if.dut.low_clock)

  async def reset_all_devices(self):
    for i in range (40):
      await RisingEdge(self.low_speed_if.dut.low_clock)
      self.low_speed_if.dut.host_d_plus  = 0
      self.low_speed_if.dut.host_d_minus = 0
  
  async def z_all_devices(self):
    await RisingEdge(self.low_speed_if.dut.low_clock)
    z_str = "z"
    for i in range (self.NUM_DEVICES - 1):
      z_str = z_str + "z"
    self.logger.info(z_str)
    self.low_speed_if.dut.host_d_plus  = BinaryValue(z_str, self.NUM_DEVICES)
    self.low_speed_if.dut.host_d_minus = BinaryValue(z_str, self.NUM_DEVICES)

  async def idle_all_devices(self, dev_num=0):
    idle_state = 0
    for i in range (self.NUM_DEVICES):
      idle_state = idle_state << 1 | 0b1
    for i in range (2):
      await RisingEdge(self.low_speed_if.dut.low_clock)
      self.low_speed_if.dut.host_d_plus  = 0
      self.low_speed_if.dut.host_d_minus = idle_state
    await self.z_all_devices()