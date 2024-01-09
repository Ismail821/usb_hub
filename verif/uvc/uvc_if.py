class Uvc_If():

  def __init__(self, name, dut, num_devices):
    self.usb_lowspeed_if = [USB_Lowspeed_If("usb_device", dut, i) for i in range(num_devices)]
    self.usb_hispeed_if  = USB_Hispeed_If("usb_host", dut)

class USB_Lowspeed_If():

  def __init__(self, name, Dut, device_num):
    self.dut      = Dut
    self.name     = name + str(device_num)
    self.d_plus   = self.dut.device_d_plus[device_num]
    self.d_minus  = self.dut.device_d_minus[device_num]
    
class USB_Hispeed_If():

  def __init__(self, name, Dut):
    self.dut      = Dut
    self.name     = name
    self.d_plus   = self.dut.host_d_plus
    self.d_minus  = self.dut.host_d_minus
    self.tx_plus  = self.dut.host_tx_plus
    self.tx_minus = self.dut.host_tx_minus
    self.rx_plus  = self.dut.host_rx_plus
    self.rx_minus = self.dut.host_rx_minus
