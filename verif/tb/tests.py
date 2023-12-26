#Seqitem code copied from tinyalu testbench, needs modification
from cocotb.triggers import Join, Combine
from pyuvm import *
import cocotb
import pyuvm
import random

@pyuvm.test()
class usb_base_test(uvm_test):
  """Test ALU with random and max values"""
  #Eg: test_one should be a top level sequence which should create the Seperate request & Response sequence
  def build_phase(self):
    self.env = 0 #usb_env("env", self)

  def end_of_elaboration_phase(self):
    self.test_one           = 0 #test_one.create("test_one")
    #self.test_one_by_one    = test_one.create("test_one_by_one")
    #self.test_parallely     = test_one.create("test_parallely")

  async def run_phase(self):
    self.raise_objection()
    await self.test_one.start()
    self.drop_objection()