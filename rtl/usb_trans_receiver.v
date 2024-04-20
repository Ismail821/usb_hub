//Just a dummy module to try out the New trans_receiver module

module usb_host_trans_receiver #(
  parameters
) (
  //=================== I/O Signals =============================
  //-----------------Common Signals------------------------------
  input clock,
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
  
endmodule