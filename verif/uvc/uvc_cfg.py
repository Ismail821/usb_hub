from pyuvm import *
import random

class USB_uvc_cfg (uvm_object):

  device_address = []

  def __init__(self, name):
    self.number_of_devices = ConfigDB().get(None, "", "number_of_devices")
    self.choose_device_address()
    super().__init__(name=name)
  
  def choose_device_address(self):
    self.device_address = [random.randint(0,128) for i in self.number_of_devices]
