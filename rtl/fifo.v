`define FIFO_DATA_DEPTH_RANGE `WIDTH_TO_RANGE(FIFO_DATA_DEPTH)
`define FIFO_DATA_WIDTH_RANGE `WIDTH_TO_RANGE(FIFO_DATA_WIDTH)

module fifo #(
  parameter integer FIFO_DATA_DEPTH=16,
  parameter integer FIFO_DATA_WIDTH=8
)(
  input wire clk,
  input wire rst,
  input wire [`FIFO_DATA_WIDTH_RANGE] w_data,
  input wire wr_en,
  input wire rd_en,
  output     flag_full,
  output     flag_empty, 
  output reg [`FIFO_DATA_WIDTH_RANGE] r_data
);

  reg [$clog2(FIFO_DATA_DEPTH)-1:0] wr_ptr;
  reg [$clog2(FIFO_DATA_DEPTH)-1:0] rd_ptr;
  reg [`FIFO_DATA_DEPTH_RANGE]      sum;
  reg [`FIFO_DATA_WIDTH_RANGE] storage [`FIFO_DATA_DEPTH_RANGE];
`ifdef SIMULATION
  reg [31:0] wr_count;
  reg [31:0] rd_count;
`endif

  assign flag_full  = &sum; 
  assign flag_empty = ~ (|sum)&&(~rst); //and with reset

  always@(posedge clk or posedge rst)begin

    if(rst)begin
      wr_ptr     <= 0;
      rd_ptr     <= 0;
      r_data     <= 0;
      sum        <= 0;
      storage[0] <= 0;
    end
    else begin
      if(wr_en && ~flag_full)begin
        storage[wr_ptr] <= w_data;
        sum[wr_ptr]     <= 1; 
        wr_ptr          <= wr_ptr+1;
`ifdef SIMULATION
        wr_count        <= wr_count +1;
`endif
      end
      if(rd_en && ~flag_empty)begin
        r_data          <= storage[rd_ptr];
        sum[rd_ptr]     <= 0;
        rd_ptr          <= (rd_ptr+1);
`ifdef SIMULATION
        rd_count        <= rd_count+1;  
`endif
      end  
    end
  end
endmodule