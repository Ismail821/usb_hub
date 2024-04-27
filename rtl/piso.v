`define PISO_DATA_RANGE = `WIDTH_TO_RANGE(PISO_DATA_WIDTH)
 
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
  output request_data,  //whenever data is available and reg1 is empty, it'll request for data. will be connected to read_enable in fifo
  output reg piso_data_last   //will indicate when the last bit of the stream is sent
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

reg [7:0] SYNC_PACKET = 8'b11000001; //send LSB out first. Assuming initial state will be J 
reg [7:0] ACK_PID = 8'b11010010; //PID for ACK is [3:0] = 0010
 
 //assign request_data = (reg1_empty && data_avail)&&~rst; 

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
    request_data<=0;
    receive<=0;
  end
  else begin 
    if(request_serial_data)begin
      case(request_serial_data_type)
        `REQUEST_SERIAL_DATA_TYPE_NULL:begin
          reg1<=reg1; //add required data
        end

        `REQUEST_SERIAL_DATA_TYPE_SYNC: begin
          reg1<=SYNC_PACKET;
          reg1_empty<=0;
        end

        `REQUEST_SERIAL_DATA_TYPE_PID: begin
          reg1<=reg1; //change and add PIDs
        end

        `REQUEST_SERIAL_DATA_TYPE_ACK: begin
          reg1<=ACK_PID;
          reg1_empty<=0;
        end

        default: begin
          reg1<=reg1;
        end
      endcase          
    end
  else begin
  request_data<= (reg1_empty && data_avail)&&~rst;
   
    if(piso_data_in!=reg1 && reg1_empty==1 && request_data)begin //checks if data is valid and if the register is empty
      receive<=1; //one clock cycle delay
      if(receive)begin
        reg1<=piso_data_in;
        reg1_empty<=0;
        if(tx2)begin
          send_data2<=1;
        end
        else begin
          send_data2<=0;
        end
      end            
    end 
    else begin
      reg1<=reg1;
      receive<=0;
    end
  end
  if(reg2_empty==1 && reg1_empty==0)begin // check is data is not being sent, and reg2 is empty and reg1 is not empty
    reg2<=reg1;   //load the data from reg1 to reg2
    reg2_empty<=0;
    reg1_empty<=1;
    send_data2<=1;
    tx2<=1;       
  end
  else if(reg3_empty==1 && reg1_empty==0)begin
    reg3<=reg1;
    reg3_empty<=0;
    reg1_empty<=1;
    send_data3<=1;
    tx3<=1;
  end
  
  //send data out serially
  if (send_data2 && !select)begin
    tx<=1;
    reg2<= {1'b0,reg2[DATA_LENGTH-1:1]}; //send the data from reg2 serially
    piso_data_out<= reg2[0]; //Sending LSB first
    count2<= count2+1;
    if(count2==DATA_LENGTH-1)begin
      piso_data_last<=1;
    end
    else begin
      piso_data_last<=0;
    end
  end
  else if (send_data3 && select)begin
    tx<=1;
    reg3<= {1'b0,reg3[DATA_LENGTH-1:1]}; //send the data from reg3 serially
    piso_data_out<= reg3[0]; //Sending LSB first
    count3<= count3+1;
    
    if(count3==DATA_LENGTH-1)begin
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
  if(count2==DATA_LENGTH)begin
    send_data2<=0;
    //tx<=0;
    tx2<=0;
    count2<=0;
    reg2_empty<=1;
    //select = 1;
    piso_data_last<=0;
  end
  if(count3==DATA_LENGTH)begin
    send_data3<=0;
    //tx<=0;
    //tx2<=0;
    count3<=0;
    reg3_empty<=1;
    //select = 0;
    piso_data_last<=0;
  end
  end
end
   
  
always @(*)begin
  if(rst)begin
    select=0;
  end
  else begin
    if(count2==DATA_LENGTH)begin
      select=1;
    end
    else if(count3==DATA_LENGTH)begin
      select=0;
    end
  end
end   
  
 
 
endmodule
