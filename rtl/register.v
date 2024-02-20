`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.01.2024 15:23:08
// Design Name: 
// Module Name: register
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


module register( //change the module name,
    input wire clk,
    input wire rst,
    input wire [8:0] data_in1,
    input wire [8:0] data_in2,
    output reg data_out

    
        );
    
 reg [9:0]reg1=10'b1000000000; //9th bit is flag-2 indicates if data is sent out(reg is empty), 8th bit is flag-1 indicates if the data is valid
 reg [9:0]reg2=10'b1000000000;
 
 reg select=0; //0-read from 1st reg, 1- read from 2nd reg
 reg [3:0] count=0;
 
 reg send_data=0; //flag to control data transmission
 
 reg [7:0] data; //temp reg to store the data to be sent out 
 

 
 always@(posedge clk) begin
 
    if(rst) begin
        reg1<=10'b1000000000;
        reg2<=10'b1000000000;
        count<=0;
        data<=0;
        data_out<=0;
    end
    else begin 
    
        if(data_in1[8]==1 && reg1[9]==1)begin //checks if data is valid and if the register is empty
            if(data_in1[7:0]!=reg1[7:0])begin
                reg1<=data_in1;
                reg1[9]<=0;
            end
        end 
        else begin
            reg1<=reg1;
        end
        if(data_in2[8]==1 && reg2[9]==1)begin
            if(data_in2[7:0]!=reg2[7:0])begin
                reg2<=data_in2;
                reg2[9]<=0;
            end
        end
        else begin
            reg2<=reg2;          
        end




        if(!select && !send_data && reg1[9]==0)begin//send data from 1st register
            data<=reg1[7:0];
            send_data<=1;       
        end
        else if(select && !send_data && reg2[9]==0) begin
            data<=reg2[7:0];
            send_data<=1;
        end
        
        //send data out serially
        if (send_data)begin
            data<= {1'b0,data[7:1]};
            data_out<= data[0]; //Sending LSB first //change interface names data out -> serial  out
            count<= count+1;
            if(count==8)begin
                send_data<=0;
                count<=0;
                if (!select)begin //change flags in reg1.//change select to current reg 
                    reg1[9]<=1;
                    reg1[8]<=0;
                end
                else begin //change flags in reg2
                    reg2[9]<=1;
                    reg2[8]<=0;                   
                end
            end
        end
        else begin
            data_out<=0;
        end

        
    end
 
 end
 
 
 always @(*)begin
 	if(!send_data)begin
		if(reg1[9]==0)begin //select reg for the output
	   		select<=0;
		end
		else if(reg2[9]==0)begin
	   		select<=1;
		end
		else begin
	   		select<=select;
		end

	end
 
end 
    
    
endmodule
