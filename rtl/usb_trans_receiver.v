//Just a dummy module to try out the New trans_receiver module

module usb_host_trans_receiver #(
  parameters
) (
  //=================== I/O Signals =============================
  //-----------------Common Signals------------------------------
  input clock,
  input polling_clock,
  input reset,
  //-----------------State Signals------------------------------
  //connected from the Top module/Here based on the device speed
  input IDLE_state,
  input J_state,
  input K_state,

  //Signals connected to the PISO, which will be driven into USB IF
  //request_serial_data goes high and data comes from the next cycles
  //The Data type tells if we need a polling read request or a ACK.
  input   serial_data_in,
  input   serial_data_in_val,
  input   serial_data_in_type,

  output  request_serial_data,
  output  request_serial_data_type,

  //Signals Connected to SIPO, Send data into SIPO to FIFO, when we get data 
  //send it along with val. if SIPO is still empty. Then we can send the Ack
  output  serial_data_out,
  output  serial_data_out_val,

  input   SIPO_empty,

  //The inout signals that will be driven. it's a concatination of d+ and d-
  inout   usb_signals
);

//Module Out declarations
reg serial_data_out;
reg serial_data_out_val;
reg request_serial_data;
reg request_serial_data_type;

///Flags that'll be used for inter block communications
reg request_ongoing;      //might not be necessary
reg response_ongoing;
reg output_usb_state;

//Some flopped signals for Storing prev values
reg j_state;
reg k_state;
reg serial_data_out_val_d1;

//State Variables for the Request Thread and Response Thread.

always (@posedge clock) begin
  j_state     <= J_state;
  k_state     <= K_state;
  idle_state  <= IDLE_state;
  output_usb_state_d1 <= output_usb_state;
end

//Request Data threat, sets the output_usb_state flag Receives the data from the serial input
//and sets the output_usb_state accordingly.
always (@posedge clock) begin
  if(polling_clock) begin
    if(!response_ongoing && !request_ongoing) begin
      request_ongoing <= 1;
      request_serial_data       = 1;
      request_serial_data_type  = `REQUEST_SERIAL_DATA_READ;
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
  end else if (response_ongoing) begin
    output_usb_state = USB_TR_STATE_Z;
  end else begin
    output_usb_state = USB_TR_STATE_IDLE;
  end
end

always @(posedge clock) begin
  case (output_usb_state)
  USB_TR_STATE_IDLE: begin
    usb_signals = idle_state;
  end
  USB_TR_STATE_TOGGLE: begin
    if(output_usb_state_d1 == USB_TR_STATE_IDLE) begin
      usb_signals = k_state;
    end else begin
      usb_signals = ~usb_signals;
    end
  end
  USB_TR_STATE_Z:begin
    usb_signals = 2'bz;
  end
  default: begin
    usb_signals = 2'bx;
  end
  endcase
end

endmodule