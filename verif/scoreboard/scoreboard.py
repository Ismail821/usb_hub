#Scoreboard code copied from tinyalu testbench, needs modification
from pyuvm import *
import cocotb
import pyuvm
import logging
logger = logging.getLogger()

class USB_Scoreboard(uvm_component):

  def build_phase(self):
    self.host_hi_fifo       = uvm_tlm_analysis_fifo("host_hi_fifo", self)
    self.host_low_fifo      = uvm_tlm_analysis_fifo("host_low_fifo", self)
    self.device_fifo_a      = [ uvm_tlm_analysis_fifo("device_fifo_"+str(i), self)
                                for i in range (ConfigDB().get(None, "", "number_of_devices"))]
    # self.cmd_get_port       = uvm_get_port("cmd_get_port", self)
    # self.result_get_port    = uvm_get_port("result_get_port", self)
    self.host_hi_export     = self.host_hi_fifo.analysis_export
    self.host_low_export    = self.host_low_fifo.analysis_export
    self.device_export_a    = [ self.device_fifo_a[i].analysis_export 
                              for i in range (ConfigDB().get(None, "", "number_of_devices")) ]

  # def connect_phase(self):
  #   self.cmd_get_port.connect(self.cmd_fifo.get_export)
  #   self.result_get_port.connect(self.result_fifo.get_export)

  # def check_phase(self):
    # passed = True
    # try:
    #   self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
    # except UVMConfigItemNotFound:
    #   self.errors = False
    # while self.result_get_port.can_get():
    #   _, actual_result = self.result_get_port.try_get()
    #   cmd_success, cmd = self.cmd_get_port.try_get()
    # if not cmd_success:
    #   self.logger.critical(f"result {actual_result} had no command")
    # else:
    #   (A, B, op_numb) = cmd
      #op = Ops(op_numb)
      #    self.logger.info(f"PASSED: 0x{A:02x} {op.name} 0x{B:02x} ="
      #                     f" 0x{actual_result:04x}")
      #else:
      #    self.logger.error(f"FAILED: 0x{A:02x} {op.name} 0x{B:02x} "
      #                      f"= 0x{actual_result:04x} "
      #                      f"expected 0x{predicted_result:04x}")
      #    passed = False
    # assert passed