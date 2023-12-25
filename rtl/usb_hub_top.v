module usb_hub_top #(
  parameter NUM_USB_DEVICES = 16
) (
  inout   host_d_plus,
  inout   host_d_minus,
  output  host_tx_plus,
  output  host_tx_minus,
  input   host_rx_plus,
  input   host_rx_minus,
//The Input output of the module are based on the direction of the RTL.
//The Naming scheme is <Connection_side>_<Signal>_<Plus/Minus>
  inout [NUM_USB_DEVICES-1:0] device_d_plus,
  inout [NUM_USB_DEVICES-1:0] device_d_minus
);
  
//This Top Module shall serve as the outer most RTL module which shall have all other submodules


endmodule