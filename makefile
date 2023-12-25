CWD=$(shell pwd)
export COCOTB_REDUCED_LOG_FMT = 1
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(CWD)/rtl/usb_hub_top.v
##Need to add the Remaining RTL files ones created
#MODULE := tb_top
TOPLEVEL = usb_hub_top
GHDL_ARGS := --ieee=synopsys
COCOTB_HDL_TIMEUNIT = 1us
COCOTB_HDL_TIMEPRECISION = 1us
WAVES = 1
include $(shell cocotb-config --makefiles)/Makefile.sim