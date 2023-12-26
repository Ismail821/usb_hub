from pyuvm import *
import cocotb
import pyuvm

class USB_Env(uvm_env):

  def build_phase(self):
    self.seqr = uvm_sequencer("seqr", self)
    ConfigDB().set(None, "*", "SEQR", self.seqr)
    """
    self.scoreboard = Scoreboard("scoreboard", self)
    self.uvc_host   = USB_uvc("usb_host", self)
    self.uvc_device = USB_uvc("usb_device", self)
    """

  def connect_phase(self):
    self.usb_host.driver.seq_item_port.connect(self.seqr.seq_item_export)
    self.usb_host.mon.connect(self.scoreboard.usb_host_export)
    self.usb_device.mon.connect(self.scoreboard.usb_device_export)
    return super().connect_phase()
