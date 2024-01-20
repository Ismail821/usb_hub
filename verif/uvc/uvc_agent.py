from pyuvm import uvm_agent
from cocotb import *
from cocotb.clock import Clock
import cocotb

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
    
    self.uvc_if        = USB_uvc_if(name="uvc_interface_to_dut", uvc_cfg=self.uvc_cfg)

    self.device_mon_a  = [USB_Lowspeed_Monitor( name      ="device_mon"+str(i), 
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              low_clock   = self.low_clock,
                                              lowspeed_if = self.uvc_if.device_if_a[i]
                                            ) for i in range (self.uvc_cfg.number_of_devices)]
    # self.device_drvr[i]  = USB_Lowspeed_Monitor("device_mon"+str(i), self.vc_cfg)
    self.host_hi_mon   = USB_Hispeed_Monitor( name        = "host_hispeed_mon",
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              hi_clock    = self.hi_clock,
                                              hi_speed_if  = self.uvc_if.host_if
                                            )
    self.host_low_mon  = USB_Lowspeed_Monitor(name        = "host_lospeed_mon",
                                              uvc_cfg     = self.uvc_cfg,
                                              parent      = self,
                                              low_clock   = self.low_clock,
                                              lowspeed_if = self.uvc_if.host_if
                                            )
    # self.host_hi_drvr  = 
    # self.host_low_drvr = 

  def start_of_simulation_phase(self):
    self.host_hi_mon.start_of_simulation_phase()
    self.host_low_mon.start_of_simulation_phase()
    # self.generate_low_clock()
    # self.generate_hi_clock()
    # Join
    # self.host_hi_drvr
    # self.host_low_drvr
    for i in range (self.uvc_cfg.number_of_devices):
      self.device_mon_a[i].start_of_simulation_phase()
      # self.device_drvr[i]

  async def run_phase(self):
    Clock(self.low_clock, 100, 'us').start()
    Clock(self.hi_clock, 10, 'us').start()
    for i in range (10):
      RisingEdge(self.low_clock)
      clock += 1
    
    #cocotb.start_soon(clock(signal=self.low_clock, period=1000).start(cycles=100))
    #cocotb.start_soon(clock(signal=self.hi_clock, period=100).start(cycles=1000))


  # async def generate_low_clock(self):

  # async def generate_hi_clock(self):