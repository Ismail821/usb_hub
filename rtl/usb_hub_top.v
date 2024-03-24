module usb_hub_top #(
  parameter NUM_USB_DEVICES = 2
) (
  input  wire hi_clock,
  input  wire low_clock,
  inout  wire host_d_plus,
  inout  wire host_d_minus,
  output wire host_tx_plus,
  output wire host_tx_minus,
  input  wire host_rx_plus,
  input  wire host_rx_minus,
  inout  wire [NUM_USB_DEVICES-1:0] device_d_plus,
  inout  wire [NUM_USB_DEVICES-1:0] device_d_minus,

  //======Debug Signals, Doesn't have any Functional useage but very helpful in Debug======
  input  wire [63:00] cycle,
  input  wire [03:00] host_low_packet_state,
  input  wire [(NUM_USB_DEVICES*4)-1:00] dev_low_packet_state 
);
  
//This Top Module shall serve as the outer most RTL module which shall have all other submodules
//All the External Port Connections should come through this &
// for the Sake of this project the Clock is also Connected through This

endmodule