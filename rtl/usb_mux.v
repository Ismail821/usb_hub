`define MUX_DEV_RANGE `WIDTH_TO_RANGE(NUMBER_OF_PISO)
`define MUX_DATA_RANGE1 `WIDTH_TO_RANGE(NUMBER_OF_PISO*`REQUEST_SERIAL_DATA_TYPE_WIDTH)

module usb_piso_tr_mux #(
  parameter NUMBER_OF_PISO = 1
  ) (
  //connections to the multiple PISO
  input wire [`MUX_DEV_RANGE] piso_data_out,
  input wire [`MUX_DEV_RANGE] piso_data_val,
  input wire [`MUX_DEV_RANGE] piso_data_last,
  input wire [`MUX_DEV_RANGE] piso_serial_data_avail,

  output reg [`MUX_DEV_RANGE]   piso_request_serial_data,
  output reg [`MUX_DATA_RANGE1] piso_request_serial_data_type,

  //connections to the single USB_TR
  output reg usb_tr_piso_data_out,
  output reg usb_tr_piso_data_val,
  output reg usb_tr_piso_data_last,
  output reg usb_tr_piso_serial_data_avail,

  input wire usb_tr_request_serial_data,
  input wire [`REQUEST_SERIAL_DATA_TYPE_RANGE] usb_tr_request_serial_data_type
);

  reg [$clog2(NUMBER_OF_PISO)-1:0] current_device;

  assign usb_tr_piso_serial_data_avail = | piso_serial_data_avail;


endmodule
