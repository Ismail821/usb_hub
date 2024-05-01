`include "rtl/includes.v"

`define DEV_RANGE `WIDTH_TO_RANGE(NUM_USB_DEVICES)

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
  inout  wire [`DEV_RANGE] device_d_plus,
  inout  wire [`DEV_RANGE] device_d_minus,

  //======Debug Signals, Doesn't have any Functional useage but very helpful in Debug======
  input  wire [63:00] cycle,
  inout  wire [03:00] host_low_packet_state,
  inout  wire [03:00][`DEV_RANGE] dev_low_packet_state
);

//This Top Module shall serve as the outer most RTL module which shall have all other submodules
//All the External Port Connections should come through this &
// for the Sake of this project the Clock is also Connected through This

wire [`DEV_RANGE] reset;
wire [`DEV_RANGE] piso_data_out;
wire [`DEV_RANGE] piso_data_val;
wire [`DEV_RANGE] piso_request_data;
wire [`DEV_RANGE] piso_data_last;
wire [`DEV_RANGE] fifo_empty;
wire [`DEV_RANGE] piso_serial_data_avail;
wire [NUM_USB_DEVICES*8-1:0] fifo_rd_data;
wire [NUM_USB_DEVICES*2-1:0] j_states;
wire [NUM_USB_DEVICES*2-1:0] k_states;
wire [NUM_USB_DEVICES*2-1:0] idle_states;
wire [`DEV_RANGE] trans_rcvr_request_piso_data;
wire [NUM_USB_DEVICES*`REQUEST_SERIAL_DATA_TYPE_WIDTH-1:0] 
                  trans_rcvr_request_piso_data_type;
wire [`DEV_RANGE] polling_clock;

wire [NUM_USB_DEVICES*2-1:0] usb_signals;

genvar i;
generate
  for (i=0; i<NUM_USB_DEVICES; i=i+1) begin
    assign usb_signals[(i*2)]   = device_d_plus[i];
    assign usb_signals[(i*2)+1] = device_d_minus[i];
  end
endgenerate

usb_host_speed_detector host_speed_detector[`DEV_RANGE] (
.clock(low_clock),
.reset(reset),
.usb_signals(usb_signals),
.j_state(j_states),
.k_state(k_states),
.idle_state(idle_states)
);

polling_clock_gen #(
  .NUMBER_OF_OUTPUT_CLOCKS(NUM_USB_DEVICES),
  .TIME_PERIOD_PCLOCK(100)
)host_pclock_gen(
  .clock(low_clock),
  .reset(reset),
  .polling_clock(polling_clock)
);

usb_host_trans_receiver host [`DEV_RANGE](
  .clock(low_clock),
  .polling_clock(polling_clock),
  .reset(reset),
  .IDLE_state(idle_states),
  .J_state(j_states),
  .K_state(k_states),
  .serial_data_in(piso_data_out),
  .serial_data_in_val(piso_data_val),
  .serial_data_in_last(piso_data_last),
  .serial_data_in_avail(piso_serial_data_avail),
  .request_serial_data(trans_rcvr_request_piso_data),
  .request_serial_data_type(trans_rcvr_request_piso_data_type),
  .serial_data_out(),             //SIPO
  .serial_data_out_val(),         //SIPO
  .SIPO_empty(1'd0),
  .usb_signals(usb_signals)
);

piso host_piso [`DEV_RANGE] (
  .clk(low_clock),
  .rst(reset),
  .piso_data_in(fifo_rd_data),
  .data_avail(~fifo_empty),
  .request_serial_data_type(trans_rcvr_request_piso_data_type),
  .request_serial_data(trans_rcvr_request_piso_data),
  .serial_data_avail(piso_serial_data_avail),
  .piso_data_out(piso_data_out),
  .piso_data_val(piso_data_val),
  .request_data(piso_request_data),
  .piso_data_last(piso_data_last)
);

fifo host_fifo [`DEV_RANGE] (
  .clk(low_clock),
  .rst(reset),
  .w_data(8'b0),
  .wr_en(1'b0),
  .flag_full(),
  .r_data(fifo_rd_data),
  .rd_en(piso_request_data),
  .flag_empty(fifo_empty)
);

endmodule
