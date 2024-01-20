from cocotb.triggers import Join, Combine
from verif.seqs.sequence import USB_main_seq
from verif.tb.env import USB_env
from pyuvm import *
from verif import *
import pyuvm
import cocotb
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

##We can USB_base_test as the base test which will do only the necesary instantiation with default values.
##The derived testcases can define specific tests
@pyuvm.test(skip=True)
class USB_base_test(uvm_test):
  def build_phase(self):
    self.env = USB_env("USB_env", self)
    self.main_seq = USB_main_seq.create("main_seq")

  async def run_phase(self):
    self.raise_objection()
    main_seq_task = cocotb.start_soon(self.main_seq.start())
    self.drop_objection()

@pyuvm.test()
class USB_one_test(USB_base_test):
      
  def build_phase(self):
    ConfigDB().set(None, "", "number_of_devices", 1)
    logger.info("One Test Config - Number of Devices for the test = %s", 1)
    return super().build_phase()

  def end_of_elaboration_phase(self):
    ConfigDB().set(None,"", "Test_case", "test_one")
    super().end_of_elaboration_phase()

  def run_phase(self):
    return super().run_phase()