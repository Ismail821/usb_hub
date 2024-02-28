`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 17.12.2023 16:38:24
// Design Name: 
// Module Name: fifo
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


module fifo #(parameter integer DEPTH=4, 
              parameter integer WIDTH=8) 

(
    input wire clk, rst,
    input wire [WIDTH-1:0] w_data,
    input wire rd_en, wr_en,
    output reg flag_full, flag_empty, 
    output reg [WIDTH-1:0] r_data,
    output reg [DEPTH-1:0] wr_count, rd_count

    
);

integer i,j,k;

reg [DEPTH-1:0] wr_ptr=0;

reg [DEPTH-1:0] rd_ptr=0;

reg [DEPTH-1:0]sum=0;

reg [WIDTH:0]storage[DEPTH-1:0];

//always@(*)begin
    
assign flag_full = &sum;
assign flag_empty = ~ (|sum);

//end

always@(posedge clk or posedge rst)begin

    if(rst)begin
        wr_ptr<=0;
        rd_ptr<=0;
        r_data<=0;
      	sum<=0;
        for(k=0;k<DEPTH;k=k+1)begin
            storage[k]<=0;
        end
        
    end
    else if(wr_en && ~flag_full)begin
        storage[wr_ptr]<= w_data;
        sum[wr_ptr]<=1; 
        wr_ptr<= (wr_ptr+1)%DEPTH;
        wr_count<= wr_count +1;
    end
    if(rd_en && ~flag_empty)begin
        r_data<= storage[rd_ptr];
        sum[rd_ptr]<=0;
        rd_ptr<= (rd_ptr+1)%DEPTH;
        rd_count<= rd_count+1;  
        
        
    end    

end
    
endmodule
