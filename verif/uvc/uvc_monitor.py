from cocotb.triggers import RisingEdge
from pyuvm import uvm_monitor
from pyuvm import uvm_analysis_port
from pyuvm import UVMError
from verif.uvc.uvc_seq_item import USB_Hispeed_Data_Seq_Item, USB_Lowspeed_Data_Seq_Item

#refer to the __init__.py file under the uvc folder, it imports all the files under uvc folder

class USB_Hispeed_Monitor(uvm_monitor):

  def __init__(self, name, uvc_cfg, hi_speed_if, hi_clock, parent):
    self.name         = name
    self.hi_speed_if  = hi_speed_if
    self.hi_clock     = hi_clock
    self.hispeed_data = USB_Hispeed_Data_Seq_Item(name = name+"_seq_item")
    super().__init__(name, parent)

  def build_phase(self):
    self.hi_speed_ap   = uvm_analysis_port(self.name+"_hi_speed_ap", self)
    super().build_phase()

  def connect_phase(self):
    self.hi_clock = self.hi_speed_if.dut.hi_clock
    self.tx_plus  = self.hi_speed_if.tx_plus
    self.tx_minus = self.hi_speed_if.tx_minus
    self.rx_plus  = self.hi_speed_if.rx_plus
    self.rx_minus = self.hi_speed_if.tx_minus
    super().connect_phase()


  async def run_phase(self):
    await self.monitor_transactions()

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
  lowspeed_if = None
  low_clock   = None

  def __init__(self, name, uvc_cfg, low_clock, lowspeed_if, parent):
    self.name     = name
    self.lowspeed_data = USB_Lowspeed_Data_Seq_Item(name=name+"_seq_item")
    super().__init__(name, parent)

  def build_phase(self):
    self.low_speed_ap   = uvm_analysis_port(self.name+"_low_speed_ap", self)
    super().build_phase

  async def run_phase(self):
    self.monitor_transactions()
    await super().run_phase()
  
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
    self.d_plus   = self.lowspeed.d_plus
    self.d_minus  = self.hi_speed_if.d_minus
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
