/*
LOW Speed:
J state:  D+ LOW | D- HIGH  | Differential 0 |
K state:  D+ HIGH  | D- LOW | Differential 1 | IDLE 

HIGH Speed:
J state:  D+ HIGH | D- LOW  | Differential 1 | IDLE
K state:  D+ LOW  | D- HIGH | Differential 0 | 

FOR THIS CODE: HIGH SPEED
*/

module transmitter #(
  //======================Parameters===================================
  J_STATE = 01,
  K_STATE = 10,
  IDLE_STATE = 00,
  //ISMAIL_TODO: Later Move these as some input register as, the Speed and state is a
  //run-time configuration, rather than static
  )(
  input wire clk,
  input wire rst,
  input wire s_data_in,//serial_in,
  input wire s_data_val,//in_data_valid,
  
  output reg d_plus,
  output reg d_minus,
  output reg out_data_valid  
  //output reg s_data_req, ?

);
//type DEF ENUM J state=00, K state=01

// typedef enum { J_STATE = 00, K_STATE = 01} usb_output_states;
//usb_output_states output_state ;


reg [2:0]state,out_state;
reg [2:0]IDLE=3'b000;

reg [2:0]J_state = 3'b001;
reg [2:0]K_state = 3'b010;
reg [2:0]EOP = 3'b011;
reg [2:0]SE0 = 3'b100;

reg [15:0]counter=0;

reg tx=0; // 1-tx is going on, 0-tx is complete/can start again
//00-tx can start again, 01-tx is going on, 10-just completed, 11-EOP completed,

always @(posedge clk)begin

  if(rst)begin
    state<=IDLE;
    out_data_valid<=0;
    out_state<=IDLE;
  end
  if(s_data_val==0)begin
    state<=IDLE;
  end
  //else begin
    //out_data_valid<=1;
    
    case(state)//add a {rst,data_in_valid, serial_in} | 
      IDLE: begin //instead of IDLE, rst-1xx, idle-00x, 011,010 - outputs, drive output_valid
      
        if(~s_data_val)begin //for SOP and EOP use this.
          if(tx==1)begin
            state<=EOP;
          end
          else begin
            state<=IDLE;
            out_state<=IDLE;
            out_data_valid<=0;
          end
        end
        else begin
          out_data_valid<=1;
          tx<=1;
          if(s_data_in)begin
            state<=J_state;
            out_state<=J_state;
          end
          else begin
            state<=K_state;
            out_state<=K_state;
          end
        end
      end
      
      J_state: begin

        if(s_data_in)begin
          state<=J_state;
          out_state<=J_state;
        end
        else begin
          state<=K_state;
          out_state<=K_state;
        end
        //state<=state if in=1 | state<=~state if in=0
        
        if(~s_data_val)begin
          state<=EOP;
        end
        
      end
      
      K_state: begin

        if(s_data_in)begin
          state<= K_state;
          out_state<=K_state;
        end
        else begin
          state<=J_state;
          out_state<=J_state;
        end
        
        if(~s_data_val)begin
          state<=EOP;
        end      
        
      end
      
      EOP: begin
        
        out_state<=SE0;
        counter<= counter +1;
        state<=EOP;
        if(counter==2)begin
          out_state<=J_state;
          state<=IDLE;
          counter<=0;
          tx<=0;
        end
        
        
      end
      
      
     
    endcase 
  //end

end

//
always @(posedge clk)begin 

  case(out_state)
    
    IDLE:begin 
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
        
    SE0: begin
      d_plus=0;
      d_minus=0;
    end
    
        
     
  endcase

end


endmodule
//Praneet TO FIX:
//first always block, case statement not guarded against Reset.
//Regs, J_state ... SE0. Why are they declared as 3 bits?. What does MSB signify?
//counter doesn't need to be a 16 bit variable?, Only see go upto 2 max
//Rename tx to some other meaningful name. Or maybe make use of output_state??
//State variable is update for s_data_val = 0 case at state <= EOP &  state <= IDLE, Might cause multiple driver issues.
//This whole block, **might** need re-architecturing,as need to implement receiver also within this interface module
