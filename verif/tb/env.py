from pyuvm import *
from verif import *
from verif import USB_uvc_agent
from verif import USB_uvc_cfg
from verif import USB_Scoreboard
import cocotb
import pyuvm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class USB_env(uvm_env):

  def build_phase(self):
    self.host_hi_seqr     = uvm_sequencer("Host_Hi_Seqr",   self)
    self.host_low_seqr    = uvm_sequencer("Host_Low_Seqr",  self)
    self.number_of_devices= ConfigDB().get(None, "", "number_of_devices")
    self.device_seqr_a    = [uvm_sequencer("Device_Seqr",self) for i in range (self.number_of_devices)]
    self.scoreboard       = USB_Scoreboard("scoreboard", parent=self)
    self.uvc_cfg          = USB_uvc_cfg.create("uvc_cfg")
    self.uvc_agent        = USB_uvc_agent("uvc_agent", self.uvc_cfg, self)

    for i in range (self.number_of_devices):
      ConfigDB().set(None, "*", "Device_Seqr"+str(i), self.device_seqr_a[i])
    ConfigDB().set(None, "*", "Host_Hi_Seqr",  self.host_hi_seqr )
    ConfigDB().set(None, "*", "Host_Low_Seqr", self.host_low_seqr )
    logger.info(msg="hello everyone")

  def connect_phase(self):
    # self.uvc_agent.host_hi_drvr.seq_item_port.connect(self.seqr.seq_item_export)
    self.uvc_agent.host_hi_mon.hi_speed_ap.connect(self.scoreboard.host_hi_export)
    self.uvc_agent.host_low_mon.low_speed_ap.connect(self.scoreboard.host_low_export)
    for i in range (self.number_of_devices):
      self.uvc_agent.device_mon_a[i].low_speed_ap.connect(self.scoreboard.device_export_a[i])
    super().connect_phase()
