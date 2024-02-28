`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07.02.2024 21:42:16
// Design Name: 
// Module Name: transmitter_tb
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

//`include "transmitter.v"

module transmitter_tb();

reg clk;
reg rst;
reg serial_in;
reg in_data_valid;

wire d_plus;
wire d_minus;
wire out_data_valid;

transmitter DUT(
 	.clk(clk),
 	.rst(rst),
    .serial_in(serial_in),
    .in_data_valid(in_data_valid),
    .d_plus(d_plus),
    .d_minus(d_minus),
    .out_data_valid(out_data_valid)
);

initial begin

$dumpfile("transmitter_tb.vcd");
$dumpvars(0,transmitter_tb);

clk=0;
rst=1;
in_data_valid=0;
serial_in=1'bz; #55;

rst=0;#50;

//for loop, one reg with 10 bits, randomize this reg and then put a for loop 0->10, serial in as bits of the reg


in_data_valid=1; #200
in_data_valid=0; #150
in_data_valid=1; #100

in_data_valid=0;#50;

$finish;
end

always #5 clk=~clk;

always @(posedge clk) begin
	if(in_data_valid)begin
		serial_in = $random;
	end
	else begin
	   serial_in = 1'bz;
	end
end

endmodule

