module usb_hub_top #(
  parameter NUM_USB_DEVICES = 16
) (
  output  reg hi_clock,
  input   low_clock,
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


 initial hi_clock = 0;
 always #5 hi_clock = ~hi_clock;

initial begin
  $display("Initial:");

end
  
//This Top Module shall serve as the outer most RTL module which shall have all other submodules
//All the External Port Connections should come through this &
// for the Sake of this project the Clock is also Connected through This

endmodule