from uvc import *
from pyuvm import *

class USB_uvc_cfg (uvm_object):

  def build_phase(self):
    self.number_of_devices = 1
