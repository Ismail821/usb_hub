`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 17.12.2023 16:40:21
// Design Name: 
// Module Name: fifo_tb
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments
// 
//////////////////////////////////////////////////////////////////////////////////

//`include "fifo.v"

module fifo_tb #(parameter integer DEPTH = 4, 
                 parameter integer WIDTH = 8
                );

bit clk;
bit rst;

//Dut signals
bit rd_en;
bit wr_en;
bit flag_full;
bit flag_empty;

bit [WIDTH-1:0] r_data;
bit [WIDTH-1:0] w_data;
bit [DEPTH-1:0] wr_count;
bit [DEPTH-1:0] rd_count;

//Common Variable Cycle Count
bit[31:0] cycle;
int i;

//Scoreboard Q common between monitor & scoreboard
bit rd_en_prev;
bit data_rcvd;
int scoreboard_w_data[$];
int scoreboard_r_data[$];

//Sequence variables common between sequence and driver
bit [WIDTH-1:0] seqs_w_data;
bit seqs_rd_en;
bit seqs_wr_en;



fifo DUT(	.clk(clk),
			    .rst(rst),
			    .w_data(w_data),
			    .wr_en(wr_en),
			    .rd_en(rd_en),
			    .flag_full(flag_full),
			    .flag_empty(flag_empty),
			    .r_data(r_data),
			    .wr_count(wr_count),
			    .rd_count(rd_count)
        );


initial begin 
  $dumpfile("fifo_tb.vcd");
  $dumpvars(0,fifo_tb);
  rst = 1; #20
  rst = 0;

  fork
    begin $display("{%d} [Env] Starting my_sequence()", cycle);
      my_sequence();
    end begin $display("{%d} [Env] Starting driver()", cycle);
      driver();
    end begin $display("{%d} [Env] Starting monitor()", cycle);
      monitor();
    end begin $display("{%d} [Env] Starting Scoreboard", cycle);
      scoreboard();
    end
  join_none

  #250
 // disable fork;
  $display("{%d} Time Over: Finishing Simulation", cycle);
  $finish;
end

always #5 clk = ~clk;

always @(posedge clk) begin
   cycle = cycle + 1;
end

task automatic my_sequence (bit dummy = 1);
  forever begin
    @(posedge clk);
    seqs_w_data  <= $urandom();
    seqs_wr_en   <= $urandom();
    seqs_rd_en   <= $urandom();
  end 
endtask
assign rd_en= seqs_rd_en && ~flag_empty;
assign wr_en = seqs_wr_en && ~flag_full;
task automatic driver (bit dummy = 1);
    
  forever begin
     @(posedge clk);
        if (wr_en)begin
            w_data = seqs_w_data;
           $display("{%d} [DRIVER] Driven Data from driver :%h", cycle, w_data);
        end
     end
endtask 

  int monitor_r_data;
  int monitor_w_data;


task automatic monitor (bit dummy = 1);


  fork
  begin
    forever begin
      @(posedge clk);
      if(wr_en) begin
        monitor_w_data = w_data;
        $display("{%d} [MONITOR] Write Data received from monitor is: %0h", cycle, monitor_w_data);
        scoreboard_w_data.push_back(monitor_w_data);
      end
    end 
  end
  begin
    forever begin
      @(posedge clk);
      rd_en_prev<=rd_en;
      if(rd_en_prev)begin
        monitor_r_data = r_data;
        if (r_data === 'bx) begin
          $display("{%d} [MONITOR] Data received is X: %h", cycle, r_data);
          $finish;
        end
        $display("{%d} [MONITOR] Read Data received from monitor is: %0h", cycle, monitor_r_data);
        scoreboard_r_data.push_back(monitor_r_data);
        data_rcvd = 1;
      end
    end
  end
  join
endtask 


task scoreboard (bit dummy = 1);

  int expected_data;
  int received_data;

  forever begin
    @(posedge data_rcvd);
    expected_data = scoreboard_w_data[i];
    received_data = scoreboard_r_data[i];

    if (expected_data == received_data) begin
      $display("{%d} [SCOREBOARD] Data Matched from Read: %0h", cycle,received_data);
      i++;
    end else begin
      $display("{%d} [SCOREBOARD ERROR] Data did not match Actual: %0h Expected: %0h", cycle, received_data, expected_data);
      foreach (scoreboard_w_data[i]) begin
        $display("{%d} [SCOREBARD] Expected Queue[%d] is %h", cycle, i, scoreboard_w_data[i]);
      end
      $display("{%d} [SCOREBOARD] Scoreboard size of %d", cycle, scoreboard_w_data.size());
      $stop;
    end
    data_rcvd = 0;
  end
endtask 


endmodule