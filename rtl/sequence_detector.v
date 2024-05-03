//sequence detector for nak
module sequence_detector(
		input wire clk,
		input wire rst,
		input wire serial_data_in,
		
		output reg sequence_detected

    );
    
reg [2:0]state;    
reg [7:0] seq = 8'b01011010; //PID for NAK    

parameter IDLE = 3'b000;
parameter A = 3'b001;
parameter B = 3'b010;
parameter C = 3'b011;
parameter D = 3'b100;
parameter E = 3'b101;
parameter F = 3'b110;
parameter G = 3'b111;


always@(posedge clk)begin 

	if(rst)begin
		state<=IDLE;
		sequence_detected<=0;
	end
  else begin
    case(state)
    	
    	IDLE:begin
		sequence_detected<=0;    	
    		if(serial_data_in==0)begin
    			state<=A;
    		end
    		else begin
    			state<=IDLE;
    			
    		end
    	end
    	
    	A: begin
    		if(serial_data_in==1)begin
    			state<=B;
    		end
    		else begin
    			state<=A;
    		end
    	end

    	B: begin
    		if(serial_data_in==0)begin
    			state<=C;
    		end
    		else begin
    			state<=IDLE;
    		end
    	end
    	
    	C: begin
    		if(serial_data_in==1)begin
    			state<=D;
    		end
    		else begin
    			state<=A;
    		end
    	end
    	
     	D: begin
    		if(serial_data_in==1)begin
    			state<=E;
    		end
    		else begin
    			state<=A;
    		end
    	end
    	
    	E: begin
    		if(serial_data_in==0)begin
    			state<=F;
    		end
    		else begin
    			state<=IDLE;
    		end
    	end
    	
    	F: begin
    		if(serial_data_in==1)begin
    			state<=G;
    		end
    		else begin
    			state<=A;
    		end
    	end    	    
    	
    	G: begin
    		if(serial_data_in==0)begin
    			state<=IDLE;
    			sequence_detected<=1;
    		end
    		else begin
    			state<=IDLE;
    		end
    	end    		   	    	    	
    	
    	default:begin
    		state<=IDLE;
    		sequence_detected<=0;
    	end
    	
    	
    endcase
    
  end  
end    
    
endmodule

