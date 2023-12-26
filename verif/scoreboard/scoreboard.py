#Scoreboard code copied from tinyalu testbench, needs modification
from pyuvm import *
import cocotb
import pyuvm

class Scoreboard(uvm_component):

    def build_phase(self):
        self.cmd_fifo = uvm_tlm_analysis_fifo("cmd_fifo", self)
        self.result_fifo = uvm_tlm_analysis_fifo("result_fifo", self)
        self.cmd_get_port = uvm_get_port("cmd_get_port", self)
        self.result_get_port = uvm_get_port("result_get_port", self)
        self.cmd_export = self.cmd_fifo.analysis_export
        self.result_export = self.result_fifo.analysis_export

    def connect_phase(self):
        self.cmd_get_port.connect(self.cmd_fifo.get_export)
        self.result_get_port.connect(self.result_fifo.get_export)

    def check_phase(self):
        passed = True
        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False
        while self.result_get_port.can_get():
            _, actual_result = self.result_get_port.try_get()
            cmd_success, cmd = self.cmd_get_port.try_get()
            if not cmd_success:
                self.logger.critical(f"result {actual_result} had no command")
            else:
                (A, B, op_numb) = cmd
                #op = Ops(op_numb)
                #predicted_result = alu_prediction(A, B, op, self.errors)
                #if predicted_result == actual_result:
                #    self.logger.info(f"PASSED: 0x{A:02x} {op.name} 0x{B:02x} ="
                #                     f" 0x{actual_result:04x}")
                #else:
                #    self.logger.error(f"FAILED: 0x{A:02x} {op.name} 0x{B:02x} "
                #                      f"= 0x{actual_result:04x} "
                #                      f"expected 0x{predicted_result:04x}")
                #    passed = False
        assert passed