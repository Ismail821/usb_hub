`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07.02.2024 21:40:31
// Design Name: 
// Module Name: transmitter
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

//better to use FSM

/*
LOW Speed:
J state:  D+ LOW | D- HIGH  | Differential 0 |
K state:  D+ HIGH  | D- LOW | Differential 1 | IDLE 

HIGH Speed:
J state:  D+ HIGH | D- LOW  | Differential 1 | IDLE
K state:  D+ LOW  | D- HIGH | Differential 0 | 


FOR THIS CODE: HIGH SPEED
*/
module transmitter(
	input wire clk,
	input wire rst,
	input wire serial_in,
	input wire in_data_valid,
	output reg d_plus,
	output reg d_minus,
	output reg out_data_valid	

);
//type DEF ENUM J state=00, K state=01

// typedef enum { J_STATE = 00, K_STATE = 01} usb_output_states;
//usb_output_states output_state ;


reg [1:0]state;
reg [1:0]IDLE=2'b00;

reg [1:0]J_state = 2'b01;
reg [1:0]K_state = 2'b10;

always @(posedge clk)begin

    if(rst)begin
        state<=IDLE;
        out_data_valid<=0;
        //d_plus<=1;
        //d_minus<=0;
    end
    else if(~in_data_valid)begin
        state<=IDLE;
        out_data_valid<=0;
        //d_plus<=1;
        //d_minus<=0;
    end
    else begin
        out_data_valid<=1;
        
        case(state)//add a {rst,data_in_valid, serial_in} | 
            IDLE: begin //instead of IDLE, rst-1xx, idle-00x, 011,010 - outputs, drive output_valid
                //d_plus<=1;
                ///d_minus<=0;
                if(serial_in)begin
                    state<=J_state;
                end
                else begin
                    state<=K_state;
                end
            end
            
            J_state: begin
                //d_plus<=1;
                //d_minus<=0;
                if(serial_in)begin
                    state<=J_state;
                end
                else begin
                    state<=K_state;
                end
                //state<=state if in=1 | state<=~state if in=0
            end
            
            K_state: begin
                //d_plus<=0;
                //d_minus<=1;
                if(serial_in)begin
                    state<= K_state;
                end
                else begin
                    state<=J_state;
                end
            
            end
       
        endcase 
    end

end

//
always @(*)begin 

    case(state)//we can have one more variable to define outputs! add one clk delay for the output state
        
        IDLE:begin //remove this and when rst happens switch to default J or K state depending on the speed
            d_plus=1;
            d_minus=0;
        end
        
        J_state:begin
            d_plus=1;
            d_minus=0; 
        end
        
        K_state: begin
            d_plus=0;
            d_minus=1;        
        end
                
    endcase

end


endmodule
