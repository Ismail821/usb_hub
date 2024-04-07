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
  input wire [`DATA_RANGE] piso_data_in,
  input wire data_avail,
  //-----------------Output Signals------------------------------------
  output reg piso_data_out,
  output piso_data_val,
  output request_data
  );
  
reg [PISO_DATA_WIDTH-1:0]reg1=0;
reg [PISO_DATA_WIDTH-1:0]reg2=0;

reg reg1_empty; //new addition: indicates if the register is empty or not
reg reg2_empty;

reg [PISO_DATA_WIDTH-1:0] count;

reg send_data; //flag to control data transmission

reg tx,tx2;

assign request_data = (reg1_empty && data_avail)&&~rst; 

assign piso_data_val = tx;

always@(posedge clk) begin
  if(rst) begin
    reg1<=0;
    reg2<=0;
    count<=0;
    reg1_empty<=1;
    reg2_empty<=1;
    piso_data_out<=0;
    send_data<=0;
    tx<=0;
    tx2<=0;
  end else begin 
    if(piso_data_in!=reg1 && reg1_empty==1 && request_data)begin //checks if data is valid and if the register is empty
      reg1<=piso_data_in;
      reg1_empty<=0;
      if(tx2)begin
        send_data<=1;
      end else begin
        send_data<=0;
      end
    end 
    else begin
      reg1<=reg1;
    end
    if(!send_data && reg2_empty==1 && reg1_empty==0)begin // check is data is not being sent, and reg2 is empty and reg1 is not empty
      reg2<=reg1;   //load the data from reg1 to reg2
      reg2_empty<=0;
      reg1_empty<=1;
      send_data<=1;
      tx2<=1;       
    end
    
    //send data out serially
    if (send_data)begin
      tx<=1;
      reg2<= {1'b0,reg2[PISO_DATA_WIDTH-1:1]}; //send the data from reg2 serially
      piso_data_out<= reg2[0]; //Sending LSB first
      count<= count+1;
      if(count==PISO_DATA_WIDTH)begin
        send_data<=0;
        tx<=0;
        tx2<=0;
        count<=0;
        reg2_empty<=1;
      end
    end
    else begin
      piso_data_out<=0;
    end
  end
end
 
endmodule
