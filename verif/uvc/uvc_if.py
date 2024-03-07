from pyuvm import *
import pyuvm


class USB_uvc_if(uvm_object):

  def __init__(self, name, uvc_cfg):
    self.uvc_cfg      = uvc_cfg
    self.dut          = cocotb.top
    self.device_if_a  = [USB_Lowspeed_If("usb_device", self.dut, i) for i in range(self.uvc_cfg.number_of_devices)]
    self.host_if      = USB_Hispeed_If("usb_host", self.dut)
    super().__init__(name=name)

class USB_Lowspeed_If():

  def __init__(self, name, Dut, device_num):
    self.dut      = Dut
    self.name     = name + str(device_num)
    self.d_plus   = self.dut.device_d_plus.value[device_num]
    self.d_minus  = self.dut.device_d_minus.value[device_num]
    #ISMAIL_TODO check how to connect a unpacked to packed connection

    
class USB_Hispeed_If():

  def __init__(self, name, Dut):
    self.dut      = Dut
    self.name     = name
    self.hi_clock = self.dut.hi_clock
    self.low_clock= self.dut.low_clock
    self.d_plus   = self.dut.host_d_plus
    self.d_minus  = self.dut.host_d_minus
    self.tx_plus  = self.dut.host_tx_plus
    self.tx_minus = self.dut.host_tx_minus
    self.rx_plus  = self.dut.host_rx_plus
    self.rx_minus = self.dut.host_rx_minus



# $$##To Do tomorrow: USB_UVC: //25-02-24 Make the driver wait half a clock with a negedge clock