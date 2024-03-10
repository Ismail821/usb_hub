from pyuvm import uvm_sequence
from cocotb.triggers import Timer
import verif.uvc.uvc_cfg
import cocotb

class uvc_sequence(uvm_sequence):

  uvc_cfg = None

  async def body(self):
    self.logger.critical("BODY of the Sequence should be overridded by the extended Class")
  
  async def wait_low_clock(self, clocks):
    for i in range (clocks):
      await Timer(100,"step")