from pyuvm import *
import random

class USB_uvc_cfg (uvm_object):

  device_address_list = []

  def __init__(self, name):
    self.number_of_devices = int(ConfigDB().get(None, "", "number_of_devices"))
    self.choose_device_address()
    super().__init__(name=name)
  
  def choose_device_address(self):
    for i in range (self.number_of_devices):
      self.device_address_list.append(random.randint(0,128))
