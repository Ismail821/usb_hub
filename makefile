CWD=$(shell pwd)
export COCOTB_REDUCED_LOG_FMT = 0
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(CWD)/rtl/usb_hub_top.v
##Need to add the Remaining RTL files ones created
MODULE := tests
# TESTCASE := USB_one_test
TOPLEVEL = usb_hub_top
GHDL_ARGS := --ieee=synopsys
COCOTB_HDL_TIMEUNIT = 100s
COCOTB_HDL_TIMEPRECISION = 1ns
WAVES = 1
include $(shell cocotb-config --makefiles)/Makefile.sim
include cleanall.mk