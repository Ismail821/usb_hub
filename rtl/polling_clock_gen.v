module polling_clock_gen #(
  parameter NUMBER_OF_OUTPUT_CLOCKS = 1,
  parameter TIME_PERIOD_PCLOCK = 100
)(
  input wire clock,
  input wire [NUMBER_OF_OUTPUT_CLOCKS-1:0] reset,
  output reg [NUMBER_OF_OUTPUT_CLOCKS-1:0] polling_clock
);
    
  reg [$clog2(TIME_PERIOD_PCLOCK)-1:0] counter;

  always @(posedge clock) begin
    if(&reset) begin
      counter = 0;
      polling_clock = 0;
    end else begin
      counter = counter + 1;
      if(counter == TIME_PERIOD_PCLOCK)begin
        counter = 0;
        if(|polling_clock) begin
          polling_clock = {polling_clock[NUMBER_OF_OUTPUT_CLOCKS-2:0], polling_clock[NUMBER_OF_OUTPUT_CLOCKS-1]};
        end else begin
          polling_clock = 1;
        end
      end
    end
  end

endmodule
