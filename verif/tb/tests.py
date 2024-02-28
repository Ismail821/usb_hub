from cocotb.triggers import Join, Combine
from verif.seqs.sequence import USB_main_seq
from verif.tb.env import USB_env
from pyuvm import *
from verif import *
import pyuvm
import cocotb
import logging


##We can USB_base_test as the base test which will do only the necesary instantiation with default values.
##The derived testcases can define specific tests
class USB_base_test(uvm_test):

  def __init__(self, name, parent):
    name   = "usb_base_test"
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    super().__init__(name, parent)

  def build_phase(self):
    logger.info("Creating USB_env")
    print("\n\n--------------------------------START-OF-BUILD-PHASE---------------------------------------\n\n")
    self.env = USB_env("Usb_Env", self)
    logger.info("Creating Main Sequence")
    self.main_seq = USB_main_seq.create("main_seq")

  def connect_phase(self):
    print("\n\n--------------------------------START-OF-CONNECT-PHASE---------------------------------------\n\n")
    self.logger.info("usb test, in connect phase")
    return super().connect_phase()

  def end_of_elaboration_phase(self):
    print("\n\n--------------------------------END-OF-ELABORATION-PHASE---------------------------------------\n\n")
    self.logger.info("usb test, done with Elaboration phase")
    return super().end_of_elaboration_phase()
  
  def start_of_simulation_phase(self):
    print("\n\n--------------------------------START-OF-SIMULATION-PHASE---------------------------------------\n\n")
    return super().start_of_simulation_phase()

  async def run_phase(self):
    self.raise_objection()
    print("\n\n--------------------------------START-OF-RUN-PHASE---------------------------------------\n\n")
    logger.info("Main Sequence Start")
    main_seq_task = cocotb.start(self.main_seq.start())
    await(main_seq_task)
    logger.info("Main Sequence excecution Finished Waiting 1 second")
    self.drop_objection()

@pyuvm.test()
class USB_one_test(USB_base_test):
      
  def __init__(self, name, parent):
    name   = "usb_one_test"
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    super().__init__(name, parent)

  def build_phase(self):
    ConfigDB().set(None, "", "number_of_devices", 1)
    logger.info("Build_Phase: ConfigDB - Number of Devices for the test = %s", 1)
    return super().build_phase()

  def end_of_elaboration_phase(self):
    ConfigDB().set(None,"", "Test_case", "test_one")
    logger.info("End_of_Elab_Phase: ConfigDB Registering Testcase name")
    super().end_of_elaboration_phase()

  def run_phase(self):
    return super().run_phase()