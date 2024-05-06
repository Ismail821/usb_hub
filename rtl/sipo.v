

module sipo #(parameter integer DATA_WIDTH=8)(
    
    input wire clk,
    input wire rst,
    input wire s_data_in,
    input wire s_data_in_val, 
    input wire sipo_cancel,
    
    output reg [DATA_WIDTH-1:0]p_data_out,
    output reg p_data_out_val

);

reg [$clog2(DATA_WIDTH):0]count1, count2;

reg [DATA_WIDTH-1:0] shift_reg1, shift_reg2;

reg select=0; //to select the register
reg tx;




always @(posedge clk)begin

    if(rst)begin
        p_data_out<=0;
        p_data_out_val<=0;
        shift_reg1<=0;
        shift_reg2<=0;
        count1<=0;
        count2<=0;
        tx<=0;
    end
    else if(sipo_cancel)begin
        p_data_out<=0;
        p_data_out_val<=0;
        shift_reg1<=0;
        shift_reg2<=0;
        count1<=0;
        count2<=0;
        tx<=0;
    end
    else if(s_data_in_val)begin
       
        tx<=1;
        if(!select)begin
            shift_reg1 <= {s_data_in,shift_reg1[DATA_WIDTH-1:1]};   
            count1<= count1 + 1;
        end
        else begin
            shift_reg2 <= {s_data_in,shift_reg2[DATA_WIDTH-1:1]};
            count2<= count2 + 1;
        end
        
    end
    else begin
	shift_reg1<=0;
	shift_reg2<=0;
	count1<=0;
	count2<=0;
	tx<=0;
    end

	if(count1==DATA_WIDTH || count2==DATA_WIDTH)begin
		p_data_out_val<=1;
		
		if(select)begin
			p_data_out<=shift_reg1;
			shift_reg1<=0;
			count1<=0;
		end
		else begin
			p_data_out<=shift_reg2;
			shift_reg2<=0;
			count2<=0;
		end
	//tx<=0;
			
	end
	else begin
		p_data_out_val<=0;
		p_data_out<=0;
	end

end


always@(*)begin

    if(rst)begin
        select=0;
    end
    if(count1==DATA_WIDTH)begin
        select=1;
    end
    else if(count2==DATA_WIDTH)begin
        select=0;
    end
    
end

endmodule

