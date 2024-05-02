from pyuvm import uvm_sequence_item, ConfigDB, UVMError
from verif.uvc.uvc_enums import *
import queue
import crcmod
import pyuvm
import random
import cocotb
import logging

class USB_Lowspeed_Data_Seq_Item(uvm_sequence_item):

  NAME = "[USB_lowspeed_Data_Sequence_item]"
  DATA_MAX_BYTES  = 10                #Usb 2.0 Spec Section 8.3.4 Says the Data Can by anywhere from 0 to 1024 Bytes
  CRC_POLYNOMIAL  = 0b1000000000000101
  CRC_REMAINDER   = 0b1000000000001101
  req_type        = 0
  address         = 0
  end_point       = 0
  pid             = []
  crc             = []
  data            = 0
  data_bytes      = 0
  device_number   = 0

  def __init__(self, name):
    super().__init__(name)
    self.name   = name
    self.logger = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)
    self.uvc_cfg = ConfigDB().get(None, "", "uvc_cfg")


  def randomize(self, req):
    if(req):
      self.req_type     = random.choice(list(request_type))
      self.logger.warning("Choosen a Request of the Type" + self.req_type.name)
      if(self.req_type == request_type.WRITE):
        ##----------------Command-Packet-------------------------------##
        self.pid.append(pid_token_type.OUT)
        self.address      = random.choice(self.uvc_cfg.device_address_list)
        self.end_point    = random.randint(0, self.uvc_cfg.number_of_devices)
        # self.crc.append(self.calculate_crc())
        ##----------------Data-Packet----------------------------------##
        self.pid.append(pid_data_type.DATA0)
        self.data_bytes   = random.randint(0,self.DATA_MAX_BYTES)
        self.data         = random.randint(0, 2**self.data_bytes)
  
      elif(self.req_type == request_type.READ):
        ##----------------Command-Packet-------------------------------##
        self.pid.append(pid_token_type.IN)
        self.address      = random.choice(self.uvc_cfg.device_address_list)
        self.end_point    = random.randint(0, self.uvc_cfg.number_of_devices)
        # self.crc.append(self.calculate_crc())
        ##----------------Acknowledgement-Packet-----------------------##
        self.pid.append(pid_handshake_type.ACK)
    else:
        if(self.req_type == request_type.READ):
          ##----------------Data-Packet----------------------------------##
          self.pid.append(pid_data_type.DATA0)
          self.data_bytes = random.randint(0,self.DATA_MAX_BYTES)
          self.d_data       = random.randint(0, 8*self.data_bytes)
        if(self.req_type == request_type.WRITE):
          # self.crc.append(self.calculate_crc())
          ##----------------Acknowledgement-Packet-----------------------##
          self.pid.append(pid_handshake_type.ACK)

    self.logger.info("Randomized Data for transactions: 0x%0h", self.transaction_id)


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
    self.logger.info(self.NAME + msg +str(self.d_data) + "CRC: " + str(self.d_crc._crc))
    return self.d_crc._crc

  def crc16(data: bytes):
      xor_in = 0x0000  # initial value
      xor_out = 0x0000  # final XOR value
      poly = 0x8005  # generator polinom (normal form)

      reg = xor_in
      for octet in data:
          # reflect in
          for i in range(8):
              topbit = reg & 0x8000
              if octet & (0x80 >> i):
                  topbit ^= 0x8000
              reg <<= 1
              if topbit:
                  reg ^= poly
          reg &= 0xFFFF
          # reflect out
      return reg ^ xor_out  
  # def __str__(self):
  #   return f"D_Data: 0x{self.d_data:x}"


class USB_Hispeed_Data_Seq_Item(uvm_sequence_item):

  logger = logging.getLogger("hi_seq_item")
  logger.setLevel(logging.DEBUG)

  NAME = "[USB_hispeed_Data_Sequence_item]"
  DATA_MAX_BYTES  = 10
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
    self.data_bytes = random.randint(0,1024)
    self.d_data       = random.randint(0, self.data_bytes)
    # self.packet_crc   = crcmod.mkCrcFun() ##Need to check the proper input outputs for the function
    self.logger.info("Randomized Transactions")

  def __eq__(self, other):
    if (self.d_data == other.d_data):
      msg  = "Data Comparision Succesfull Actual: "
      self.logger.info(self.NAME + msg +str(self.d_data))
    else:
      msg  = "Data Comparision Failed Actual: "
      self.logger.error("")
    return 

  def calculate_crc(self):
    #crcmod.mkCrcFun(self.CRC_POLYNOMIAL, False, )
    self.d_crc =  crcmod.Crc(self.CRC_POLYNOMIAL, initCrc=0xFFFF)
    msg = "Calculating CRC for Data: "
    self.logger.info(self.NAME + msg +str(self.d_data) + "CRC: " + str(self.d_crc._crc))
    return self.d_crc._crc
  
  def __str__(self):
    return f"D_Data: 0x{self.d_data:x}"

