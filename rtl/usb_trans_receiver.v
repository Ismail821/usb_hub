
module usb_host_trans_receiver #(
  //parameters
  parameter DUMMY_PARAM = 0
) (
  //=================== I/O Signals =============================
  //-----------------Common Signals------------------------------
  input clock,
  input polling_clock,
  input reset,
  //-----------------State Signals------------------------------
  //connected from the Top module/Here based on the device speed
  input wire [1:0] IDLE_state,
  input wire [1:0] J_state,
  input wire [1:0] K_state,

  //Signals connected to the PISO, which will be driven into USB IF
  //request_serial_data goes high and data comes from the next cycles
  //The Data type tells if we need a polling read request or a ACK.
  input   serial_data_in,
  input   serial_data_in_val,
  input   serial_data_in_last,
  input   serial_data_in_avail,

  output  request_serial_data,
  output  reg [`REQUEST_SERIAL_DATA_TYPE_RANGE] request_serial_data_type,

  //Signals Connected to SIPO, Send data into SIPO to FIFO, when we get data 
  //send it along with val. if SIPO is still empty. Then we can send the Ack
  output  serial_data_out,
  output  serial_data_out_val,

  input   SIPO_empty,

  //The inout signals that will be driven. it's a concatination of d+ and d-
  inout   wire [1:0] usb_signals
);

//Module Out declarations
reg serial_data_out;
reg serial_data_out_val;
reg request_serial_data;

///Flags that'll be used for inter block communications
reg request_ongoing;
reg response_ongoing;
reg [USB_TR_STATE_WIDTH-1:0] output_usb_state;
reg output_usb_state_d1;

//Some flopped signals for Storing prev values
reg j_state;
reg k_state;
reg idle_state;
reg serial_data_out_val_d1;
reg serial_data_in_val_d1;
reg polling_clock_d1;

reg [1:0] usb_signals_reg;

parameter USB_TR_STATE_WIDTH  = 3;
parameter USB_TR_STATE_TOGGLE = 3'h0;
parameter USB_TR_STATE_IDLE   = 3'h1;
parameter USB_TR_STATE_Z      = 3'h2;
parameter USB_TR_STATE_RESET  = 3'h3;


//State Variables for the Request Thread and Response Thread.
always @(*) begin
  j_state     <= J_state;
  k_state     <= K_state;
  idle_state  <= IDLE_state;
end
always @(posedge clock) begin
  output_usb_state_d1 <= output_usb_state;
  polling_clock_d1    <= polling_clock;
end

//Request Data threat, sets the output_usb_state flag Receives the data from the serial input
//and sets the output_usb_state accordingly.
always @(posedge clock) begin
  if(reset) begin
    request_ongoing   <= 0;
    response_ongoing  <= 0;
    output_usb_state   = USB_TR_STATE_RESET;
    request_serial_data = 0;
    request_serial_data_type = `REQUEST_SERIAL_DATA_TYPE_NULL;
  end else begin
    if(polling_clock && ~polling_clock_d1) begin
      if(~response_ongoing && ~request_ongoing) begin
        request_ongoing           <= 1;
        request_serial_data       = 1;
        request_serial_data_type  = `REQUEST_SERIAL_DATA_TYPE_SYNC;
      end
    end
    if(request_ongoing) begin
      if(serial_data_in_val) begin
        output_usb_state = serial_data_in ? output_usb_state : USB_TR_STATE_TOGGLE;
      end else if(serial_data_in_val_d1) begin
        request_ongoing     <= 0;
        response_ongoing    <= 1;
        request_serial_data  = 0;
      end
`ifdef SIMULATION
    else begin
      `ERROR("Request is ongoing but Data isn't available")
    end
`endif
      if(serial_data_in_last) begin
        case(request_serial_data_type)
        `REQUEST_SERIAL_DATA_TYPE_SYNC: begin
          request_serial_data       = 1;
          request_serial_data_type  = serial_data_in_avail ? 
                          `REQUEST_SERIAL_DATA_TYPE_PASS_THROUGH : `REQUEST_SERIAL_DATA_TYPE_PID_READ;
        end
        `REQUEST_SERIAL_DATA_TYPE_PID_READ:  begin
          request_serial_data       = 1;
          request_serial_data_type  = `REQUEST_SERIAL_DATA_TYPE_READ_ADDRESS;
        end
        `REQUEST_SERIAL_DATA_TYPE_READ_ADDRESS: begin
          request_serial_data       = 0;
          response_ongoing          <= 1;
        end
        endcase
      end else begin
        request_serial_data         = 0;
        request_serial_data_type    = `REQUEST_SERIAL_DATA_TYPE_NULL;
      end
    end else if (response_ongoing) begin
      output_usb_state = USB_TR_STATE_Z;
    end else begin
      output_usb_state = USB_TR_STATE_IDLE;
    end
  end
end

always @(posedge clock) begin
  case (output_usb_state)
  USB_TR_STATE_IDLE: begin
    usb_signals_reg = idle_state;
    // assign usb_signals = usb_signals_reg;
  end
  USB_TR_STATE_TOGGLE: begin
    if(output_usb_state_d1 == USB_TR_STATE_IDLE) begin
      usb_signals_reg = k_state;
      // assign usb_signals = usb_signals_reg;
    end else begin
      usb_signals_reg = ~usb_signals;
      // assign usb_signals = usb_signals_reg;
    end
  end
  USB_TR_STATE_Z:begin
    // assign usb_signals = 2'bz;//sb_signals_reg;
    usb_signals_reg    = 2'bz;
  end
  default: begin
    usb_signals_reg = 2'bx;
  end
  endcase
end

endmodule