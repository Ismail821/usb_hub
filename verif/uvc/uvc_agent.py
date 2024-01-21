from pyuvm import uvm_agent
from cocotb import *
from cocotb.clock import Clock
import cocotb
import logging
logger = logging.getLogger("Uvc")
logger.setLevel(logging.DEBUG)

from cocotb.triggers import RisingEdge
from verif.uvc.uvc_if import USB_uvc_if
from verif.uvc.uvc_monitor import USB_Hispeed_Monitor
from verif.uvc.uvc_monitor import USB_Lowspeed_Monitor

class USB_uvc_agent (uvm_agent):
  uvc_cfg   = None
  hi_clock  = None
  low_clock = None

  def __init__(self, name, uvc_cfg, parent):
    self.uvc_cfg = uvc_cfg
    super().__init__(name=name, parent=parent)

  def build_phase(self):
    
    logger.info(msg="Creating Interface")
    self.uvc_if        = USB_uvc_if(name="uvc_interface_to_dut", uvc_cfg=self.uvc_cfg)

    self.device_mon_a  = [USB_Lowspeed_Monitor( name      ="device_mon"+str(i), 
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              low_clock   = self.low_clock,
                                              lowspeed_if = self.uvc_if.device_if_a[i]
                                            ) for i in range (self.uvc_cfg.number_of_devices)]
    logger.info(msg="Creating Low Speed Device Monitor Array")
    # self.device_drvr[i]  = USB_Lowspeed_Monitor("device_mon"+str(i), self.vc_cfg)
    self.host_hi_mon   = USB_Hispeed_Monitor( name        = "host_hispeed_mon",
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              hi_clock    = self.hi_clock,
                                              hi_speed_if  = self.uvc_if.host_if
                                            )
    logger.info(msg="Creating Hi Speed Host Monitor ")
    self.host_low_mon  = USB_Lowspeed_Monitor(name        = "host_lospeed_mon",
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              low_clock   = self.low_clock,
                                              lowspeed_if = self.uvc_if.host_if
                                            )
    logger.info(msg="Creating Hi Speed Device Monitor ")
    # self.host_hi_drvr  = 
    # self.host_low_drvr = 

  async def run_phase(self):
    self.cycle = 0
    logger.info(msg="Starting Low Clock generation")
    self.generate_low_clock()
    logger.info(msg="Starting Hi Clock generation")
    self.generate_hi_clock()
    for i in range (10):
      await RisingEdge(self.uvc_if.dut.low_clock)
      self.cycle += 1
      logger.info(msg="Hello Current cycle (Low clock) = "+str(self.cycle))

  async def generate_low_clock(self):
    logger.info(msg="Starting Clock generation")
    Clock(self.uvc_if.dut.hi_clock, 10, 'us').start()

  async def generate_hi_clock(self):
    logger.info(msg="Starting Clock generation")
    Clock(self.uvc_if.dut.low_clock, 100, 'us').start()