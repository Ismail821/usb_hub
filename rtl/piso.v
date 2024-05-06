`define PISO_DATA_RANGE `WIDTH_TO_RANGE(PISO_DATA_WIDTH)
 
module piso #(
  //======================Parameters===================================
  parameter PISO_DATA_WIDTH = 8
  )(
  //======================I/O Signals==================================
  //-----------------Common Signals----------------------------------
  input wire clk,
  input wire rst,
  //-----------------Input Signals-------------------------------------
  input wire [`PISO_DATA_RANGE] piso_data_in,
  input wire data_avail,
  input wire [`REQUEST_SERIAL_DATA_TYPE_RANGE] request_serial_data_type, //inputs from trans_receiver
  input wire request_serial_data,
  
  //-----------------Output Signals------------------------------------
  output reg piso_data_out,
  output piso_data_val,
  output reg request_data,  //whenever data is available and reg1 is empty, it'll request for data. will be connected to read_enable in fifo
  output reg piso_data_last,   //will indicate when the last bit of the stream is sent
  output reg serial_data_available
  );
  
reg [`PISO_DATA_RANGE] reg1=0;
reg [`PISO_DATA_RANGE] reg2=0;
reg [`PISO_DATA_RANGE] reg3=0;

reg reg1_empty; //new addition: indicates if the register is empty or not
reg reg2_empty;
reg reg3_empty;

reg [`PISO_DATA_RANGE] count2;
reg [`PISO_DATA_RANGE] count3;

reg send_data2; //flag to control data transmission
reg send_data3; //flag to control data transmission

reg tx;
reg tx2;
reg tx3;

reg receive;

reg select=0; //to select reg2 or reg3 to send the data out

 
 reg [7:0] SYNC_PACKET = 8'b10000001; //send LSB out first. Assuming initial state will be J 
 reg [7:0] ACK_PID = 8'b11010010; //PID for ACK is [3:0] = 0010
 reg [7:0] NAK_PID = 8'b01011010; //PID for NAK is [3:0] = 1010
 reg [7:0] READ_PID = 8'b01101001; //PID for IN token is [3:0] = 1001
 
 
 //delayed signals
 // control signals for serial request data
 reg sync, ack, nak, address, read;
 reg fifo_data;
 
 //counters for sync,ack,nak
 reg [4:0]serial_counter;
 


assign piso_data_val = tx;



always@(posedge clk) begin
   
  if(rst) begin
    reg1<=0;
    reg2<=0;
    reg3<=0;
    count2<=0;
    count3<=0;
    reg1_empty<=1;
    reg2_empty<=1;
    reg3_empty<=1;
    piso_data_out<=0;
    piso_data_last<=0;
    send_data2<=0;
    send_data3<=0;
    tx<=0;
    tx2<=0;
    tx3<=0;
    request_data<=0;
    receive<=0;
        
    sync<=0;
    ack<=0;
    nak<=0;
    read<=0;
    address<=0;
    fifo_data<=0;
    serial_counter<=0;
		serial_data_available <= 0;
  end
  else begin 
        if(request_serial_data && (reg2_empty || reg3_empty))begin //and either reg2 or 3 should be empty
            case(request_serial_data_type)

							`REQUEST_SERIAL_DATA_TYPE_SYNC: begin
									if(!sync)begin
										serial_counter<=0;
										sync<=1;
										if(reg2_empty==1)begin
											reg2<=SYNC_PACKET;
											send_data2<=1;
											reg2_empty<=0;
										end
										else if(reg3_empty==1)begin
											reg3<=SYNC_PACKET;
											reg3_empty<=0;
											send_data3<=1;
										end
									end
									else begin
										serial_counter<= serial_counter +1;
									end
									
									if(serial_counter==7)begin
										sync<=0;
										serial_counter<=0;
									end

							end
					
							`REQUEST_SERIAL_DATA_TYPE_PID_READ: begin //IN token
									if(!read)begin
										serial_counter<=0;
										read<=1;
										if(reg2_empty==1)begin
											reg2<=READ_PID;
											send_data2<=1;
											reg2_empty<=0;
										end
										else if(reg3_empty==1)begin
											reg3<=READ_PID;
											reg3_empty<=0;
											send_data3<=1;
										end
									end
									else begin
										serial_counter<= serial_counter +1;
									end
									
									if(serial_counter==7)begin
										read<=0;
										serial_counter<=0;
									end									
							end
							
							`REQUEST_SERIAL_DATA_TYPE_READ_ADDRESS:begin
									if(!address)begin
										serial_counter<=0;
										address<=1;
										if(reg2_empty==1 && reg3_empty==1)begin
											reg2<=0;
											reg3<=0;
											reg2_empty<=0;
											reg3_empty<=0;
											send_data2<=1;
											send_data3<=1;
										end
									end
									else begin
										serial_counter<=serial_counter +1;
									end
									
									if(serial_counter==15)begin
										address<=0;
									end
									//reg1<=reg1; //16 bit field, hardode to 00
							end
							
							`REQUEST_SERIAL_DATA_TYPE_PASS_THROUGH: begin //send data from fifo
									fifo_data=1;
									//request_data<= (reg1_empty && data_avail && ~request_data)&&~rst;//remove from here and add it below. only send when requested
							end
							
							//if reg1 is not empty, reg2<= reg1, else exit
							`REQUEST_SERIAL_DATA_TYPE_PID_ACK: begin
									if(!ack)begin
										serial_counter<=0;
										ack<=1;	
										if(reg2_empty==1)begin
											reg2<=ACK_PID;
											reg2_empty<=0;
											send_data2<=1;
										end
										else if(reg3_empty==1)begin
											reg3<=ACK_PID;
											reg3_empty<=0;
											send_data3<=1;
										end
									end
									else begin
										serial_counter<= serial_counter +1;
									end
									
									if(serial_counter==7)begin
										ack<=0;
									end
		
							end
							
							`REQUEST_SERIAL_DATA_TYPE_PID_NAK: begin
									if(!nak)begin
										nak<=1;
										serial_counter<=0;
										if(reg2_empty==1)begin
											reg2<=NAK_PID;
											reg2_empty<=0;
											send_data2<=1;
										end
										else if(reg3_empty==1)begin
											reg3<=NAK_PID;
											reg3_empty<=0;
											send_data3<=1;
										end
									end
									else begin
										serial_counter<= serial_counter +1;
									end
									
									if(serial_counter==7)begin
										nak<=0;
									end
									
	
							end
							
							default: begin
									reg1<=reg1;
									request_data<=0;
									serial_counter<=0;
									sync<=0;
									ack<=0;
									nak<=0;
							end
						 
            endcase
            
                     
        end
        else begin //else for if serial request
          //request_data<=0;
          sync<=0;
          ack<=0;
          nak<=0;
          fifo_data<=0;
          
        end

        serial_data_available<=~reg1_empty;
        
        request_data<= (reg1_empty && data_avail && ~request_data)&&~rst;
        //request_data<= (reg1_empty && data_avail && ~request_data)&&~rst; //reg1_empty_d1 && data_avail && ~rst;
  				//piso_data_in remove
          if(piso_data_in!=reg1 && reg1_empty==1 && request_data)begin //checks if data is valid and if the register is empty
              reg1<=piso_data_in;
              reg1_empty<=0;
          end 
          else begin
              reg1<=reg1;
              receive=0;
              //exit simulation , error message data has been requested but no reg is empty
          end
				
				if(fifo_data)begin
						if(reg2_empty==1 && reg1_empty==0)begin // check is data is not being sent, and reg2 is empty and reg1 is not empty
								reg2<=reg1;   //load the data from reg1 to reg2
								reg2_empty<=0;
								reg1_empty<=1;
								send_data2<=1;       
						end
						else if(reg3_empty==1 && reg1_empty==0)begin
								reg3<=reg1;
								reg3_empty<=0;
								reg1_empty<=1;
								send_data3<=1;
						end
        end
        
        //send data out serially
        if (send_data2 && !select)begin
            tx<=1;
            tx2<=1;
            reg2<= {1'b0,reg2[PISO_DATA_WIDTH-1:1]}; //send the data from reg2 serially
            piso_data_out<= reg2[0]; //Sending LSB first
            count2<= count2+1;
            
            if(count2==PISO_DATA_WIDTH-1)begin
                piso_data_last<=1;
            end
            else begin
                piso_data_last<=0;
            end
            

        end
        else if (send_data3 && select)begin
            tx<=1;
            reg3<= {1'b0,reg3[PISO_DATA_WIDTH-1:1]}; //send the data from reg3 serially
            piso_data_out<= reg3[0]; //Sending LSB first
            count3<= count3+1;
            
            if(count3==PISO_DATA_WIDTH-1)begin
                piso_data_last<=1;
            end
            else begin
                piso_data_last<=0;
            end
            
        end
        else begin
            piso_data_out<=0;
            tx<=0;
        end
    
        if(count2==PISO_DATA_WIDTH)begin
            send_data2<=0;
            //tx<=0;
            tx2<=0;
            count2<=0;
            reg2_empty<=1;
            //select = 1;
            piso_data_last<=0;
        
        end
                        
        if(count3==PISO_DATA_WIDTH)begin
            send_data3<=0;
            //tx<=0;
            tx3<=0;
            count3<=0;
            reg3_empty<=1;
            //select = 0;
            piso_data_last<=0;
        end
    
    end //closing else block
      
 
 end
   

    
 always @(*)begin
    if(rst)begin
        select=0;
    end
    else begin
        if(count2==PISO_DATA_WIDTH)begin
            select=1;
        end
        else if(count3==PISO_DATA_WIDTH)begin
            select=0;
        end
        else if(reg2_empty==0 && reg3_empty==1)begin
        		select=0;
        end
        else if(reg2_empty==1 && reg3_empty==0)begin
        		select=1;
        end
    end
 end   
   
    
    
 endmodule
