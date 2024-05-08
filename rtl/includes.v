//When a New module/ File is added, Incude it in this includes.v file.
//This file is included in the usb_hub_top main file directory
//The path of the files should be given from the root directory of the project

`include "rtl/common_defines.v"
`include "rtl/fifo.v"
`include "rtl/piso.v"
`include "rtl/polling_clock_gen.v"
`include "rtl/sequence_detector.v"
`include "rtl/sipo.v"
`include "rtl/usb_host_speed_detector.v"
`include "rtl/usb_mux.v"
`include "rtl/usb_trans_receiver.v"