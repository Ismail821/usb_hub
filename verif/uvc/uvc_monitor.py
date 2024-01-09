from cocotb.triggers import RisingEdge
from pyuvm import uvm_monitor
from pyuvm import uvm_analysis_port
from pyuvm import UVMError
from uvc import *
#refer to the __init__.py file under the uvc folder, it imports all the files under uvc folder

class USB_Hispeed_Monitor(uvm_monitor):

  def __init__(self, name, USB_Hispeed_If, hi_clock):
    self.name     = name
    self.hi_clock = hi_clock
    self.tx_plus  = USB_Hispeed_If.tx_plus
    self.tx_minus = USB_Hispeed_If.tx_minus
    self.rx_plus  = USB_Hispeed_If.rx_plus
    self.rx_minus = USB_Hispeed_If.tx_minus
    self.usb_hispeed_data_seq_item = USB_Hispeed_Data_Seq_Item("monitor_pkt")

  def build_phase(self):
    self.usb_hi_speed_ap   = uvm_analysis_port("usb_hi_speed", self)

  async def run_phase(self):
    self.monitor_transactions(self)

  async def monitor_transactions(self):
    while 1:
      await RisingEdge(self.hi_clock)
      if self.start_of_txn(self):
        print("hi")
        # if start_of_data(self):
        #   unpack(self.raw_data)

  def start_of_txn(self):
    if (self.d_plus == self.START_OF_PACKET_D_PLUS & self.d_minus == self.START_OF_PACKET_D_MINUS):
      return 1
    else :
      return 0
  

class USB_Lowspeed_Monitor(uvm_monitor):

  START_OF_PACKET_D_PLUS  = 1
  START_OF_PACKET_D_MINUS = 1

  def __init__(self, name, USB_Hispeed_If, low_clock):
    self.name     = name
    self.low_clock = low_clock
    self.d_plus   = 0
    self.d_minus  = 0
    self.d_plus   = 0
    self.d_minus  = 0
    self.usb_lowspeed_data_seq_item = USB_Lowspeed_Data_Seq_Item("monitor_pkt")

  def build_phase(self):
    self.usb_hi_speed_ap   = uvm_analysis_port("usb_hi_speed", self)

  async def monitor_transactions(self):
    while 1:
      await RisingEdge(self.hi_clock)
      if self.start_of_txn(self):
        print("hi")
        # if start_of_data(self):
        #   unpack(self.raw_data)

  def start_of_txn(self):
    if (self.d_plus == self.START_OF_PACKET_D_PLUS & self.d_minus == self.START_OF_PACKET_D_MINUS):
      return 1
    else :
      return 0

  async def start_of_data(self):
    while True:
      ##There should be 4 Sync signals after the Start of the packet, for clock recovery purposes
      for i in range (4):
        await RisingEdge(self.low_clock)
        val = self.decode_val(self)
        if (val != 0):
          UVMError(self.name + "Expecting 4 sync Packet only received " + str(i))
      ##After the SYNC Packet, We Expect the PID to be received, which is a 8 bit field with 4 bits of data
      for i in range (4):
        await RisingEdge(self.low_clock)
        val[i] = self.decode_val(self)

      for i in range (1024*8):
        await RisingEdge(self.low_clock)
        val = self.decode(self)


  def decode_val(self):
    self.d_plus   = USB_Hispeed_If.d_plus
    self.d_minus  = USB_Hispeed_If.d_minus
    if(self.d_plus == self.d_plus_prev & self.d_minus == self.d_minus_prev):
      #Same values means no change in signals, which represents 0
      self.d_plus_prev  = self.d_plus
      self.d_minus_prev = self.d_minus
      return 1
    elif (self.d_plus != self.d_plus_prev & self.d_minus != self.d_minus_prev):
      #Change in values represents 1
      self.d_plus_prev  = self.d_plus
      self.d_minus_prev = self.d_minus
      return 0
    else:
      UVMError("Protocol Violation: Differentail Signals Expected d_plus:" + str(self.d_plus) + "d_minus" + str(self.d_minus))
