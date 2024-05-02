module usb_host_speed_detector#(
  parameter RESET_TIMER = 20
)(
  input wire clock,
  input wire [1:0] usb_signals,

  output reg       reset,
  output reg [1:0] j_state,
  output reg [1:0] k_state,
  output reg [1:0] idle_state
);

  reg [$clog2(RESET_TIMER)-1:0] reset_counter;

  always @(posedge clock) begin
    if(usb_signals == 2'b0) begin
      if(reset_counter == RESET_TIMER) begin
        reset_counter = RESET_TIMER;
      end else begin
        reset_counter = reset_counter + 1;
      end
    end else begin
      reset_counter = 0;
    end
    if(reset_counter == RESET_TIMER) begin
      reset = 1;
    end else begin
      reset = 0;
    end
  end

  always @(negedge reset)begin
    case(usb_signals)
      2'b10: begin
        j_state     = 2'b10;
        k_state     = 2'b01;
        idle_state  = j_state;
      end
      2'b01: begin
        j_state     = 2'b01;
        k_state     = 2'b10;
        idle_state  = j_state;
      end
    endcase
  end 

endmodule
