from cocotb.triggers import RisingEdge
from pyuvm import uvm_driver
from pyuvm import uvm_analysis_port
from pyuvm import UVMError
from verif.uvc.uvc_seq_item import USB_Lowspeed_Data_Seq_Item
import logging
from verif.uvc.uvc_enums import *

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
    self.ap = uvm_analysis_port(self.name+"_ap", self)
    self.logger.info("Creating Analysis port " + self.name + "_ap")
    self.logger.critical("My device value " + str(self.device_array))

  def connect_phase(self):
    super().connect_phase()

  async def run_phase(self):
    self.NUM_DEVICES = int(self.low_speed_if.dut.NUM_USB_DEVICES)
    while True:
      self.low_item = USB_Lowspeed_Data_Seq_Item("Driver_low_item")
      self.logger.info("Waiting for sequence item")
      self.low_item = await self.seq_item_port.get_next_item()
      self.logger.info("Received sequence item with TID = 0x%0x, %s",   self.low_item.transaction_id, vars(self.low_item))
      await(self.start_transaction())
      self.seq_item_port.item_done()

  async def start_transaction(self):
    await self.initialize_port()
    self.low_speed_if.device_state = self.low_speed_if.device_state | (DEBUG_PACKET.SYNC_PACKET.value << self.low_item.device_number*4)
    self.low_speed_if.dut.dev_low_packet_state.value = self.low_speed_if.device_state
    await self.sync_packets()
    await RisingEdge(self.low_speed_if.dut.low_clock)
    if(self.low_item.req_type == request_type.WRITE):
      self.logger.info("Drive a request of type WRITE")
      self.low_speed_if.device_state = self.low_speed_if.device_state | (DEBUG_PACKET.TOKEN_PKT_WRITE.value << self.low_item.device_number*4)
      self.low_speed_if.dut.dev_low_packet_state.value = self.low_speed_if.device_state
      await self.start_token_packet()
      await self.start_data_packet()
      self.low_speed_if.device_state = self.low_speed_if.device_state | (DEBUG_PACKET.DONE.value << self.low_item.device_number*4)
      self.low_speed_if.dut.dev_low_packet_state.value = self.low_speed_if.device_state
    else:
      self.logger.info("Drive a request of type READ")
      self.low_speed_if.device_state = self.low_speed_if.device_state | (DEBUG_PACKET.TOKEN_PKT_READ.value << self.low_item.device_number*4)
      self.low_speed_if.dut.dev_low_packet_state.value = self.low_speed_if.device_state
      await self.start_token_packet()
      self.low_speed_if.device_state = self.low_speed_if.device_state | (DEBUG_PACKET.DONE.value << self.low_item.device_number*4)
      self.low_speed_if.dut.dev_low_packet_state.value = self.low_speed_if.device_state

  async def initialize_port(self):
    self.logger.debug("Initializing Port, Waiting for a Raising Edge of Clock")
    await RisingEdge(self.low_speed_if.dut.low_clock)
    self.logger.debug("Setting Port to SE1")
    self.low_speed_if.d_minus  = 3
    self.low_speed_if.d_plus   = 0

  async def sync_packets(self):
    await RisingEdge(self.low_speed_if.dut.low_clock)
    self.logger.debug("Driving Sync Packets in Low_clock")
    await self.drive_signal(0b0, 12)

  async def start_token_packet(self):
    self.logger.debug("Starting driving PID Bits")
    await self.start_pid_packet()
    self.logger.debug("done with driving PID Bits")
    self.low_item.pid.pop(0)
    self.logger.debug("Starting driving Address Bits ")
    await self.start_address_packet()
    self.logger.debug("done with driving Address Bits")

  async def start_pid_packet(self):
    self.logger.debug("Starting to Drive PID for device %d, value = 0x%0x", self.low_item.device_number, self.low_item.pid[0].value)
    await self.drive_signal(self.low_item.pid[0].value, 8)

  async def start_address_packet(self):
    if(self.low_item.address > 128):
      UVMError("Address is a 7 bit field Cannot be greater than 128")
    self.low_speed_if.device_state = self.low_speed_if.device_state | (DEBUG_PACKET.ADDRESS_PACKET.value << self.low_item.device_number*4)
    self.low_speed_if.dut.dev_low_packet_state.value = self.low_speed_if.device_state
    self.logger.debug("Starting to Drive Address Packet with Address = 0x%0x", self.low_item.address)
    await self.drive_signal(self.low_item.address, 7)
    self.low_speed_if.device_state = self.low_speed_if.device_state | (DEBUG_PACKET.CRC_PACKET.value << self.low_item.device_number*4)
    self.low_speed_if.dut.dev_low_packet_state.value = self.low_speed_if.device_state
    # await self.drive_signal(self.low_item.crc[0].vaue, 5)

  async def start_data_packet(self):
    self.logger.debug("Starting driving PID Bits")
    self.low_speed_if.device_state = self.low_speed_if.device_state | (DEBUG_PACKET.DATA_PACKET_PID.value << self.low_item.device_number*4)
    self.low_speed_if.dut.dev_low_packet_state.value = self.low_speed_if.device_state
    await self.start_pid_packet()
    self.low_item.pid.pop(0)
    self.low_speed_if.device_state = self.low_speed_if.device_state | (DEBUG_PACKET.DATA_PACKET_DATA.value << self.low_item.device_number*4)
    self.low_speed_if.dut.dev_low_packet_state.value = self.low_speed_if.device_state
    self.logger.debug("Starting driving Data Bits")
    await self.drive_signal(self.low_item.data, self.low_item.data_bytes)
    self.logger.debug("done with driving Data Bits")

  async def drive_signal(self, data, no_bits):
    def get_bit(value, n):
      int(value)
      str(value)
      return ((value >> n & 1))

    def put_bit(bit_positon):
      value = 0
      for i in range (self.NUM_DEVICES):
        if(i != bit_positon):
          value = value << 1 | 0b1
          self.logger.debug("Retrning bit mask = " + str(value) + ", i = " + str(i))
        else:
          value = value << 1
          self.logger.debug("Retrning bit mask = " + str(value) + ", i = " + str(i))
      self.logger.debug("Retrning bit mask = " + str(value))
      self.logger.debug("Given bit pos is " + str(bit_positon))
      return(value)

    def set_if_bit(bit_mask):
      device_list = 0
      for i in range (self.NUM_DEVICES):
        device_list = device_list << 1 | 0b1
      self.logger.debug("Bit_mask = " + bin(bit_mask) + ", device_list = " + bin(device_list))
      self.logger.debug("current interface value before driving = " + str(self.low_speed_if.dut.device_d_plus))
      self.logger.debug("current if variable value before driving = " + bin(self.low_speed_if.d_plus))
      self.low_speed_if.d_plus   = (self.low_speed_if.d_plus ) ^ (bit_mask & device_list)
      self.low_speed_if.d_minus  = (self.low_speed_if.d_minus) ^ (bit_mask & device_list)
      self.logger.debug("current interface value should after driving = " + bin((self.low_speed_if.d_plus)))
      self.logger.debug("current interface value should after driving = " + bin((self.low_speed_if.d_minus)))

    def drive_if_bits(value):
      if(value == 1):
        self.logger.debug("Drving Values from variables to interface d_plus = %2b, d_minus = %2b", self.low_speed_if.d_plus, self.low_speed_if.d_minus)
      self.low_speed_if.dut.device_d_plus  = self.low_speed_if.d_plus
      self.low_speed_if.dut.device_d_minus = self.low_speed_if.d_minus

    for i in range (no_bits):
      self.logger.debug("Starting to drive signal bit ["+ str(i) + "] = " + str(get_bit(data, i)))
      if(get_bit(data, i) == 0):
        bit_mask = put_bit(self.low_item.device_number)
        set_if_bit(bit_mask=bit_mask)
      if(self.low_item.device_number == self.NUM_DEVICES - 1):
        drive_if_bits(value=1)
      await RisingEdge(self.low_speed_if.dut.low_clock)
