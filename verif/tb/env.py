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
    
    self.number_of_devices= ConfigDB().get(None, "", "number_of_devices")
    self.logger.info("ConfigDB Retrieved: Number of Devices for the test = %s", self.number_of_devices)

    self.logger.info("Creating all the sequencers and Registering it with ConfigDB")

    # self.host_hi_seqr     = uvm_sequencer("Host_hi_seqr",   self)
    # ConfigDB().set(None, "*", "Host_hi_seqr",  self.host_hi_seqr )
    # self.logger.info(msg="ConfigDB Registered: Host_hi_seqr")
    
    self.host_low_seqr    = uvm_sequencer("Host_low_seqr",  self)
    ConfigDB().set(None, "*", "Host_low_seqr", self.host_low_seqr )
    self.logger.info(msg="ConfigDB Registered: Host_low_seqr")

    self.device_seqr_a    = [uvm_sequencer("Device_seqr_"+str(i),self) 
                             for i in range (self.number_of_devices)]
    for i in range (self.number_of_devices):
      ConfigDB().set(None, "*", "Device_seqr_"+str(i), self.device_seqr_a[i])
      self.logger.info(msg="ConfigDB Registered: Device_seqr_"+str(i))

    ConfigDB().set(None, "*", "env", self)

    self.uvc_cfg          = USB_uvc_cfg.create("uvc_cfg")
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
    for i in range (self.number_of_devices):
      self.uvc_agent.device_drvr_a[i].seq_item_port.connect(self.device_seqr_a[i].seq_item_export)
    # import debugpy
    # listen_host, listen_port = debugpy.listen(("localhost", 1213))
    # self.logger.info("Waiting for Python debugger attach on {}:{}".format(listen_host, listen_port))
    # # Suspend execution until debugger attaches
    # debugpy.wait_for_client()
    super().connect_phase()
