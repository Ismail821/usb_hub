from pyuvm import *

class USB_uvc_cfg (uvm_object):

  def __init__(self, name):
    self.number_of_devices = ConfigDB().get(None, "", "number_of_devices")
    super().__init__(name=name)
