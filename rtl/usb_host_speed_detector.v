module usb_host_speed_detector
(
  input wire clock,
  input wire reset,
  input wire [1:0] usb_signals,
  output reg [1:0] j_state,
  output reg [1:0] k_state,
  output reg [1:0] idle_state
);

  always @(posedge reset)begin
    case(usb_signals)
      2'b10: begin
        j_state = 2'b00;
        k_state = 2'b00;
        idle_state = 2'b00;
      end
      2'b01: begin
        j_state = 2'b00;
        k_state = 2'b00;
        idle_state = 2'b00;
      end
      default:begin
      end
    endcase
  end 
endmodule
