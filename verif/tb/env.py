from pyuvm import *
from verif import *
from verif import USB_uvc_agent, USB_uvc_cfg, USB_Scoreboard
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
import logging


class USB_env(uvm_env):

  def __init__(self, name, parent):
    super().__init__(name, parent)
    self.logger = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)
    self.dut = cocotb.top


  def build_phase(self):
    
    self.number_of_devices= int(ConfigDB().get(None, "", "number_of_devices"))
    self.logger.info("ConfigDB Retrieved: Number of Devices for the test = %s", self.number_of_devices)

    self.logger.info("Creating all the sequencers and Registering it with ConfigDB")

    # self.host_hi_seqr     = uvm_sequencer("Host_hi_seqr",   self)
    # ConfigDB().set(None, "*", "Host_hi_seqr",  self.host_hi_seqr )
    # self.logger.info(msg="ConfigDB Registered: Host_hi_seqr")
    
    self.host_low_seqr    = uvm_sequencer("Host_low_seqr",  self)
    ConfigDB().set(None, "*", "Host_low_seqr", self.host_low_seqr )
    self.logger.info(msg="ConfigDB Registered: Host_low_seqr")

    self.host_hi_seqr    = uvm_sequencer("Host_hi_seqr",  self)
    ConfigDB().set(None, "*", "Host_hi_seqr", self.host_low_seqr )
    self.logger.info(msg="ConfigDB Registered: Host_hi_seqr")

    self.device_seqr_a    = [uvm_sequencer("Device_seqr_"+str(i),self) for i in range (self.number_of_devices)]
    for i in range (self.number_of_devices):
      ConfigDB().set(None, "*", "Device_seqr_"+str(i), self.device_seqr_a[i])
      self.logger.info(msg="ConfigDB Registered: Device_seqr_"+str(i))
    
    self.uvc_cfg          = USB_uvc_cfg.create("uvc_cfg")
    ConfigDB().set(None, "*", "uvc_cfg", self.uvc_cfg)
    self.uvc_agent        = USB_uvc_agent("uvc_agent", self.uvc_cfg, self)
    self.scoreboard       = USB_Scoreboard("scoreboard", parent=self)


  def connect_phase(self):
    self.logger.info("Starting Env Connect Phase")
    self.logger.info("Connecting monitors with Scoreboard export's")
    self.uvc_agent.host_low_mon.low_speed_ap.connect(self.scoreboard.host_low_export)
    for i in range (self.number_of_devices):
      self.uvc_agent.device_mon_a[i].low_speed_ap.connect(self.scoreboard.device_export_a[i])
    
    self.logger.info("Connecting drivers with Sequencer's export")
    self.uvc_agent.host_low_drvr.seq_item_port.connect(self.host_low_seqr.seq_item_export)
    self.logger.debug("Connecting Driver: %s with Sequencer: %s", self.uvc_agent.host_low_drvr.name, self.host_low_seqr.name)
    self.uvc_agent.host_hi_drvr.seq_item_port.connect(self.host_hi_seqr.seq_item_export)
    self.logger.debug("Connecting Driver: %s with Sequencer: %s", self.uvc_agent.host_hi_drvr.name, self.host_hi_seqr.name)
    for i in range (self.number_of_devices):
      self.uvc_agent.device_drvr_a[i].seq_item_port.connect(self.device_seqr_a[i].seq_item_export)
      self.logger.debug("Connecting Driver: %s with Sequencer: %s", self.uvc_agent.device_drvr_a[i].name, self.device_seqr_a[i].name)
    # import debugpy
    # listen_host, listen_port = debugpy.listen(("localhost", 1213))
    # self.logger.info("Waiting for Python debugger attach on {}:{}".format(listen_host, listen_port))
    # # Suspend execution until debugger attaches
    # debugpy.wait_for_client()
    super().connect_phase()

  def start_of_simulation_phase(self):
    self.logger.critical("Starting Generation of Clocks")
    self.logger.critical(msg="Starting Clock generation")
    self.logger.critical(msg="Starting Clock generation")
    # self.generate_hi_clock()
    # self.generate_low_clock()
    self.logger.critical("Done Starting Generation of Clocks")
    super().start_of_simulation_phase()


  async def run_phase(self):
    self.count_cycles()

  async def count_cycles(self):
    while True:
      await RisingEdge(self.uvc_agent.uvc_if.dut.hi_clock)
      self.cycles=+1

  async def generate_hi_clock(self):
    self.logger.critical(msg="Starting Clock generation")
    # fork(Clock(self.dut.hi_clock, 10, "step").start())
    Clock(self.dut.hi_clock, 10, "step").start()

  async def generate_low_clock(self):
    self.logger.critical(msg="Starting Clock generation")
    # fork(Clock(signal=self.dut.low_clock, period=100, units="step").start())
    Clock(signal=self.dut.low_clock, period=1, units="step").start()