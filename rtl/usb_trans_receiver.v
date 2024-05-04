
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
  
  output  driving_req,
  //The inout signals that will be driven. it's a concatination of d+ and d-
  inout   wire [1:0] usb_signals
);

  //Module Out declarations
  reg serial_data_out;
  reg serial_data_out_val;
  reg request_serial_data;
  
  ///Flags that'll be used for inter block communications
  reg request_ongoing;
  reg request_ongoing_d1;
  reg response_ongoing;
  reg response_ongoing_d1;
  reg reset_d1;
  reg [`USB_TR_STATE_RANGE] output_usb_state;
  reg [`USB_TR_STATE_RANGE] output_usb_state_d1 = 0;
  reg [`USB_TR_STATE_RANGE] reset_done;
  reg driving_req;
  
  //Some flopped signals for Storing prev values
  reg [1:0] j_state;
  reg [1:0] k_state;
  reg [1:0] idle_state;
  reg serial_data_out_val_d1;
  reg serial_data_in_val_d1;
  reg polling_clock_d1;
  
  reg [1:0] usb_signals_reg;
  
  parameter USB_TR_STATE_NULL     = `USB_TR_STATE_WIDTH'h0;
  parameter USB_TR_STATE_TOGGLE   = `USB_TR_STATE_WIDTH'h1;
  parameter USB_TR_STATE_IDLE     = `USB_TR_STATE_WIDTH'h2;
  parameter USB_TR_STATE_Z        = `USB_TR_STATE_WIDTH'h3;
  parameter USB_TR_STATE_RESET    = `USB_TR_STATE_WIDTH'h4;
  parameter USB_TR_STATE_NOTOGGLE = `USB_TR_STATE_WIDTH'h5;
  
  assign driving_req = request_ongoing | request_ongoing_d1; 
  assign usb_signals = driving_req ? usb_signals_reg : 2'bz;
  
  //State Variables for the Request Thread and Response Thread.
  always @(*) begin
    j_state     <= J_state;
    k_state     <= K_state;
    idle_state  <= IDLE_state;
  end
  always @(posedge clock) begin
    polling_clock_d1      <= polling_clock;
    serial_data_in_val_d1 <= serial_data_in_val;
    request_ongoing_d1    <= request_ongoing;
    response_ongoing_d1   <= response_ongoing;
    reset_d1              <= reset;
  end
  
  always @(reset) begin
    if((reset_d1 == 1) & (reset == 0)) begin
      reset_done            =  {`USB_TR_STATE_WIDTH{1'b1}};
    end
  end
  
  //Request Data threat, sets the output_usb_state flag Receives the data from the serial input
  //and sets the output_usb_state accordingly.
  always @(posedge clock) begin
    if(reset) begin
      request_ongoing           = 0;
      response_ongoing          = 0;
      output_usb_state          = USB_TR_STATE_RESET;
      request_serial_data       = 0;
      request_serial_data_type  = `REQUEST_SERIAL_DATA_TYPE_NULL;
    end else begin
      if(polling_clock && ~polling_clock_d1) begin
        if(~response_ongoing && ~request_ongoing) begin
          request_serial_data       = 1;
          request_serial_data_type  = `REQUEST_SERIAL_DATA_TYPE_SYNC;
          request_ongoing           = 1;
        end
      end
      if(request_ongoing_d1) begin
        if(serial_data_in_val) begin
          output_usb_state   = serial_data_in ? USB_TR_STATE_NOTOGGLE : USB_TR_STATE_TOGGLE;
        end else begin
          output_usb_state   = USB_TR_STATE_IDLE;
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
            request_ongoing      = 0;
            response_ongoing     = 1;
            request_serial_data  = 0;
          end
          endcase
        end else begin
          request_serial_data         = 0;
          // request_serial_data_type    = `REQUEST_SERIAL_DATA_TYPE_NULL;
        end
      end else if (response_ongoing_d1) begin
        output_usb_state = USB_TR_STATE_Z;
      end else begin
        output_usb_state = USB_TR_STATE_IDLE;
      end
    end
    output_usb_state_d1   <= output_usb_state;
  end
  
  always @(posedge clock) begin
    // if(reset_done) begin
      case (output_usb_state_d1 & reset_done)
      USB_TR_STATE_IDLE: begin
         if(serial_data_in_val && ~serial_data_in_val_d1) begin
           usb_signals_reg <= k_state;
         end else begin
          usb_signals_reg <= idle_state;
         end
      end
      USB_TR_STATE_TOGGLE: begin
        if(usb_signals_reg == j_state) begin
          usb_signals_reg  <= k_state;
        end else if(usb_signals_reg == k_state) begin
          usb_signals_reg  <= j_state;
        end else begin
          usb_signals_reg  <= idle_state;
        end
      end
      USB_TR_STATE_NOTOGGLE: begin
      end
      USB_TR_STATE_Z:begin
        usb_signals_reg    <= 2'bz;
      end
      default: begin
        usb_signals_reg    <= 2'bz;
      end
      endcase
    // end
  end

endmodule