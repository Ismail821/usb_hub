from pyuvm import *
import pyuvm
import random
import cocotb
import crcmod

class usb_lowspeed_data_seq_item(uvm_sequence_item):

  NAME = "[USB_Host_D_Sequence_item]"
  DATA_MAX_BYTES  = 1024                #Usb 2.0 Spec Section 8.3.4 Says the Data Can by anywhere from 0 to 1024 Bytes
  CRC_POLYNOMIAL  = 0b1000000000000101
  CRC_REMAINDER   = 0b1000000000001101

  def __init__(self, name):
    super().__init__(name)
    self.d_data   = 0
    self.d_data_bytes = self.DATA_MAX_BYTES
    self.d_crc        = self.CRC_REMAINDER

  def randomize(self):
    self.d_data_bytes = random.randint(0,1024)
    self.d_data       = random.randint(0, self.data_bytes)

  def __eq__(self, other):
    if (self.d_data == other.d_data):
      msg  = "Data Comparision Succesfull"
      uvm_root.logger.info(self.NAME + msg +str(self.d_data))
    else:
      msg  = "Data Comparision Failed"
      uvm_root.logger.info(self.NAME + msg +str(self.d_data))
    return 

  def calculate_crc(self):
    crcmod.mkCrcFun(self.d_data, self.CRC_POLYNOMIAL, False, )