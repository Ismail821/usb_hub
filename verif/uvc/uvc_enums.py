from enum import Enum, auto

class request_type(Enum):
  WRITE   = auto()
  READ    = auto()

class packet_pid_type(Enum):
  TOKEN     = auto()
  DATA      = auto()
  HANDSHAKE = auto()
  SPECIAL   = auto()

class usb_txn_type(Enum):
  DIFFERENTIAL  = auto()
  SE0           = auto()
  SE1           = auto()

class pid_token_type(Enum):
  OUT   = 0b0001
  IN    = 0b1001
  SOF   = 0b0101
  SETUP = 0b1011
  RES   = 0b0000

class pid_data_type(Enum):
  DATA0 = 0b0011
  DATA1 = 0b1011
  DATA2 = 0b0111
  MDATA = 0b1111

class pid_handshake_type(Enum):
  ACK   = 0b0010
  NAK   = 0b1010
  STALL = 0b1110
  NYET  = 0b0110

class pid_special_type(Enum):
  PRE   = 0b1100
  ERR   = 0b1100
  SPLIT = 0b1000
  PING  = 0b0100

class DEBUG_PACKET(Enum):
  DONE            = 0b0000
  SYNC_PACKET     = 0b0001
  TOKEN_PKT_WRITE = 0b0010
  TOKEN_PKT_READ  = 0b0011
  ADDRESS_PACKET  = 0b0100
  CRC_PACKET      = 0b0101
  DATA_PACKET_PID = 0b0110
  DATA_PACKET_DATA= 0b0111

class usb_state(Enum):
  J_STATE   = 0b01
  K_STATE   = 0b10
  #d_minus, d_plus