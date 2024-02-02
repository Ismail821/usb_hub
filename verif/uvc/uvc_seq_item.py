from pyuvm import uvm_sequence_item
from pyuvm import uvm_root
from pyuvm import UVMError
import random
import cocotb
import crcmod
import logging

class USB_Lowspeed_Data_Seq_Item(uvm_sequence_item):

  NAME = "[USB_lowspeed_Data_Sequence_item]"
  DATA_MAX_BYTES  = 1024                #Usb 2.0 Spec Section 8.3.4 Says the Data Can by anywhere from 0 to 1024 Bytes
  CRC_POLYNOMIAL  = 0b1000000000000101
  CRC_REMAINDER   = 0b1000000000001101

  def __init__(self, name):
    super().__init__(name)
    self.logger = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)


  def randomize(self):
    self.d_data   = 0
    self.d_data_bytes = self.DATA_MAX_BYTES
    self.d_crc        = self.CRC_REMAINDER
    self.d_data_bytes = random.randint(0,1024)
    self.d_data       = random.randint(0, 8*self.d_data_bytes)
    msg = "Randomized Data for transactions: 0x%0h", hex(self.d_data)
    self.logger.info(msg)

  def __eq__(self, other):
    if (self.d_data == other.d_data):
      msg  = "Data Comparision Succesfull Actual: "
      self.logger.info(self.NAME + msg +str(hex(self.d_data)))
    else:
      msg  = "Data Comparision Failed Actual: "
      self.logger.error(self.NAME + msg +str(hex(self.d_data)) + "Received: " + str(hex(other.d_data)))
      UVMError(self.NAME + msg +str(hex(self.d_data)) + "Received: " + str(hex(other.d_data)))
    return 

  def calculate_crc(self):
    #crcmod.mkCrcFun(self.CRC_POLYNOMIAL, False, )
    self.d_crc =  crcmod.Crc(self.CRC_POLYNOMIAL, initCrc=0xFFFF)
    msg = "Calculating CRC for Data: "
    uvm_root.self.logger.info(self.NAME + msg +str(self.d_data) + "CRC: " + str(self.d_crc._crc))
    return self.d_crc._crc
  
  def __str__(self):
    return f"D_Data: 0x{self.d_data:x}"


class USB_Hispeed_Data_Seq_Item(uvm_sequence_item):

  logger = logging.getLogger("hi_seq_item")
  logger.setLevel(logging.DEBUG)

  NAME = "[USB_hispeed_Data_Sequence_item]"
  DATA_MAX_BYTES  = 1024
  CRC_POLYNOMIAL  = 0b1000000000000101
  CRC_REMAINDER   = 0b1000000000001101
  ADDRESS_SIZE    = 8
  ADDRESS_MAX     = 2**ADDRESS_SIZE
  SUBTYPE_SIZE    = 4
  SUBTYPE_MAX     = 2**SUBTYPE_SIZE
  STREAM_ID_SIZE  = 16
  STREAM_ID_MAX   = 2**STREAM_ID_SIZE

  def __init__(self, name):
    super().__init__(name)
    self.type = 0x0   #Probably should be from driver
    self.address = 0x0
    self.subType = 0x0
    self.stream_id = 0x0
    self.packet_crc = 0x0
    self.d_data   = 0x0

  def randomize(self):
    self.address      = random.randint(0, self.ADDRESS_MAX)
    self.subType      = random.randint(0, self.SUBTYPE_MAX)
    self.stream_id    = random.randint(0, self.STREAM_ID_MAX)
    self.d_data_bytes = random.randint(0,1024)
    self.d_data       = random.randint(0, self.d_data_bytes)
    self.packet_crc   = crcmod.mkCrcFun() ##Need to check the proper input outputs for the function
    self.logger.info("Randomized Transactions")

  def __eq__(self, other):
    if (self.d_data == other.d_data):
      msg  = "Data Comparision Succesfull Actual: "
      self.logger.info(self.NAME + msg +str(self.d_data))
    else:
      msg  = "Data Comparision Failed Actual: "
      self.logger.erro
    return 

  def calculate_crc(self):
    #crcmod.mkCrcFun(self.CRC_POLYNOMIAL, False, )
    self.d_crc =  crcmod.Crc(self.CRC_POLYNOMIAL, initCrc=0xFFFF)
    msg = "Calculating CRC for Data: "
    self.logger.info(self.NAME + msg +str(self.d_data) + "CRC: " + str(self.d_crc._crc))
    return self.d_crc._crc
  
  def __str__(self):
    return f"D_Data: 0x{self.d_data:x}"
