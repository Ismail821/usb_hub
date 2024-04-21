//Common Macros

`define MAX_NUM_USB_DEVICES 16
`define WIDTH_TO_RANGE(width) width-1:0
//Usage: `def <MY_RANGE> `WIDTH_TO_RANGE(WIDTH_PARAMETER)

`define REQUEST_SERIAL_DATA_READ 0
`define REQUEST_SERIAL_DATA_ACK  1

`define SIMULATION

`define ERROR(input_string)\
  $display("RTL Error: %s, from Module %m", input_string); \
  $finish

parameter USB_TR_STATE_TOGGLE
parameter USB_TR_STATE_IDLE
parameter USB_TR_STATE_Z