from pyuvm import *
import random

class USB_uvc_cfg (uvm_object):

  device_address_list = []
  logger = logging.getLogger("uvc_cfg")
  logger.setLevel(DEBUG)

  def __init__(self, name):
    self.number_of_devices = int(ConfigDB().get(None, "", "number_of_devices"))
    self.logger.debug("Retrieved Number of Devices for test = %0d", self.number_of_devices)
    self.choose_device_address()
    super().__init__(name=name)
  
  def choose_device_address(self):
    for i in range (self.number_of_devices):
      rand_address = random.randint(1,128)
      self.device_address_list.append(rand_address)
      self.logger.debug("Choosen address for device[%0d] is 0x%0x", i, rand_address)
