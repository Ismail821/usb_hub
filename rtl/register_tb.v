`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 24.01.2024 17:57:23
// Design Name: 
// Module Name: register_tb
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

//`include "register.v"

module register_tb();

  reg clk;
  reg rst;
  reg [8:0] data_in1;
  reg [8:0] data_in2;

  wire data_out;


  register dut (
    .clk(clk),
    .rst(rst),
    .data_in1(data_in1),
    .data_in2(data_in2),
    .data_out(data_out)

  );

  initial begin
    
    $dumpfile("register_tb.vcd");
    $dumpvars(0, register_tb);
    clk = 0;
    rst = 1;
    data_in1 = 9'b0;
    data_in2 = 9'b0; #25

    rst = 0; #20

    repeat (25) begin
        data_in1 = $random; #60;
        data_in2 = $random; #80;
    end
    
    $finish;
    
  end

always #5 clk=~clk;
 /*
  always @(posedge clk) begin
    $display("Time = %t, Data Out = %b", $time, data_out);
  end
*/
endmodule

