from pyuvm import uvm_sequence
from pyuvm import ConfigDB
from cocotb.triggers import Timer
import verif.uvc.uvc_cfg
import cocotb

class uvc_sequence(uvm_sequence):

  uvc_cfg = None

  async def body(self):
    self.logger.critical("BODY of the Sequence should be overridded by the extended Class")
  
  async def wait_low_clock(self, clocks):
    single_clock_time = ConfigDB().get(None, "", "low_clock_period")
    for i in range (clocks):
      await Timer(single_clock_time,"step")