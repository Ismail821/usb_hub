from pyuvm import uvm_agent
from cocotb import *
from cocotb.clock import Clock
import cocotb
import logging

from cocotb.triggers import RisingEdge
from verif.uvc.uvc_if import USB_uvc_if
from verif.uvc.uvc_monitor import USB_Hispeed_Monitor
from verif.uvc.uvc_monitor import USB_Lowspeed_Monitor
from verif.uvc.usb_host_driver  import USB_hispeed_driver
from verif.uvc.usb_host_driver  import USB_lowspeed_host_driver
from verif.uvc.uvc_device_driver  import USB_lowspeed_device_driver

class USB_uvc_agent (uvm_agent):
  uvc_cfg   = None
  hi_clock  = None
  low_clock = None

  def __init__(self, name, uvc_cfg, parent):
    self.uvc_cfg  = uvc_cfg
    super().__init__(name, parent)
    self.logger = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)

  def build_phase(self):
    
    self.logger.info("Creating Interface")
    self.uvc_if        = USB_uvc_if(name="uvc_interface_to_dut", uvc_cfg=self.uvc_cfg)

    self.device_mon_a  = [USB_Lowspeed_Monitor( name      ="device_mon"+str(i), 
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              low_clock   = self.low_clock,
                                              lowspeed_if = self.uvc_if.device_if
                                            ) for i in range (self.uvc_cfg.number_of_devices)]
    self.logger.info(msg="Creating Low Speed Device Monitor Array")
    self.host_hi_mon   = USB_Hispeed_Monitor( name        = "host_hispeed_mon",
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              hi_clock    = self.hi_clock,
                                              hi_speed_if  = self.uvc_if.host_if
                                            )
    self.logger.info(msg="Creating Hi Speed Host Monitor ")
    self.host_low_mon  = USB_Lowspeed_Monitor(name        = "host_lospeed_mon",
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              low_clock   = self.low_clock,
                                              lowspeed_if = self.uvc_if.host_if
                                            )
    self.logger.info(msg="Creating Low Speed Host Monitor")

    self.device_drvr_a  = [USB_lowspeed_device_driver( name      ="device_drvr"+str(i), 
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              lowspeed_if = self.uvc_if.device_if,
                                              i           = i
                                            ) for i in range (self.uvc_cfg.number_of_devices)]
    self.logger.info(msg="Creating Low Speed Device driver Array")
    self.host_hi_drvr   = USB_hispeed_driver( name        = "host_hispeed_drvr",
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              hi_clock    = self.hi_clock,
                                              hi_speed_if = self.uvc_if.host_if
                                            )
    self.logger.info(msg="Creating Hi Speed Host driver ")
    self.host_low_drvr  = USB_lowspeed_host_driver(name        = "host_lowspeed_drvr",
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              lowspeed_if = self.uvc_if.host_if,
                                              i           = 0
                                            )
    self.host_low_drvr.is_host_driver = 1

  async def run_phase(self):
    self.cycle = 0
    self.logger.info(msg="Starting Low Clock generation")
    cocotb.start_soon(self.generate_low_clock())
    self.logger.info(msg="Starting Hi Clock generation")
    cocotb.start_soon(self.generate_hi_clock())
    cocotb.start_soon(self.count_clock())

  async def generate_low_clock(self):
    self.logger.info(msg="Starting Clock generation")
    self.uvc_if.dut.low_clock.value = 0
    self.low_clock = self.uvc_if.dut.low_clock
    cocotb.start_soon(Clock(self.uvc_if.dut.hi_clock, 10, 'step').start())

  async def generate_hi_clock(self):
    self.logger.info(msg="Starting Clock generation")
    self.uvc_if.dut.hi_clock.value = 0
    self.hi_clock = self.uvc_if.dut.hi_clock
    cocotb.start_soon(Clock(self.uvc_if.dut.low_clock, 100, 'step').start())

  async def count_clock(self):
    while True:
      await RisingEdge(self.uvc_if.dut.low_clock)
      self.uvc_if.dut.cycle.value = self.cycle
      self.cycle += 1
      self.logger.debug(msg="Low Clock Advanced: Current cycle (Low clock) = "+str(self.cycle))