from pyuvm import uvm_agent
from uvc import *
from uvc import USB_Lowspeed_Monitor
from uvc import USB_Hispeed_Monitor

class USB_usb_agent (uvm_agent):
  
  def build_phase(self, usb_uvc_cfg, uvc_if):
    self.uvc_cfg    = usb_uvc_cfg
    self.uvc_if     = uvc_if
    for i in range (self.uvc_cfg.number_of_devices):
      self.device_mon[i]  = USB_Lowspeed_Monitor("device_mon"+str(i), self.uvc_cfg)
      # self.device_drvr[i]  = USB_Lowspeed_Monitor("device_mon"+str(i), self.vc_cfg)
    self.host_hi_mon   = USB_Hispeed_Monitor("host_hispeed_mon", self.uvc_cfg)
    self.host_low_mon  = USB_Lowspeed_Monitor("host_lospeed_mon", self.uvc_cfg)
    # self.host_hi_drvr  = 
    # self.host_low_drvr = 

  def connect_phase(self):
    for i in range (self.uvc_cfg.number_of_devices):
      self.device_mon[i].lowspeed_if = self.uvc_if.lowspeed_if_a[i]
    self.host_mon.hispeed_if = self.uvc_if.hispeed_if

  def start_of_simulation_phase(self):
    self.host_mon.start_of_simulation_phase()
    # self.host_hi_drvr
    # self.host_low_drvr
    for i in range (self.uvc_cfg.number_of_devices):
      self.device_mon[i].start_of_simulation_phase()
      # self.device_drvr[i]