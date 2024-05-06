//
//sequence detector for nak
//


module sequence_detector(
		input wire clk,
		input wire rst,
		input wire serial_data_in,
		input wire serial_data_in_valid,

		output reg sequence_detected

    );

reg [2:0]state;

reg [7:0] seq = 8'b01011010; //PID for NAK

reg deb;

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
		deb<=0;
	end
  else if(serial_data_in_valid) begin
  	deb<=1;
    case(state)

    	IDLE:begin
		sequence_detected<=0;
    		if(serial_data_in==seq[0])begin
    			state<=A;
    		end
    		else begin
    			state<=IDLE;

    		end
    	end

    	A: begin
    		if(serial_data_in==seq[1])begin
    			state<=B;
    		end
    		else if(serial_data_in==seq[0]) begin
    			state<=A;
    		end
    		else begin
    			state<=IDLE;
    		end
    	end

    	B: begin
    		if(serial_data_in==seq[2])begin
    			state<=C;
    		end
    		else if(serial_data_in==seq[0]) begin
    			state<=A;
    		end
    		else begin
    			state<=IDLE;
    		end
    	end

    	C: begin
    		if(serial_data_in==seq[3])begin
    			state<=D;
    		end
    		else if(serial_data_in==seq[0]) begin
    			state<=A;
    		end
    		else begin
    			state<=IDLE;
    		end
    	end

     	D: begin
    		if(serial_data_in==seq[4])begin
			state<=E;
		end
		else if(serial_data_in==seq[0]) begin
			state<=A;
		end
		else begin
	 		state<=IDLE;
		end
    	end

    	E: begin
    		if(serial_data_in==seq[5])begin
			state<=F;
		end
		else if(serial_data_in==seq[0]) begin
			state<=A;
		end
		else begin
			state<=IDLE;
		end
    	end

    	F: begin
    		if(serial_data_in==seq[6])begin
			state<=G;
		end
		else if(serial_data_in==seq[0]) begin
			state<=A;
		end
		else begin
			state<=IDLE;
		end
    	end

    	G: begin
    		if(serial_data_in==seq[7])begin
			state<=IDLE;
			sequence_detected<=1;
		end
		else if(serial_data_in==seq[0]) begin
			state<=A;
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
  else begin
  	sequence_detected<=0;
  	state<=IDLE;
  end

end

endmodule

