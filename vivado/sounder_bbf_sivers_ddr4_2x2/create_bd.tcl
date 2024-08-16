
################################################################
# This is a generated script based on design: system_bd
#
# Though there are limitations about the generated script,
# the main purpose of this utility is to make learning
# IP Integrator Tcl commands easier.
################################################################

namespace eval _tcl {
proc get_script_folder {} {
   set script_path [file normalize [info script]]
   set script_folder [file dirname $script_path]
   return $script_folder
}
}
variable script_folder
set script_folder [_tcl::get_script_folder]

################################################################
# Check if script is running in correct Vivado version.
################################################################
set scripts_vivado_version 2022.1
set current_vivado_version [version -short]

if { [string first $scripts_vivado_version $current_vivado_version] == -1 } {
   puts ""
   catch {common::send_gid_msg -ssname BD::TCL -id 2041 -severity "ERROR" "This script was generated using Vivado <$scripts_vivado_version> and is being run in <$current_vivado_version> of Vivado. Please run the script in Vivado <$scripts_vivado_version> then open the design in Vivado <$current_vivado_version>. Upgrade the design by running \"Tools => Report => Report IP Status...\", then run write_bd_tcl to create an updated script."}

   return 1
}

################################################################
# START
################################################################

# To test this script, run the following commands from Vivado Tcl console:
# source system_bd_script.tcl

# If there is no project opened, this script will create a
# project, but make sure you do not have an existing project
# <./myproj/project_1.xpr> in the current working folder.

set list_projs [get_projects -quiet]
if { $list_projs eq "" } {
   create_project project_1 myproj -part xczu28dr-ffvg1517-2-e
   set_property BOARD_PART xilinx.com:rfsoc2x2:part0:1.1 [current_project]
}


# CHANGE DESIGN NAME HERE
variable design_name
set design_name system_bd

# If you do not already have an existing IP Integrator design open,
# you can create a design using the following command:
#    create_bd_design $design_name

# Creating design if needed
set errMsg ""
set nRet 0

set cur_design [current_bd_design -quiet]
set list_cells [get_bd_cells -quiet]

if { ${design_name} eq "" } {
   # USE CASES:
   #    1) Design_name not set

   set errMsg "Please set the variable <design_name> to a non-empty value."
   set nRet 1

} elseif { ${cur_design} ne "" && ${list_cells} eq "" } {
   # USE CASES:
   #    2): Current design opened AND is empty AND names same.
   #    3): Current design opened AND is empty AND names diff; design_name NOT in project.
   #    4): Current design opened AND is empty AND names diff; design_name exists in project.

   if { $cur_design ne $design_name } {
      common::send_gid_msg -ssname BD::TCL -id 2001 -severity "INFO" "Changing value of <design_name> from <$design_name> to <$cur_design> since current design is empty."
      set design_name [get_property NAME $cur_design]
   }
   common::send_gid_msg -ssname BD::TCL -id 2002 -severity "INFO" "Constructing design in IPI design <$cur_design>..."

} elseif { ${cur_design} ne "" && $list_cells ne "" && $cur_design eq $design_name } {
   # USE CASES:
   #    5) Current design opened AND has components AND same names.

   set errMsg "Design <$design_name> already exists in your project, please set the variable <design_name> to another value."
   set nRet 1
} elseif { [get_files -quiet ${design_name}.bd] ne "" } {
   # USE CASES: 
   #    6) Current opened design, has components, but diff names, design_name exists in project.
   #    7) No opened design, design_name exists in project.

   set errMsg "Design <$design_name> already exists in your project, please set the variable <design_name> to another value."
   set nRet 2

} else {
   # USE CASES:
   #    8) No opened design, design_name not in project.
   #    9) Current opened design, has components, but diff names, design_name not in project.

   common::send_gid_msg -ssname BD::TCL -id 2003 -severity "INFO" "Currently there is no design <$design_name> in project, so creating one..."

   create_bd_design $design_name

   common::send_gid_msg -ssname BD::TCL -id 2004 -severity "INFO" "Making design <$design_name> as current_bd_design."
   current_bd_design $design_name

}

common::send_gid_msg -ssname BD::TCL -id 2005 -severity "INFO" "Currently the variable <design_name> is equal to \"$design_name\"."

if { $nRet != 0 } {
   catch {common::send_gid_msg -ssname BD::TCL -id 2006 -severity "ERROR" $errMsg}
   return $nRet
}

set bCheckIPsPassed 1
##################################################################
# CHECK IPs
##################################################################
set bCheckIPs 1
if { $bCheckIPs == 1 } {
   set list_check_ips "\ 
xilinx.com:ip:ddr4:2.2\
xilinx.com:ip:xlconcat:2.1\
xilinx.com:ip:smartconnect:1.0\
xilinx.com:ip:usp_rf_data_converter:2.6\
xilinx.com:ip:xlconstant:1.1\
xilinx.com:ip:xlslice:1.0\
xilinx.com:ip:zynq_ultra_ps_e:3.4\
xilinx.com:ip:axi_dma:7.1\
xilinx.com:ip:axis_combiner:1.1\
user.org:user:axis_flow_ctrl:1.0\
xilinx.com:ip:util_ds_buf:2.2\
xilinx.com:ip:clk_wiz:6.0\
xilinx.com:user:sync:1.0\
xilinx:user:binary_latch_counter:1.0\
xilinx.com:ip:proc_sys_reset:5.0\
xilinx.com:ip:util_vector_logic:2.0\
xilinx.com:ip:axis_clock_converter:1.1\
xilinx.com:ip:axis_data_fifo:2.0\
xilinx.com:ip:axis_register_slice:1.1\
xilinx.com:ip:axis_broadcaster:1.1\
user.org:user:adc_strm_mux:1.0\
"

   set list_ips_missing ""
   common::send_gid_msg -ssname BD::TCL -id 2011 -severity "INFO" "Checking if the following IPs exist in the project's IP catalog: $list_check_ips ."

   foreach ip_vlnv $list_check_ips {
      set ip_obj [get_ipdefs -all $ip_vlnv]
      if { $ip_obj eq "" } {
         lappend list_ips_missing $ip_vlnv
      }
   }

   if { $list_ips_missing ne "" } {
      catch {common::send_gid_msg -ssname BD::TCL -id 2012 -severity "ERROR" "The following IPs are not found in the IP Catalog:\n  $list_ips_missing\n\nResolution: Please add the repository containing the IP(s) to the project." }
      set bCheckIPsPassed 0
   }

}

if { $bCheckIPsPassed != 1 } {
  common::send_gid_msg -ssname BD::TCL -id 2023 -severity "WARNING" "Will not continue with creation of design due to the error(s) above."
  return 3
}

##################################################################
# DESIGN PROCs
##################################################################


# Hierarchical cell: soft_reset
proc create_hier_cell_soft_reset_1 { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2092 -severity "ERROR" "create_hier_cell_soft_reset_1() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins

  # Create pins
  create_bd_pin -dir I -from 94 -to 0 Din
  create_bd_pin -dir I -type clk dac_clk
  create_bd_pin -dir I -from 0 -to 0 dac_resetn
  create_bd_pin -dir O -from 0 -to 0 dac_sresetn
  create_bd_pin -dir I -type clk ddr4_clk
  create_bd_pin -dir I -from 0 -to 0 ddr4_resetn_1
  create_bd_pin -dir O -from 0 -to 0 ddr4_sresetn

  # Create instance: dac_sresetn, and set properties
  set dac_sresetn [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 dac_sresetn ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {0} \
   CONFIG.DIN_TO {0} \
   CONFIG.DIN_WIDTH {95} \
   CONFIG.DOUT_WIDTH {1} \
 ] $dac_sresetn

  # Create instance: sync_0, and set properties
  set sync_0 [ create_bd_cell -type ip -vlnv xilinx.com:user:sync:1.0 sync_0 ]
  set_property -dict [ list \
   CONFIG.SRC_INPUT_REG {0} \
 ] $sync_0

  # Create instance: sync_1, and set properties
  set sync_1 [ create_bd_cell -type ip -vlnv xilinx.com:user:sync:1.0 sync_1 ]
  set_property -dict [ list \
   CONFIG.SRC_INPUT_REG {0} \
 ] $sync_1

  # Create instance: util_vector_logic_0, and set properties
  set util_vector_logic_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_0 ]
  set_property -dict [ list \
   CONFIG.C_SIZE {1} \
 ] $util_vector_logic_0

  # Create instance: util_vector_logic_1, and set properties
  set util_vector_logic_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_1 ]
  set_property -dict [ list \
   CONFIG.C_SIZE {1} \
 ] $util_vector_logic_1

  # Create instance: util_vector_logic_2, and set properties
  set util_vector_logic_2 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_2 ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $util_vector_logic_2

  # Create instance: xlconstant_0, and set properties
  set xlconstant_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_0 ]
  set_property -dict [ list \
   CONFIG.CONST_VAL {0} \
 ] $xlconstant_0

  # Create port connections
  connect_bd_net -net Din_1 [get_bd_pins Din] [get_bd_pins dac_sresetn/Din]
  connect_bd_net -net dac_resetn_1 [get_bd_pins dac_resetn] [get_bd_pins util_vector_logic_1/Op2]
  connect_bd_net -net dac_sresetn_Dout [get_bd_pins dac_sresetn/Dout] [get_bd_pins util_vector_logic_2/Op1]
  connect_bd_net -net ddr4_0_c0_ddr4_ui_clk [get_bd_pins ddr4_clk] [get_bd_pins sync_0/dest_clk]
  connect_bd_net -net ddr4_resetn_1_1 [get_bd_pins ddr4_resetn_1] [get_bd_pins util_vector_logic_0/Op2]
  connect_bd_net -net m_axis_aclk_1 [get_bd_pins dac_clk] [get_bd_pins sync_1/dest_clk]
  connect_bd_net -net sync_0_dest_out [get_bd_pins sync_1/dest_out] [get_bd_pins util_vector_logic_1/Op1]
  connect_bd_net -net sync_2_dest_out [get_bd_pins sync_0/dest_out] [get_bd_pins util_vector_logic_0/Op1]
  connect_bd_net -net util_vector_logic_0_Res [get_bd_pins ddr4_sresetn] [get_bd_pins util_vector_logic_0/Res]
  connect_bd_net -net util_vector_logic_1_Res [get_bd_pins dac_sresetn] [get_bd_pins util_vector_logic_1/Res]
  connect_bd_net -net util_vector_logic_2_Res [get_bd_pins sync_0/src_in] [get_bd_pins sync_1/src_in] [get_bd_pins util_vector_logic_2/Res]
  connect_bd_net -net xlconstant_0_dout [get_bd_pins sync_0/src_clk] [get_bd_pins sync_1/src_clk] [get_bd_pins xlconstant_0/dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: mem
proc create_hier_cell_mem_1 { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2092 -severity "ERROR" "create_hier_cell_mem_1() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 M01_AXIS

  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 M02_AXIS

  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:axis_rtl:1.0 S_AXIS


  # Create pins
  create_bd_pin -dir I -from 94 -to 0 Din
  create_bd_pin -dir I -type clk dac_clk
  create_bd_pin -dir I -from 0 -to 0 dac_control
  create_bd_pin -dir I -type rst dac_resetn
  create_bd_pin -dir I -type clk ddr4_clk
  create_bd_pin -dir I -type rst ddr4_resetn

  # Create instance: axis_broadcaster_1, and set properties
  set axis_broadcaster_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_broadcaster:1.1 axis_broadcaster_1 ]
  set_property -dict [ list \
   CONFIG.M00_TDATA_REMAP {tdata[127:0]} \
   CONFIG.M01_TDATA_REMAP {tdata[127:0]} \
   CONFIG.M02_TDATA_REMAP {tdata[255:0]} \
   CONFIG.M03_TDATA_REMAP {tdata[7:0]} \
   CONFIG.M_TDATA_NUM_BYTES {16} \
   CONFIG.NUM_MI {2} \
   CONFIG.S_TDATA_NUM_BYTES {16} \
 ] $axis_broadcaster_1

  # Create instance: axis_broadcaster_2, and set properties
  set axis_broadcaster_2 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_broadcaster:1.1 axis_broadcaster_2 ]
  set_property -dict [ list \
   CONFIG.M00_TDATA_REMAP {tdata[63:0]} \
   CONFIG.M01_TDATA_REMAP {tdata[127:64]} \
   CONFIG.M02_TDATA_REMAP {tdata[255:0]} \
   CONFIG.M03_TDATA_REMAP {tdata[7:0]} \
   CONFIG.M_TDATA_NUM_BYTES {8} \
   CONFIG.NUM_MI {2} \
   CONFIG.S_TDATA_NUM_BYTES {16} \
 ] $axis_broadcaster_2

  # Create instance: axis_data_fifo_0, and set properties
  set axis_data_fifo_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_data_fifo:2.0 axis_data_fifo_0 ]
  set_property -dict [ list \
   CONFIG.FIFO_DEPTH {16} \
 ] $axis_data_fifo_0

  # Create instance: axis_data_fifo_1, and set properties
  set axis_data_fifo_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_data_fifo:2.0 axis_data_fifo_1 ]
  set_property -dict [ list \
   CONFIG.FIFO_DEPTH {16} \
   CONFIG.IS_ACLK_ASYNC {1} \
   CONFIG.SYNCHRONIZATION_STAGES {2} \
 ] $axis_data_fifo_1

  # Create instance: axis_data_fifo_2, and set properties
  set axis_data_fifo_2 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_data_fifo:2.0 axis_data_fifo_2 ]
  set_property -dict [ list \
   CONFIG.FIFO_DEPTH {2048} \
   CONFIG.IS_ACLK_ASYNC {0} \
   CONFIG.SYNCHRONIZATION_STAGES {3} \
 ] $axis_data_fifo_2

  # Create instance: axis_register_slice_0, and set properties
  set axis_register_slice_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_register_slice:1.1 axis_register_slice_0 ]

  # Create instance: control_tready, and set properties
  set control_tready [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 control_tready ]
  set_property -dict [ list \
   CONFIG.C_SIZE {1} \
 ] $control_tready

  # Create instance: control_tvalid, and set properties
  set control_tvalid [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 control_tvalid ]
  set_property -dict [ list \
   CONFIG.C_SIZE {1} \
 ] $control_tvalid

  # Create instance: dac_strm_mux, and set properties
  set dac_strm_mux [ create_bd_cell -type ip -vlnv user.org:user:adc_strm_mux:1.0 dac_strm_mux ]
  set_property -dict [ list \
   CONFIG.AXIS_TDATA_WIDTH {128} \
   CONFIG.AXIS_TKEEP_WIDTH {16} \
 ] $dac_strm_mux

  # Create instance: xlslice_0, and set properties
  set xlslice_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {3} \
   CONFIG.DIN_TO {3} \
   CONFIG.DIN_WIDTH {95} \
   CONFIG.DOUT_WIDTH {1} \
 ] $xlslice_0

  # Create interface connections
  connect_bd_intf_net -intf_net axis_broadcaster_1_M00_AXIS [get_bd_intf_pins axis_broadcaster_1/M00_AXIS] [get_bd_intf_pins axis_data_fifo_0/S_AXIS]
  connect_bd_intf_net -intf_net axis_broadcaster_1_M01_AXIS [get_bd_intf_pins axis_broadcaster_1/M01_AXIS] [get_bd_intf_pins axis_broadcaster_2/S_AXIS]
  connect_bd_intf_net -intf_net axis_broadcaster_2_M00_AXIS [get_bd_intf_pins M01_AXIS] [get_bd_intf_pins axis_broadcaster_2/M00_AXIS]
  connect_bd_intf_net -intf_net axis_broadcaster_2_M01_AXIS [get_bd_intf_pins M02_AXIS] [get_bd_intf_pins axis_broadcaster_2/M01_AXIS]
  connect_bd_intf_net -intf_net axis_data_fifo_0_M_AXIS [get_bd_intf_pins axis_data_fifo_0/M_AXIS] [get_bd_intf_pins dac_strm_mux/s1_axi_stream]
  connect_bd_intf_net -intf_net axis_data_fifo_1_M_AXIS [get_bd_intf_pins axis_data_fifo_1/M_AXIS] [get_bd_intf_pins dac_strm_mux/s0_axi_stream]
  connect_bd_intf_net -intf_net axis_data_fifo_2_M_AXIS [get_bd_intf_pins axis_data_fifo_2/M_AXIS] [get_bd_intf_pins axis_register_slice_0/S_AXIS]
  connect_bd_intf_net -intf_net axis_register_slice_0_M_AXIS [get_bd_intf_pins axis_broadcaster_1/S_AXIS] [get_bd_intf_pins axis_register_slice_0/M_AXIS]
  connect_bd_intf_net -intf_net dac_strm_mux_m0_axi_stream [get_bd_intf_pins axis_data_fifo_2/S_AXIS] [get_bd_intf_pins dac_strm_mux/m0_axi_stream]
  connect_bd_intf_net -intf_net dma_dac_0_M_AXIS_MM2S [get_bd_intf_pins S_AXIS] [get_bd_intf_pins axis_data_fifo_1/S_AXIS]

  # Create port connections
  connect_bd_net -net Din_1 [get_bd_pins Din] [get_bd_pins xlslice_0/Din]
  connect_bd_net -net Op2_1 [get_bd_pins dac_control] [get_bd_pins control_tready/Op2] [get_bd_pins control_tvalid/Op2]
  connect_bd_net -net axis_broadcaster_1_s_axis_tready [get_bd_pins axis_broadcaster_1/s_axis_tready] [get_bd_pins control_tready/Op1]
  connect_bd_net -net axis_register_slice_0_m_axis_tvalid [get_bd_pins axis_register_slice_0/m_axis_tvalid] [get_bd_pins control_tvalid/Op1]
  connect_bd_net -net ddr4_0_c0_ddr4_ui_clk [get_bd_pins ddr4_clk] [get_bd_pins axis_data_fifo_1/s_axis_aclk]
  connect_bd_net -net m_axis_aclk_1 [get_bd_pins dac_clk] [get_bd_pins axis_broadcaster_1/aclk] [get_bd_pins axis_broadcaster_2/aclk] [get_bd_pins axis_data_fifo_0/s_axis_aclk] [get_bd_pins axis_data_fifo_1/m_axis_aclk] [get_bd_pins axis_data_fifo_2/s_axis_aclk] [get_bd_pins axis_register_slice_0/aclk] [get_bd_pins dac_strm_mux/s_axis_aclk]
  connect_bd_net -net util_vector_logic_0_Res [get_bd_pins dac_resetn] [get_bd_pins axis_broadcaster_1/aresetn] [get_bd_pins axis_broadcaster_2/aresetn] [get_bd_pins axis_data_fifo_0/s_axis_aresetn] [get_bd_pins axis_data_fifo_2/s_axis_aresetn] [get_bd_pins axis_register_slice_0/aresetn]
  connect_bd_net -net util_vector_logic_0_Res1 [get_bd_pins axis_register_slice_0/m_axis_tready] [get_bd_pins control_tready/Res]
  connect_bd_net -net util_vector_logic_1_Res [get_bd_pins ddr4_resetn] [get_bd_pins axis_data_fifo_1/s_axis_aresetn]
  connect_bd_net -net util_vector_logic_1_Res1 [get_bd_pins axis_broadcaster_1/s_axis_tvalid] [get_bd_pins control_tvalid/Res]
  connect_bd_net -net xlslice_0_Dout [get_bd_pins dac_strm_mux/mux_select] [get_bd_pins xlslice_0/Dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: soft_reset
proc create_hier_cell_soft_reset { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2092 -severity "ERROR" "create_hier_cell_soft_reset() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins

  # Create pins
  create_bd_pin -dir I -from 94 -to 0 Din
  create_bd_pin -dir I -type clk adc_clk
  create_bd_pin -dir I -from 0 -to 0 -type rst adc_resetn
  create_bd_pin -dir O -from 0 -to 0 adc_sresetn
  create_bd_pin -dir I -type clk ddr4_clk
  create_bd_pin -dir I -from 0 -to 0 ddr4_resetn
  create_bd_pin -dir O -from 0 -to 0 ddr4_sresetn

  # Create instance: sync_0, and set properties
  set sync_0 [ create_bd_cell -type ip -vlnv xilinx.com:user:sync:1.0 sync_0 ]
  set_property -dict [ list \
   CONFIG.SRC_INPUT_REG {0} \
 ] $sync_0

  # Create instance: sync_1, and set properties
  set sync_1 [ create_bd_cell -type ip -vlnv xilinx.com:user:sync:1.0 sync_1 ]
  set_property -dict [ list \
   CONFIG.SRC_INPUT_REG {0} \
 ] $sync_1

  # Create instance: util_vector_logic_0, and set properties
  set util_vector_logic_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_0 ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $util_vector_logic_0

  # Create instance: util_vector_logic_3, and set properties
  set util_vector_logic_3 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_3 ]
  set_property -dict [ list \
   CONFIG.C_SIZE {1} \
 ] $util_vector_logic_3

  # Create instance: util_vector_logic_4, and set properties
  set util_vector_logic_4 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_4 ]
  set_property -dict [ list \
   CONFIG.C_SIZE {1} \
 ] $util_vector_logic_4

  # Create instance: xlconstant_0, and set properties
  set xlconstant_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_0 ]
  set_property -dict [ list \
   CONFIG.CONST_VAL {0} \
 ] $xlconstant_0

  # Create instance: xlslice_0, and set properties
  set xlslice_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {32} \
   CONFIG.DIN_TO {32} \
   CONFIG.DIN_WIDTH {95} \
   CONFIG.DOUT_WIDTH {1} \
 ] $xlslice_0

  # Create port connections
  connect_bd_net -net Din_1 [get_bd_pins Din] [get_bd_pins xlslice_0/Din]
  connect_bd_net -net aclk_1 [get_bd_pins adc_clk] [get_bd_pins sync_0/dest_clk]
  connect_bd_net -net ddr4_clk_1 [get_bd_pins ddr4_clk] [get_bd_pins sync_1/dest_clk]
  connect_bd_net -net ddr4_resetn_1_1 [get_bd_pins ddr4_resetn] [get_bd_pins util_vector_logic_3/Op2]
  connect_bd_net -net rst_ps8_100M_peripheral_aresetn [get_bd_pins adc_resetn] [get_bd_pins util_vector_logic_4/Op2]
  connect_bd_net -net sync_0_dest_out [get_bd_pins sync_0/dest_out] [get_bd_pins util_vector_logic_4/Op1]
  connect_bd_net -net sync_1_dest_out [get_bd_pins sync_1/dest_out] [get_bd_pins util_vector_logic_3/Op1]
  connect_bd_net -net util_vector_logic_0_Res [get_bd_pins sync_0/src_in] [get_bd_pins sync_1/src_in] [get_bd_pins util_vector_logic_0/Res]
  connect_bd_net -net util_vector_logic_3_Res [get_bd_pins ddr4_sresetn] [get_bd_pins util_vector_logic_3/Res]
  connect_bd_net -net util_vector_logic_4_Res [get_bd_pins adc_sresetn] [get_bd_pins util_vector_logic_4/Res]
  connect_bd_net -net xlconstant_0_dout [get_bd_pins sync_0/src_clk] [get_bd_pins sync_1/src_clk] [get_bd_pins xlconstant_0/dout]
  connect_bd_net -net xlslice_0_Dout [get_bd_pins util_vector_logic_0/Op1] [get_bd_pins xlslice_0/Dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: mem
proc create_hier_cell_mem { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2092 -severity "ERROR" "create_hier_cell_mem() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 M_AXIS

  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:axis_rtl:1.0 S_AXIS


  # Create pins
  create_bd_pin -dir I -type clk adc_clk
  create_bd_pin -dir I -type rst adc_resetn
  create_bd_pin -dir I -type clk ddr4_clk
  create_bd_pin -dir I -type rst ddr4_resetn

  # Create instance: axis_clock_converter_0, and set properties
  set axis_clock_converter_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_clock_converter:1.1 axis_clock_converter_0 ]

  # Create instance: axis_data_fifo_0, and set properties
  set axis_data_fifo_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_data_fifo:2.0 axis_data_fifo_0 ]
  set_property -dict [ list \
   CONFIG.FIFO_DEPTH {32768} \
   CONFIG.IS_ACLK_ASYNC {0} \
   CONFIG.SYNCHRONIZATION_STAGES {3} \
 ] $axis_data_fifo_0

  # Create instance: axis_register_slice_0, and set properties
  set axis_register_slice_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_register_slice:1.1 axis_register_slice_0 ]

  # Create interface connections
  connect_bd_intf_net -intf_net axis_clock_converter_0_M_AXIS [get_bd_intf_pins axis_clock_converter_0/M_AXIS] [get_bd_intf_pins axis_data_fifo_0/S_AXIS]
  connect_bd_intf_net -intf_net axis_data_fifo_0_M_AXIS [get_bd_intf_pins M_AXIS] [get_bd_intf_pins axis_data_fifo_0/M_AXIS]
  connect_bd_intf_net -intf_net axis_flow_ctrl_0_m_axis [get_bd_intf_pins S_AXIS] [get_bd_intf_pins axis_register_slice_0/S_AXIS]
  connect_bd_intf_net -intf_net axis_register_slice_0_M_AXIS [get_bd_intf_pins axis_clock_converter_0/S_AXIS] [get_bd_intf_pins axis_register_slice_0/M_AXIS]

  # Create port connections
  connect_bd_net -net aclk_1 [get_bd_pins adc_clk] [get_bd_pins axis_clock_converter_0/s_axis_aclk] [get_bd_pins axis_register_slice_0/aclk]
  connect_bd_net -net ddr4_0_c0_ddr4_ui_clk [get_bd_pins ddr4_clk] [get_bd_pins axis_clock_converter_0/m_axis_aclk] [get_bd_pins axis_data_fifo_0/s_axis_aclk]
  connect_bd_net -net ddr4_resetn_1 [get_bd_pins ddr4_resetn] [get_bd_pins axis_clock_converter_0/m_axis_aresetn] [get_bd_pins axis_data_fifo_0/s_axis_aresetn]
  connect_bd_net -net util_vector_logic_1_Res [get_bd_pins adc_resetn] [get_bd_pins axis_clock_converter_0/s_axis_aresetn] [get_bd_pins axis_register_slice_0/aresetn]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: reset_block
proc create_hier_cell_reset_block { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2092 -severity "ERROR" "create_hier_cell_reset_block() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins

  # Create pins
  create_bd_pin -dir I -type clk clk_in1
  create_bd_pin -dir I dcm_locked
  create_bd_pin -dir I -type clk ddr4_clk
  create_bd_pin -dir O -from 0 -to 0 -type rst ddr4_resetn_1
  create_bd_pin -dir I -type rst ddr4_rstn
  create_bd_pin -dir O -from 0 -to 0 ddr4_sys_rst
  create_bd_pin -dir I -type clk ps8_clk
  create_bd_pin -dir O -from 0 -to 0 -type rst ps8_resetn_0
  create_bd_pin -dir O -from 0 -to 0 -type rst ps8_resetn_1
  create_bd_pin -dir I -type rst ps8_rstn
  create_bd_pin -dir I -type clk rf_clk
  create_bd_pin -dir O -from 0 -to 0 -type rst rf_resetn

  # Create instance: binary_latch_counter_0, and set properties
  set binary_latch_counter_0 [ create_bd_cell -type ip -vlnv xilinx:user:binary_latch_counter:1.0 binary_latch_counter_0 ]

  # Create instance: clk_wiz_0, and set properties
  set clk_wiz_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:6.0 clk_wiz_0 ]
  set_property -dict [ list \
   CONFIG.CLKIN1_JITTER_PS {50.0} \
   CONFIG.CLKOUT1_JITTER {92.799} \
   CONFIG.CLKOUT1_PHASE_ERROR {82.655} \
   CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {200.000} \
   CONFIG.MMCM_CLKFBOUT_MULT_F {6.000} \
   CONFIG.MMCM_CLKIN1_PERIOD {5.000} \
   CONFIG.MMCM_CLKIN2_PERIOD {10.0} \
   CONFIG.MMCM_CLKOUT0_DIVIDE_F {6.000} \
   CONFIG.PRIM_IN_FREQ {200.000} \
   CONFIG.PRIM_SOURCE {No_buffer} \
 ] $clk_wiz_0

  # Create instance: rst_adc_245M, and set properties
  set rst_adc_245M [ create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 rst_adc_245M ]

  # Create instance: rst_ddr4_200M, and set properties
  set rst_ddr4_200M [ create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 rst_ddr4_200M ]

  # Create instance: rst_ps8_100M, and set properties
  set rst_ps8_100M [ create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 rst_ps8_100M ]

  # Create instance: util_vector_logic_0, and set properties
  set util_vector_logic_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_0 ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $util_vector_logic_0

  # Create instance: util_vector_logic_1, and set properties
  set util_vector_logic_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_1 ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $util_vector_logic_1

  # Create port connections
  connect_bd_net -net ADC_clk_wiz_0_clk_out1 [get_bd_pins rf_clk] [get_bd_pins rst_adc_245M/slowest_sync_clk]
  connect_bd_net -net binary_latch_counter_0_latched [get_bd_pins binary_latch_counter_0/latched] [get_bd_pins util_vector_logic_0/Op1]
  connect_bd_net -net clk_in1_1 [get_bd_pins clk_in1] [get_bd_pins clk_wiz_0/clk_in1]
  connect_bd_net -net clk_wiz_0_locked [get_bd_pins clk_wiz_0/locked] [get_bd_pins util_vector_logic_1/Op1]
  connect_bd_net -net dcm_locked_1 [get_bd_pins dcm_locked] [get_bd_pins rst_adc_245M/dcm_locked]
  connect_bd_net -net ddr4_0_c0_ddr4_ui_clk [get_bd_pins ddr4_clk] [get_bd_pins rst_ddr4_200M/slowest_sync_clk]
  connect_bd_net -net ddr4_0_c0_ddr4_ui_clk_sync_rst [get_bd_pins ddr4_rstn] [get_bd_pins rst_ddr4_200M/ext_reset_in]
  connect_bd_net -net rst_adc_0_245M_peripheral_aresetn [get_bd_pins rf_resetn] [get_bd_pins rst_adc_245M/peripheral_aresetn]
  connect_bd_net -net rst_ddr4_200M_peripheral_aresetn [get_bd_pins ddr4_resetn_1] [get_bd_pins rst_ddr4_200M/peripheral_aresetn]
  connect_bd_net -net rst_ps8_100M_interconnect_aresetn [get_bd_pins ps8_resetn_0] [get_bd_pins rst_ps8_100M/interconnect_aresetn]
  connect_bd_net -net rst_ps8_100M_peripheral_aresetn [get_bd_pins ps8_resetn_1] [get_bd_pins binary_latch_counter_0/resetn] [get_bd_pins rst_ps8_100M/peripheral_aresetn]
  connect_bd_net -net util_vector_logic_0_Res [get_bd_pins clk_wiz_0/reset] [get_bd_pins util_vector_logic_0/Res]
  connect_bd_net -net util_vector_logic_1_Res [get_bd_pins ddr4_sys_rst] [get_bd_pins util_vector_logic_1/Res]
  connect_bd_net -net zynq_ultra_ps_e_0_pl_clk0 [get_bd_pins ps8_clk] [get_bd_pins binary_latch_counter_0/clk] [get_bd_pins rst_ps8_100M/slowest_sync_clk]
  connect_bd_net -net zynq_ultra_ps_e_0_pl_resetn0 [get_bd_pins ps8_rstn] [get_bd_pins rst_adc_245M/ext_reset_in] [get_bd_pins rst_ps8_100M/ext_reset_in]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: dac_path
proc create_hier_cell_dac_path { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2092 -severity "ERROR" "create_hier_cell_dac_path() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 DAC0_AXIS

  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 DAC1_AXIS

  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:aximm_rtl:1.0 PL_MEM_AXI

  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:aximm_rtl:1.0 PS_MEM_AXI

  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 S_AXI_LITE


  # Create pins
  create_bd_pin -dir I -from 94 -to 0 Din
  create_bd_pin -dir I -type clk dac_clk
  create_bd_pin -dir I dac_control
  create_bd_pin -dir I dac_resetn
  create_bd_pin -dir I -type clk ddr4_clk
  create_bd_pin -dir I -type rst ddr4_resetn_1
  create_bd_pin -dir O -type intr mm2s_introut
  create_bd_pin -dir I -type clk ps8_clk
  create_bd_pin -dir I -type rst ps8_resetn

  # Create instance: axi_dma_0, and set properties
  set axi_dma_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 axi_dma_0 ]
  set_property -dict [ list \
   CONFIG.c_addr_width {64} \
   CONFIG.c_include_s2mm {0} \
   CONFIG.c_include_sg {0} \
   CONFIG.c_m_axi_mm2s_data_width {256} \
   CONFIG.c_m_axis_mm2s_tdata_width {128} \
   CONFIG.c_mm2s_burst_size {128} \
   CONFIG.c_sg_include_stscntrl_strm {0} \
   CONFIG.c_sg_length_width {26} \
 ] $axi_dma_0

  # Create instance: mem
  create_hier_cell_mem_1 $hier_obj mem

  # Create instance: smartconnect_0, and set properties
  set smartconnect_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect:1.0 smartconnect_0 ]
  set_property -dict [ list \
   CONFIG.NUM_MI {2} \
   CONFIG.NUM_SI {1} \
 ] $smartconnect_0

  # Create instance: soft_reset
  create_hier_cell_soft_reset_1 $hier_obj soft_reset

  # Create interface connections
  connect_bd_intf_net -intf_net Conn1 [get_bd_intf_pins DAC0_AXIS] [get_bd_intf_pins mem/M01_AXIS]
  connect_bd_intf_net -intf_net Conn2 [get_bd_intf_pins DAC1_AXIS] [get_bd_intf_pins mem/M02_AXIS]
  connect_bd_intf_net -intf_net axi_dma_0_M_AXI_MM2S [get_bd_intf_pins axi_dma_0/M_AXI_MM2S] [get_bd_intf_pins smartconnect_0/S00_AXI]
  connect_bd_intf_net -intf_net dma_dac_0_M_AXIS_MM2S [get_bd_intf_pins axi_dma_0/M_AXIS_MM2S] [get_bd_intf_pins mem/S_AXIS]
  connect_bd_intf_net -intf_net ps8_axi_periph_M00_AXI [get_bd_intf_pins S_AXI_LITE] [get_bd_intf_pins axi_dma_0/S_AXI_LITE]
  connect_bd_intf_net -intf_net smartconnect_0_M00_AXI [get_bd_intf_pins PS_MEM_AXI] [get_bd_intf_pins smartconnect_0/M00_AXI]
  connect_bd_intf_net -intf_net smartconnect_0_M01_AXI [get_bd_intf_pins PL_MEM_AXI] [get_bd_intf_pins smartconnect_0/M01_AXI]

  # Create port connections
  connect_bd_net -net Din_1 [get_bd_pins Din] [get_bd_pins mem/Din] [get_bd_pins soft_reset/Din]
  connect_bd_net -net Op2_1 [get_bd_pins dac_control] [get_bd_pins mem/dac_control]
  connect_bd_net -net dac_resetn_1 [get_bd_pins dac_resetn] [get_bd_pins soft_reset/dac_resetn]
  connect_bd_net -net ddr4_0_c0_ddr4_ui_clk [get_bd_pins ddr4_clk] [get_bd_pins axi_dma_0/m_axi_mm2s_aclk] [get_bd_pins mem/ddr4_clk] [get_bd_pins smartconnect_0/aclk] [get_bd_pins soft_reset/ddr4_clk]
  connect_bd_net -net dma_dac_0_mm2s_introut [get_bd_pins mm2s_introut] [get_bd_pins axi_dma_0/mm2s_introut]
  connect_bd_net -net m_axis_aclk_1 [get_bd_pins dac_clk] [get_bd_pins mem/dac_clk] [get_bd_pins soft_reset/dac_clk]
  connect_bd_net -net rst_ddr4_200M_peripheral_aresetn [get_bd_pins ddr4_resetn_1] [get_bd_pins smartconnect_0/aresetn] [get_bd_pins soft_reset/ddr4_resetn_1]
  connect_bd_net -net rst_ps8_100M_peripheral_aresetn [get_bd_pins ps8_resetn] [get_bd_pins axi_dma_0/axi_resetn]
  connect_bd_net -net util_vector_logic_0_Res [get_bd_pins mem/dac_resetn] [get_bd_pins soft_reset/dac_sresetn]
  connect_bd_net -net util_vector_logic_1_Res [get_bd_pins mem/ddr4_resetn] [get_bd_pins soft_reset/ddr4_sresetn]
  connect_bd_net -net zynq_ultra_ps_e_0_pl_clk0 [get_bd_pins ps8_clk] [get_bd_pins axi_dma_0/s_axi_lite_aclk]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: clocktreeMTS
proc create_hier_cell_clocktreeMTS { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2092 -severity "ERROR" "create_hier_cell_clocktreeMTS() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 lmk_clk1

  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 lmk_clk2

  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 s_axi_lite

  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 sys_clk_ddr4


  # Create pins
  create_bd_pin -dir I -from 94 -to 0 Din
  create_bd_pin -dir O -from 0 -to 0 adc_control
  create_bd_pin -dir O -from 0 -to 0 dac_control
  create_bd_pin -dir O -from 0 -to 0 -type clk ddr_clk
  create_bd_pin -dir O -type intr interrupt
  create_bd_pin -dir O locked
  create_bd_pin -dir O -type clk rf_clk
  create_bd_pin -dir I -type clk s_axi_aclk
  create_bd_pin -dir I -type rst s_axi_aresetn
  create_bd_pin -dir O -from 0 -to 0 user_sysref

  # Create instance: BUFG_DDR4, and set properties
  set BUFG_DDR4 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_ds_buf:2.2 BUFG_DDR4 ]
  set_property -dict [ list \
   CONFIG.C_BUF_TYPE {BUFG} \
 ] $BUFG_DDR4

  # Create instance: BUFG_PL_CLK, and set properties
  set BUFG_PL_CLK [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_ds_buf:2.2 BUFG_PL_CLK ]
  set_property -dict [ list \
   CONFIG.C_BUF_TYPE {BUFG} \
 ] $BUFG_PL_CLK

  # Create instance: IBUFDS_DDR4, and set properties
  set IBUFDS_DDR4 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_ds_buf:2.2 IBUFDS_DDR4 ]

  # Create instance: IBUFDS_PL_CLK, and set properties
  set IBUFDS_PL_CLK [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_ds_buf:2.2 IBUFDS_PL_CLK ]

  # Create instance: IBUFDS_SYSREF, and set properties
  set IBUFDS_SYSREF [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_ds_buf:2.2 IBUFDS_SYSREF ]

  # Create instance: adc_control, and set properties
  set adc_control [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 adc_control ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {34} \
   CONFIG.DIN_TO {34} \
   CONFIG.DIN_WIDTH {95} \
   CONFIG.DOUT_WIDTH {1} \
 ] $adc_control

  # Create instance: clk_wiz_0, and set properties
  set clk_wiz_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:6.0 clk_wiz_0 ]
  set_property -dict [ list \
   CONFIG.CLKIN1_JITTER_PS {81.38} \
   CONFIG.CLKIN1_UI_JITTER {0.010} \
   CONFIG.CLKIN2_JITTER_PS {100.0} \
   CONFIG.CLKIN2_UI_JITTER {0.010} \
   CONFIG.CLKOUT1_DRIVES {Buffer} \
   CONFIG.CLKOUT1_JITTER {82.359} \
   CONFIG.CLKOUT1_PHASE_ERROR {74.849} \
   CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {245.76} \
   CONFIG.CLKOUT1_REQUESTED_PHASE {0} \
   CONFIG.CLKOUT1_USED {true} \
   CONFIG.CLKOUT2_DRIVES {Buffer} \
   CONFIG.CLKOUT2_JITTER {82.359} \
   CONFIG.CLKOUT2_PHASE_ERROR {74.849} \
   CONFIG.CLKOUT2_REQUESTED_OUT_FREQ {245.76} \
   CONFIG.CLKOUT2_REQUESTED_PHASE {22.5} \
   CONFIG.CLKOUT2_USED {true} \
   CONFIG.CLKOUT3_DRIVES {Buffer} \
   CONFIG.CLKOUT4_DRIVES {Buffer} \
   CONFIG.CLKOUT5_DRIVES {Buffer} \
   CONFIG.CLKOUT6_DRIVES {Buffer} \
   CONFIG.CLKOUT7_DRIVES {Buffer} \
   CONFIG.ENABLE_CLOCK_MONITOR {true} \
   CONFIG.JITTER_OPTIONS {UI} \
   CONFIG.JITTER_SEL {Min_O_Jitter} \
   CONFIG.MMCM_BANDWIDTH {HIGH} \
   CONFIG.MMCM_CLKFBOUT_MULT_F {12.000} \
   CONFIG.MMCM_CLKIN1_PERIOD {8.138} \
   CONFIG.MMCM_CLKOUT0_DIVIDE_F {6.000} \
   CONFIG.MMCM_CLKOUT0_PHASE {0.000} \
   CONFIG.MMCM_CLKOUT1_DIVIDE {6} \
   CONFIG.MMCM_CLKOUT1_PHASE {22.500} \
   CONFIG.MMCM_REF_JITTER1 {0.010} \
   CONFIG.MMCM_REF_JITTER2 {0.010} \
   CONFIG.NUM_OUT_CLKS {2} \
   CONFIG.OPTIMIZE_CLOCKING_STRUCTURE_EN {true} \
   CONFIG.PRIMITIVE {MMCM} \
   CONFIG.PRIM_IN_FREQ {122.88} \
   CONFIG.PRIM_SOURCE {Global_buffer} \
   CONFIG.SECONDARY_SOURCE {Single_ended_clock_capable_pin} \
   CONFIG.USE_PHASE_ALIGNMENT {true} \
 ] $clk_wiz_0

  # Create instance: dac_control, and set properties
  set dac_control [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 dac_control ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {2} \
   CONFIG.DIN_TO {2} \
   CONFIG.DIN_WIDTH {95} \
   CONFIG.DOUT_WIDTH {1} \
 ] $dac_control

  # Create instance: sync_0, and set properties
  set sync_0 [ create_bd_cell -type ip -vlnv xilinx.com:user:sync:1.0 sync_0 ]
  set_property -dict [ list \
   CONFIG.DEST_SYNC_FF {2} \
   CONFIG.SRC_INPUT_REG {0} \
 ] $sync_0

  # Create instance: sync_1, and set properties
  set sync_1 [ create_bd_cell -type ip -vlnv xilinx.com:user:sync:1.0 sync_1 ]
  set_property -dict [ list \
   CONFIG.DEST_SYNC_FF {2} \
   CONFIG.SRC_INPUT_REG {0} \
 ] $sync_1

  # Create instance: sync_2, and set properties
  set sync_2 [ create_bd_cell -type ip -vlnv xilinx.com:user:sync:1.0 sync_2 ]
  set_property -dict [ list \
   CONFIG.DEST_SYNC_FF {2} \
   CONFIG.SRC_INPUT_REG {0} \
 ] $sync_2

  # Create instance: sync_3, and set properties
  set sync_3 [ create_bd_cell -type ip -vlnv xilinx.com:user:sync:1.0 sync_3 ]
  set_property -dict [ list \
   CONFIG.DEST_SYNC_FF {2} \
   CONFIG.SRC_INPUT_REG {0} \
 ] $sync_3

  # Create instance: xlconstant_0, and set properties
  set xlconstant_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_0 ]
  set_property -dict [ list \
   CONFIG.CONST_VAL {0} \
 ] $xlconstant_0

  # Create interface connections
  connect_bd_intf_net -intf_net Conn1 [get_bd_intf_pins s_axi_lite] [get_bd_intf_pins clk_wiz_0/s_axi_lite]
  connect_bd_intf_net -intf_net lmk_clk1_1 [get_bd_intf_pins lmk_clk2] [get_bd_intf_pins IBUFDS_SYSREF/CLK_IN_D]
  connect_bd_intf_net -intf_net lmk_clk2_1 [get_bd_intf_pins lmk_clk1] [get_bd_intf_pins IBUFDS_PL_CLK/CLK_IN_D]
  connect_bd_intf_net -intf_net sys_clk_ddr4_1 [get_bd_intf_pins sys_clk_ddr4] [get_bd_intf_pins IBUFDS_DDR4/CLK_IN_D]

  # Create port connections
  connect_bd_net -net BUFG_DDR4_BUFG_O [get_bd_pins ddr_clk] [get_bd_pins BUFG_DDR4/BUFG_O]
  connect_bd_net -net BUFG_PL_CLK_BUFG_O [get_bd_pins BUFG_PL_CLK/BUFG_O] [get_bd_pins clk_wiz_0/clk_in1] [get_bd_pins sync_3/dest_clk]
  connect_bd_net -net Din_1 [get_bd_pins Din] [get_bd_pins adc_control/Din] [get_bd_pins dac_control/Din]
  connect_bd_net -net IBUFDS_DDR4_IBUF_OUT [get_bd_pins BUFG_DDR4/BUFG_I] [get_bd_pins IBUFDS_DDR4/IBUF_OUT]
  connect_bd_net -net IBUFDS_PL_CLK_IBUF_OUT [get_bd_pins BUFG_PL_CLK/BUFG_I] [get_bd_pins IBUFDS_PL_CLK/IBUF_OUT]
  connect_bd_net -net IBUFDS_SYSREF_IBUF_OUT [get_bd_pins IBUFDS_SYSREF/IBUF_OUT] [get_bd_pins sync_3/src_in]
  connect_bd_net -net adc_control_Dout [get_bd_pins adc_control/Dout] [get_bd_pins sync_0/src_in]
  connect_bd_net -net clk_wiz_0_clk_out1 [get_bd_pins clk_wiz_0/clk_out1] [get_bd_pins sync_0/dest_clk] [get_bd_pins sync_1/dest_clk]
  connect_bd_net -net clk_wiz_0_clk_out2 [get_bd_pins rf_clk] [get_bd_pins clk_wiz_0/clk_out2] [get_bd_pins sync_2/dest_clk]
  connect_bd_net -net clk_wiz_0_interrupt [get_bd_pins interrupt] [get_bd_pins clk_wiz_0/interrupt]
  connect_bd_net -net clk_wiz_0_locked [get_bd_pins locked] [get_bd_pins clk_wiz_0/locked]
  connect_bd_net -net dac_control_Dout [get_bd_pins dac_control/Dout] [get_bd_pins sync_1/src_in]
  connect_bd_net -net s_axi_aclk_1 [get_bd_pins s_axi_aclk] [get_bd_pins clk_wiz_0/ref_clk] [get_bd_pins clk_wiz_0/s_axi_aclk]
  connect_bd_net -net s_axi_aresetn_1 [get_bd_pins s_axi_aresetn] [get_bd_pins clk_wiz_0/s_axi_aresetn]
  connect_bd_net -net sync_0_dest_out [get_bd_pins adc_control] [get_bd_pins sync_0/dest_out]
  connect_bd_net -net sync_1_dest_out [get_bd_pins dac_control] [get_bd_pins sync_1/dest_out]
  connect_bd_net -net sync_2_dest_out [get_bd_pins user_sysref] [get_bd_pins sync_2/dest_out]
  connect_bd_net -net sync_3_dest_out [get_bd_pins sync_2/src_in] [get_bd_pins sync_3/dest_out]
  connect_bd_net -net xlconstant_0_dout [get_bd_pins sync_0/src_clk] [get_bd_pins sync_1/src_clk] [get_bd_pins sync_2/src_clk] [get_bd_pins sync_3/src_clk] [get_bd_pins xlconstant_0/dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: adc_path
proc create_hier_cell_adc_path { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2092 -severity "ERROR" "create_hier_cell_adc_path() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:axis_rtl:1.0 ADC0_AXIS

  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:axis_rtl:1.0 ADC1_AXIS

  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 DMA_AXI_LITE

  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 FLOW_AXI_LITE

  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:aximm_rtl:1.0 PL_MEM_AXI

  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:aximm_rtl:1.0 PS_MEM_AXI


  # Create pins
  create_bd_pin -dir I -from 94 -to 0 Din
  create_bd_pin -dir I -type clk adc_clk
  create_bd_pin -dir I adc_control
  create_bd_pin -dir I -type rst adc_resetn
  create_bd_pin -dir I -type clk ddr4_clk
  create_bd_pin -dir I -type rst ddr4_resetn_1
  create_bd_pin -dir I -type clk ps8_clk
  create_bd_pin -dir I -type rst ps8_resetn
  create_bd_pin -dir O -type intr s2mm_introut

  # Create instance: axi_dma_0, and set properties
  set axi_dma_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 axi_dma_0 ]
  set_property -dict [ list \
   CONFIG.c_addr_width {64} \
   CONFIG.c_include_mm2s {0} \
   CONFIG.c_include_s2mm {1} \
   CONFIG.c_include_s2mm_dre {0} \
   CONFIG.c_include_sg {0} \
   CONFIG.c_m_axi_mm2s_data_width {32} \
   CONFIG.c_m_axi_s2mm_data_width {256} \
   CONFIG.c_m_axis_mm2s_tdata_width {32} \
   CONFIG.c_mm2s_burst_size {16} \
   CONFIG.c_s2mm_burst_size {128} \
   CONFIG.c_s_axis_s2mm_tdata_width {128} \
   CONFIG.c_sg_include_stscntrl_strm {0} \
   CONFIG.c_sg_length_width {26} \
 ] $axi_dma_0

  # Create instance: axis_combiner_0, and set properties
  set axis_combiner_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_combiner:1.1 axis_combiner_0 ]

  # Create instance: axis_flow_ctrl_0, and set properties
  set axis_flow_ctrl_0 [ create_bd_cell -type ip -vlnv user.org:user:axis_flow_ctrl:1.0 axis_flow_ctrl_0 ]
  set_property -dict [ list \
   CONFIG.C_AXIS_DWIDTH {128} \
 ] $axis_flow_ctrl_0

  # Create instance: mem
  create_hier_cell_mem $hier_obj mem

  # Create instance: smartconnect_0, and set properties
  set smartconnect_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect:1.0 smartconnect_0 ]
  set_property -dict [ list \
   CONFIG.NUM_MI {2} \
   CONFIG.NUM_SI {1} \
 ] $smartconnect_0

  # Create instance: soft_reset
  create_hier_cell_soft_reset $hier_obj soft_reset

  # Create instance: xlconstant_0, and set properties
  set xlconstant_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_0 ]
  set_property -dict [ list \
   CONFIG.CONST_VAL {0xFFFF} \
   CONFIG.CONST_WIDTH {16} \
 ] $xlconstant_0

  # Create interface connections
  connect_bd_intf_net -intf_net Conn1 [get_bd_intf_pins ADC0_AXIS] [get_bd_intf_pins axis_combiner_0/S00_AXIS]
  connect_bd_intf_net -intf_net Conn2 [get_bd_intf_pins ADC1_AXIS] [get_bd_intf_pins axis_combiner_0/S01_AXIS]
  connect_bd_intf_net -intf_net Conn3 [get_bd_intf_pins FLOW_AXI_LITE] [get_bd_intf_pins axis_flow_ctrl_0/S00_AXI]
  connect_bd_intf_net -intf_net axi_dma_0_M_AXI_S2MM [get_bd_intf_pins axi_dma_0/M_AXI_S2MM] [get_bd_intf_pins smartconnect_0/S00_AXI]
  connect_bd_intf_net -intf_net axis_combiner_0_M_AXIS [get_bd_intf_pins axis_combiner_0/M_AXIS] [get_bd_intf_pins axis_flow_ctrl_0/s_axis]
  connect_bd_intf_net -intf_net axis_data_fifo_1_M_AXIS [get_bd_intf_pins axi_dma_0/S_AXIS_S2MM] [get_bd_intf_pins mem/M_AXIS]
  connect_bd_intf_net -intf_net axis_flow_ctrl_0_m_axis [get_bd_intf_pins axis_flow_ctrl_0/m_axis] [get_bd_intf_pins mem/S_AXIS]
  connect_bd_intf_net -intf_net ps8_axi_periph_M01_AXI [get_bd_intf_pins DMA_AXI_LITE] [get_bd_intf_pins axi_dma_0/S_AXI_LITE]
  connect_bd_intf_net -intf_net smartconnect_0_M00_AXI [get_bd_intf_pins PS_MEM_AXI] [get_bd_intf_pins smartconnect_0/M00_AXI]
  connect_bd_intf_net -intf_net smartconnect_0_M01_AXI [get_bd_intf_pins PL_MEM_AXI] [get_bd_intf_pins smartconnect_0/M01_AXI]

  # Create port connections
  connect_bd_net -net Din_1 [get_bd_pins Din] [get_bd_pins soft_reset/Din]
  connect_bd_net -net aclk_1 [get_bd_pins adc_clk] [get_bd_pins axis_combiner_0/aclk] [get_bd_pins axis_flow_ctrl_0/axis_aclk] [get_bd_pins mem/adc_clk] [get_bd_pins soft_reset/adc_clk]
  connect_bd_net -net adc_control_1 [get_bd_pins adc_control] [get_bd_pins axis_flow_ctrl_0/adc_control]
  connect_bd_net -net aresetn1_1 [get_bd_pins adc_resetn] [get_bd_pins soft_reset/adc_resetn]
  connect_bd_net -net ddr4_0_c0_ddr4_ui_clk [get_bd_pins ddr4_clk] [get_bd_pins axi_dma_0/m_axi_s2mm_aclk] [get_bd_pins mem/ddr4_clk] [get_bd_pins smartconnect_0/aclk] [get_bd_pins soft_reset/ddr4_clk]
  connect_bd_net -net dma_adc_0_s2mm_introut [get_bd_pins s2mm_introut] [get_bd_pins axi_dma_0/s2mm_introut]
  connect_bd_net -net rst_ddr4_200M_peripheral_aresetn [get_bd_pins ddr4_resetn_1] [get_bd_pins smartconnect_0/aresetn] [get_bd_pins soft_reset/ddr4_resetn]
  connect_bd_net -net rst_ps8_100M_peripheral_aresetn [get_bd_pins ps8_resetn] [get_bd_pins axi_dma_0/axi_resetn] [get_bd_pins axis_flow_ctrl_0/s00_axi_aresetn]
  connect_bd_net -net soft_reset_Res [get_bd_pins mem/ddr4_resetn] [get_bd_pins soft_reset/ddr4_sresetn]
  connect_bd_net -net util_vector_logic_1_Res [get_bd_pins axis_combiner_0/aresetn] [get_bd_pins axis_flow_ctrl_0/axis_aresetn] [get_bd_pins mem/adc_resetn] [get_bd_pins soft_reset/adc_sresetn]
  connect_bd_net -net xlconstant_0_dout [get_bd_pins axi_dma_0/s_axis_s2mm_tkeep] [get_bd_pins xlconstant_0/dout]
  connect_bd_net -net zynq_ultra_ps_e_0_pl_clk0 [get_bd_pins ps8_clk] [get_bd_pins axi_dma_0/s_axi_lite_aclk] [get_bd_pins axis_flow_ctrl_0/s00_axi_aclk]

  # Restore current instance
  current_bd_instance $oldCurInst
}


# Procedure to create entire design; Provide argument to make
# procedure reusable. If parentCell is "", will use root.
proc create_root_design { parentCell } {

  variable script_folder
  variable design_name

  if { $parentCell eq "" } {
     set parentCell [get_bd_cells /]
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj


  # Create interface ports
  set adc0_clk [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 adc0_clk ]

  set adc2_clk [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 adc2_clk ]

  set dac0_clk [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 dac0_clk ]

  set dac1_clk [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 dac1_clk ]

  set ddr4_pl [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:ddr4_rtl:1.0 ddr4_pl ]

  set lmk_clk1 [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 lmk_clk1 ]
  set_property -dict [ list \
   CONFIG.FREQ_HZ {122880000} \
   ] $lmk_clk1

  set lmk_clk2 [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 lmk_clk2 ]
  set_property -dict [ list \
   CONFIG.FREQ_HZ {7680000} \
   ] $lmk_clk2

  set sys_clk_ddr4 [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 sys_clk_ddr4 ]
  set_property -dict [ list \
   CONFIG.FREQ_HZ {200000000} \
   ] $sys_clk_ddr4

  set sysref_in [ create_bd_intf_port -mode Slave -vlnv xilinx.com:display_usp_rf_data_converter:diff_pins_rtl:1.0 sysref_in ]

  set vin0_01 [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vin0_01 ]

  set vin0_23 [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vin0_23 ]

  set vin2_01 [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vin2_01 ]

  set vin2_23 [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vin2_23 ]

  set vout00 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vout00 ]

  set vout01 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vout01 ]

  set vout02 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vout02 ]

  set vout03 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vout03 ]

  set vout10 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vout10 ]

  set vout11 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vout11 ]

  set vout12 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vout12 ]

  set vout13 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:diff_analog_io_rtl:1.0 vout13 ]


  # Create ports
  set ddr4_led [ create_bd_port -dir O ddr4_led ]
  set gpio_test [ create_bd_port -dir O -from 0 -to 0 gpio_test ]
  set lmk_rst [ create_bd_port -dir O -from 0 -to 0 lmk_rst ]

  # Create instance: adc_path
  create_hier_cell_adc_path [current_bd_instance .] adc_path

  # Create instance: clocktreeMTS
  create_hier_cell_clocktreeMTS [current_bd_instance .] clocktreeMTS

  # Create instance: dac_path
  create_hier_cell_dac_path [current_bd_instance .] dac_path

  # Create instance: ddr4_0, and set properties
  set ddr4_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:ddr4:2.2 ddr4_0 ]
  set_property -dict [ list \
   CONFIG.C0.BANK_GROUP_WIDTH {1} \
   CONFIG.C0.DDR4_AxiAddressWidth {33} \
   CONFIG.C0.DDR4_AxiDataWidth {512} \
   CONFIG.C0.DDR4_CLKOUT0_DIVIDE {5} \
   CONFIG.C0.DDR4_CasLatency {17} \
   CONFIG.C0.DDR4_CasWriteLatency {12} \
   CONFIG.C0.DDR4_DataWidth {64} \
   CONFIG.C0.DDR4_InputClockPeriod {4998} \
   CONFIG.C0.DDR4_MemoryPart {MT40A1G16RC-062E} \
   CONFIG.C0.DDR4_TimePeriod {833} \
   CONFIG.RESET_BOARD_INTERFACE {Custom} \
   CONFIG.System_Clock {No_Buffer} \
 ] $ddr4_0

  # Create instance: irq_concat, and set properties
  set irq_concat [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 irq_concat ]
  set_property -dict [ list \
   CONFIG.NUM_PORTS {4} \
 ] $irq_concat

  # Create instance: ps8_axi_periph, and set properties
  set ps8_axi_periph [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 ps8_axi_periph ]
  set_property -dict [ list \
   CONFIG.NUM_MI {5} \
 ] $ps8_axi_periph

  # Create instance: reset_block
  create_hier_cell_reset_block [current_bd_instance .] reset_block

  # Create instance: smartconnect_0, and set properties
  set smartconnect_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect:1.0 smartconnect_0 ]
  set_property -dict [ list \
   CONFIG.NUM_SI {3} \
 ] $smartconnect_0

  # Create instance: usp_rf_data_converter_0, and set properties
  set usp_rf_data_converter_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:usp_rf_data_converter:2.6 usp_rf_data_converter_0 ]
  set_property -dict [ list \
   CONFIG.ADC0_Fabric_Freq {245.760} \
   CONFIG.ADC0_Multi_Tile_Sync {true} \
   CONFIG.ADC0_Outclk_Freq {245.760} \
   CONFIG.ADC0_PLL_Enable {false} \
   CONFIG.ADC0_Refclk_Freq {3932.160} \
   CONFIG.ADC0_Sampling_Rate {3.93216} \
   CONFIG.ADC1_Enable {0} \
   CONFIG.ADC1_Fabric_Freq {0.0} \
   CONFIG.ADC1_Multi_Tile_Sync {false} \
   CONFIG.ADC1_Outclk_Freq {15.625} \
   CONFIG.ADC1_Refclk_Freq {2000.000} \
   CONFIG.ADC1_Sampling_Rate {2.0} \
   CONFIG.ADC2_Enable {1} \
   CONFIG.ADC2_Fabric_Freq {245.760} \
   CONFIG.ADC2_Multi_Tile_Sync {true} \
   CONFIG.ADC2_Outclk_Freq {245.760} \
   CONFIG.ADC2_PLL_Enable {false} \
   CONFIG.ADC2_Refclk_Freq {3932.160} \
   CONFIG.ADC2_Sampling_Rate {3.93216} \
   CONFIG.ADC3_Enable {0} \
   CONFIG.ADC3_Fabric_Freq {0.0} \
   CONFIG.ADC3_Multi_Tile_Sync {false} \
   CONFIG.ADC3_Outclk_Freq {15.625} \
   CONFIG.ADC3_Refclk_Freq {2000.000} \
   CONFIG.ADC3_Sampling_Rate {2.0} \
   CONFIG.ADC_Data_Width00 {4} \
   CONFIG.ADC_Data_Width01 {4} \
   CONFIG.ADC_Data_Width02 {4} \
   CONFIG.ADC_Data_Width03 {4} \
   CONFIG.ADC_Data_Width10 {8} \
   CONFIG.ADC_Data_Width11 {8} \
   CONFIG.ADC_Data_Width12 {8} \
   CONFIG.ADC_Data_Width13 {8} \
   CONFIG.ADC_Data_Width20 {4} \
   CONFIG.ADC_Data_Width21 {4} \
   CONFIG.ADC_Data_Width22 {4} \
   CONFIG.ADC_Data_Width23 {4} \
   CONFIG.ADC_Data_Width30 {8} \
   CONFIG.ADC_Data_Width31 {8} \
   CONFIG.ADC_Data_Width32 {8} \
   CONFIG.ADC_Data_Width33 {8} \
   CONFIG.ADC_Decimation_Mode00 {4} \
   CONFIG.ADC_Decimation_Mode01 {4} \
   CONFIG.ADC_Decimation_Mode02 {4} \
   CONFIG.ADC_Decimation_Mode03 {4} \
   CONFIG.ADC_Decimation_Mode10 {0} \
   CONFIG.ADC_Decimation_Mode11 {0} \
   CONFIG.ADC_Decimation_Mode12 {0} \
   CONFIG.ADC_Decimation_Mode13 {0} \
   CONFIG.ADC_Decimation_Mode20 {4} \
   CONFIG.ADC_Decimation_Mode21 {4} \
   CONFIG.ADC_Decimation_Mode22 {4} \
   CONFIG.ADC_Decimation_Mode23 {4} \
   CONFIG.ADC_Decimation_Mode30 {0} \
   CONFIG.ADC_Decimation_Mode31 {0} \
   CONFIG.ADC_Decimation_Mode32 {0} \
   CONFIG.ADC_Decimation_Mode33 {0} \
   CONFIG.ADC_Mixer_Type02 {0} \
   CONFIG.ADC_Mixer_Type03 {0} \
   CONFIG.ADC_Mixer_Type10 {3} \
   CONFIG.ADC_Mixer_Type11 {3} \
   CONFIG.ADC_Mixer_Type12 {3} \
   CONFIG.ADC_Mixer_Type13 {3} \
   CONFIG.ADC_Mixer_Type20 {0} \
   CONFIG.ADC_Mixer_Type21 {0} \
   CONFIG.ADC_Mixer_Type22 {0} \
   CONFIG.ADC_Mixer_Type23 {0} \
   CONFIG.ADC_Mixer_Type30 {3} \
   CONFIG.ADC_Mixer_Type31 {3} \
   CONFIG.ADC_Mixer_Type32 {3} \
   CONFIG.ADC_Mixer_Type33 {3} \
   CONFIG.ADC_OBS02 {false} \
   CONFIG.ADC_OBS12 {false} \
   CONFIG.ADC_OBS22 {false} \
   CONFIG.ADC_OBS32 {false} \
   CONFIG.ADC_RESERVED_1_00 {false} \
   CONFIG.ADC_RESERVED_1_02 {false} \
   CONFIG.ADC_RESERVED_1_10 {false} \
   CONFIG.ADC_RESERVED_1_12 {false} \
   CONFIG.ADC_RESERVED_1_20 {false} \
   CONFIG.ADC_RESERVED_1_22 {false} \
   CONFIG.ADC_RESERVED_1_30 {false} \
   CONFIG.ADC_RESERVED_1_32 {false} \
   CONFIG.ADC_Slice02_Enable {true} \
   CONFIG.ADC_Slice03_Enable {true} \
   CONFIG.ADC_Slice10_Enable {false} \
   CONFIG.ADC_Slice11_Enable {false} \
   CONFIG.ADC_Slice12_Enable {false} \
   CONFIG.ADC_Slice13_Enable {false} \
   CONFIG.ADC_Slice20_Enable {true} \
   CONFIG.ADC_Slice21_Enable {true} \
   CONFIG.ADC_Slice22_Enable {true} \
   CONFIG.ADC_Slice23_Enable {true} \
   CONFIG.ADC_Slice30_Enable {false} \
   CONFIG.ADC_Slice31_Enable {false} \
   CONFIG.ADC_Slice32_Enable {false} \
   CONFIG.ADC_Slice33_Enable {false} \
   CONFIG.DAC0_Enable {1} \
   CONFIG.DAC0_Fabric_Freq {245.760} \
   CONFIG.DAC0_Multi_Tile_Sync {true} \
   CONFIG.DAC0_Outclk_Freq {245.760} \
   CONFIG.DAC0_PLL_Enable {false} \
   CONFIG.DAC0_Refclk_Freq {3932.160} \
   CONFIG.DAC0_Sampling_Rate {3.93216} \
   CONFIG.DAC1_Enable {1} \
   CONFIG.DAC1_Fabric_Freq {245.760} \
   CONFIG.DAC1_Multi_Tile_Sync {true} \
   CONFIG.DAC1_Outclk_Freq {245.760} \
   CONFIG.DAC1_PLL_Enable {false} \
   CONFIG.DAC1_Refclk_Freq {3932.160} \
   CONFIG.DAC1_Sampling_Rate {3.93216} \
   CONFIG.DAC_Data_Width00 {4} \
   CONFIG.DAC_Data_Width01 {4} \
   CONFIG.DAC_Data_Width02 {4} \
   CONFIG.DAC_Data_Width03 {4} \
   CONFIG.DAC_Data_Width10 {4} \
   CONFIG.DAC_Data_Width11 {4} \
   CONFIG.DAC_Data_Width12 {4} \
   CONFIG.DAC_Data_Width13 {4} \
   CONFIG.DAC_Interpolation_Mode00 {4} \
   CONFIG.DAC_Interpolation_Mode01 {4} \
   CONFIG.DAC_Interpolation_Mode02 {4} \
   CONFIG.DAC_Interpolation_Mode03 {4} \
   CONFIG.DAC_Interpolation_Mode10 {4} \
   CONFIG.DAC_Interpolation_Mode11 {4} \
   CONFIG.DAC_Interpolation_Mode12 {4} \
   CONFIG.DAC_Interpolation_Mode13 {4} \
   CONFIG.DAC_Mixer_Type00 {0} \
   CONFIG.DAC_Mixer_Type01 {0} \
   CONFIG.DAC_Mixer_Type02 {0} \
   CONFIG.DAC_Mixer_Type03 {0} \
   CONFIG.DAC_Mixer_Type10 {0} \
   CONFIG.DAC_Mixer_Type11 {0} \
   CONFIG.DAC_Mixer_Type12 {0} \
   CONFIG.DAC_Mixer_Type13 {0} \
   CONFIG.DAC_RESERVED_1_00 {false} \
   CONFIG.DAC_RESERVED_1_01 {false} \
   CONFIG.DAC_RESERVED_1_02 {false} \
   CONFIG.DAC_RESERVED_1_03 {false} \
   CONFIG.DAC_RESERVED_1_10 {false} \
   CONFIG.DAC_RESERVED_1_11 {false} \
   CONFIG.DAC_RESERVED_1_12 {false} \
   CONFIG.DAC_RESERVED_1_13 {false} \
   CONFIG.DAC_Slice00_Enable {true} \
   CONFIG.DAC_Slice01_Enable {true} \
   CONFIG.DAC_Slice02_Enable {true} \
   CONFIG.DAC_Slice03_Enable {true} \
   CONFIG.DAC_Slice10_Enable {true} \
   CONFIG.DAC_Slice11_Enable {true} \
   CONFIG.DAC_Slice12_Enable {true} \
   CONFIG.DAC_Slice13_Enable {true} \
 ] $usp_rf_data_converter_0

  # Create instance: xlconstant_0, and set properties
  set xlconstant_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_0 ]

  # Create instance: xlconstant_1, and set properties
  set xlconstant_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_1 ]

  # Create instance: xlconstant_2, and set properties
  set xlconstant_2 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_2 ]
  set_property -dict [ list \
   CONFIG.CONST_VAL {0} \
   CONFIG.CONST_WIDTH {64} \
 ] $xlconstant_2

  # Create instance: xlslice_0, and set properties
  set xlslice_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {84} \
   CONFIG.DIN_TO {84} \
   CONFIG.DIN_WIDTH {95} \
   CONFIG.DOUT_WIDTH {1} \
 ] $xlslice_0

  # Create instance: xlslice_1, and set properties
  set xlslice_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_1 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {80} \
   CONFIG.DIN_TO {80} \
   CONFIG.DIN_WIDTH {95} \
   CONFIG.DOUT_WIDTH {1} \
 ] $xlslice_1

  # Create instance: zynq_ultra_ps_e_0, and set properties
  set zynq_ultra_ps_e_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:zynq_ultra_ps_e:3.4 zynq_ultra_ps_e_0 ]
  set_property -dict [ list \
   CONFIG.PSU_BANK_0_IO_STANDARD {LVCMOS18} \
   CONFIG.PSU_BANK_1_IO_STANDARD {LVCMOS18} \
   CONFIG.PSU_BANK_2_IO_STANDARD {LVCMOS18} \
   CONFIG.PSU_BANK_3_IO_STANDARD {LVCMOS18} \
   CONFIG.PSU_DDR_RAM_HIGHADDR {0x1FFFFFFFF} \
   CONFIG.PSU_DDR_RAM_HIGHADDR_OFFSET {0x800000000} \
   CONFIG.PSU_DDR_RAM_LOWADDR_OFFSET {0x80000000} \
   CONFIG.PSU_MIO_0_DIRECTION {out} \
   CONFIG.PSU_MIO_0_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_0_POLARITY {Default} \
   CONFIG.PSU_MIO_10_DIRECTION {inout} \
   CONFIG.PSU_MIO_10_POLARITY {Default} \
   CONFIG.PSU_MIO_11_DIRECTION {inout} \
   CONFIG.PSU_MIO_11_POLARITY {Default} \
   CONFIG.PSU_MIO_12_DIRECTION {inout} \
   CONFIG.PSU_MIO_12_POLARITY {Default} \
   CONFIG.PSU_MIO_13_DIRECTION {inout} \
   CONFIG.PSU_MIO_13_POLARITY {Default} \
   CONFIG.PSU_MIO_14_DIRECTION {inout} \
   CONFIG.PSU_MIO_14_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_14_POLARITY {Default} \
   CONFIG.PSU_MIO_14_SLEW {slow} \
   CONFIG.PSU_MIO_15_DIRECTION {inout} \
   CONFIG.PSU_MIO_15_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_15_POLARITY {Default} \
   CONFIG.PSU_MIO_15_SLEW {slow} \
   CONFIG.PSU_MIO_16_DIRECTION {inout} \
   CONFIG.PSU_MIO_16_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_16_POLARITY {Default} \
   CONFIG.PSU_MIO_16_SLEW {slow} \
   CONFIG.PSU_MIO_17_DIRECTION {inout} \
   CONFIG.PSU_MIO_17_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_17_POLARITY {Default} \
   CONFIG.PSU_MIO_17_SLEW {slow} \
   CONFIG.PSU_MIO_18_DIRECTION {in} \
   CONFIG.PSU_MIO_18_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_18_POLARITY {Default} \
   CONFIG.PSU_MIO_18_SLEW {fast} \
   CONFIG.PSU_MIO_19_DIRECTION {out} \
   CONFIG.PSU_MIO_19_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_19_POLARITY {Default} \
   CONFIG.PSU_MIO_1_DIRECTION {in} \
   CONFIG.PSU_MIO_1_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_1_POLARITY {Default} \
   CONFIG.PSU_MIO_1_SLEW {fast} \
   CONFIG.PSU_MIO_20_DIRECTION {inout} \
   CONFIG.PSU_MIO_20_POLARITY {Default} \
   CONFIG.PSU_MIO_21_DIRECTION {inout} \
   CONFIG.PSU_MIO_21_POLARITY {Default} \
   CONFIG.PSU_MIO_22_DIRECTION {inout} \
   CONFIG.PSU_MIO_22_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_22_POLARITY {Default} \
   CONFIG.PSU_MIO_23_DIRECTION {inout} \
   CONFIG.PSU_MIO_23_POLARITY {Default} \
   CONFIG.PSU_MIO_24_DIRECTION {inout} \
   CONFIG.PSU_MIO_24_POLARITY {Default} \
   CONFIG.PSU_MIO_25_DIRECTION {inout} \
   CONFIG.PSU_MIO_25_POLARITY {Default} \
   CONFIG.PSU_MIO_26_DIRECTION {out} \
   CONFIG.PSU_MIO_26_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_26_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_26_POLARITY {Default} \
   CONFIG.PSU_MIO_26_SLEW {slow} \
   CONFIG.PSU_MIO_27_DIRECTION {out} \
   CONFIG.PSU_MIO_27_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_27_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_27_POLARITY {Default} \
   CONFIG.PSU_MIO_27_SLEW {slow} \
   CONFIG.PSU_MIO_28_DIRECTION {out} \
   CONFIG.PSU_MIO_28_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_28_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_28_POLARITY {Default} \
   CONFIG.PSU_MIO_28_SLEW {fast} \
   CONFIG.PSU_MIO_29_DIRECTION {out} \
   CONFIG.PSU_MIO_29_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_29_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_29_POLARITY {Default} \
   CONFIG.PSU_MIO_29_SLEW {slow} \
   CONFIG.PSU_MIO_2_DIRECTION {inout} \
   CONFIG.PSU_MIO_2_POLARITY {Default} \
   CONFIG.PSU_MIO_30_DIRECTION {out} \
   CONFIG.PSU_MIO_30_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_30_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_30_POLARITY {Default} \
   CONFIG.PSU_MIO_30_SLEW {fast} \
   CONFIG.PSU_MIO_31_DIRECTION {out} \
   CONFIG.PSU_MIO_31_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_31_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_31_POLARITY {Default} \
   CONFIG.PSU_MIO_31_SLEW {slow} \
   CONFIG.PSU_MIO_32_DIRECTION {in} \
   CONFIG.PSU_MIO_32_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_32_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_32_POLARITY {Default} \
   CONFIG.PSU_MIO_32_SLEW {fast} \
   CONFIG.PSU_MIO_33_DIRECTION {in} \
   CONFIG.PSU_MIO_33_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_33_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_33_POLARITY {Default} \
   CONFIG.PSU_MIO_33_SLEW {fast} \
   CONFIG.PSU_MIO_34_DIRECTION {in} \
   CONFIG.PSU_MIO_34_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_34_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_34_POLARITY {Default} \
   CONFIG.PSU_MIO_34_SLEW {fast} \
   CONFIG.PSU_MIO_35_DIRECTION {in} \
   CONFIG.PSU_MIO_35_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_35_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_35_POLARITY {Default} \
   CONFIG.PSU_MIO_35_SLEW {fast} \
   CONFIG.PSU_MIO_36_DIRECTION {in} \
   CONFIG.PSU_MIO_36_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_36_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_36_POLARITY {Default} \
   CONFIG.PSU_MIO_36_SLEW {fast} \
   CONFIG.PSU_MIO_37_DIRECTION {in} \
   CONFIG.PSU_MIO_37_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_37_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_37_POLARITY {Default} \
   CONFIG.PSU_MIO_37_SLEW {fast} \
   CONFIG.PSU_MIO_38_DIRECTION {inout} \
   CONFIG.PSU_MIO_38_POLARITY {Default} \
   CONFIG.PSU_MIO_39_DIRECTION {inout} \
   CONFIG.PSU_MIO_39_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_39_POLARITY {Default} \
   CONFIG.PSU_MIO_39_SLEW {slow} \
   CONFIG.PSU_MIO_3_DIRECTION {inout} \
   CONFIG.PSU_MIO_3_POLARITY {Default} \
   CONFIG.PSU_MIO_40_DIRECTION {inout} \
   CONFIG.PSU_MIO_40_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_40_POLARITY {Default} \
   CONFIG.PSU_MIO_40_SLEW {slow} \
   CONFIG.PSU_MIO_41_DIRECTION {inout} \
   CONFIG.PSU_MIO_41_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_41_POLARITY {Default} \
   CONFIG.PSU_MIO_41_SLEW {slow} \
   CONFIG.PSU_MIO_42_DIRECTION {inout} \
   CONFIG.PSU_MIO_42_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_42_POLARITY {Default} \
   CONFIG.PSU_MIO_42_SLEW {slow} \
   CONFIG.PSU_MIO_43_DIRECTION {inout} \
   CONFIG.PSU_MIO_43_POLARITY {Default} \
   CONFIG.PSU_MIO_44_DIRECTION {in} \
   CONFIG.PSU_MIO_44_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_44_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_44_POLARITY {Default} \
   CONFIG.PSU_MIO_44_SLEW {fast} \
   CONFIG.PSU_MIO_45_DIRECTION {in} \
   CONFIG.PSU_MIO_45_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_45_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_45_POLARITY {Default} \
   CONFIG.PSU_MIO_45_SLEW {fast} \
   CONFIG.PSU_MIO_46_DIRECTION {inout} \
   CONFIG.PSU_MIO_46_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_46_POLARITY {Default} \
   CONFIG.PSU_MIO_46_SLEW {slow} \
   CONFIG.PSU_MIO_47_DIRECTION {inout} \
   CONFIG.PSU_MIO_47_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_47_POLARITY {Default} \
   CONFIG.PSU_MIO_47_SLEW {slow} \
   CONFIG.PSU_MIO_48_DIRECTION {inout} \
   CONFIG.PSU_MIO_48_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_48_POLARITY {Default} \
   CONFIG.PSU_MIO_48_SLEW {slow} \
   CONFIG.PSU_MIO_49_DIRECTION {inout} \
   CONFIG.PSU_MIO_49_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_49_POLARITY {Default} \
   CONFIG.PSU_MIO_49_SLEW {slow} \
   CONFIG.PSU_MIO_4_DIRECTION {out} \
   CONFIG.PSU_MIO_4_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_4_POLARITY {Default} \
   CONFIG.PSU_MIO_50_DIRECTION {inout} \
   CONFIG.PSU_MIO_50_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_50_POLARITY {Default} \
   CONFIG.PSU_MIO_50_SLEW {slow} \
   CONFIG.PSU_MIO_51_DIRECTION {out} \
   CONFIG.PSU_MIO_51_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_51_POLARITY {Default} \
   CONFIG.PSU_MIO_51_SLEW {slow} \
   CONFIG.PSU_MIO_52_DIRECTION {in} \
   CONFIG.PSU_MIO_52_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_52_POLARITY {Default} \
   CONFIG.PSU_MIO_52_SLEW {fast} \
   CONFIG.PSU_MIO_53_DIRECTION {in} \
   CONFIG.PSU_MIO_53_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_53_POLARITY {Default} \
   CONFIG.PSU_MIO_53_SLEW {fast} \
   CONFIG.PSU_MIO_54_DIRECTION {inout} \
   CONFIG.PSU_MIO_54_POLARITY {Default} \
   CONFIG.PSU_MIO_55_DIRECTION {in} \
   CONFIG.PSU_MIO_55_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_55_POLARITY {Default} \
   CONFIG.PSU_MIO_55_SLEW {fast} \
   CONFIG.PSU_MIO_56_DIRECTION {inout} \
   CONFIG.PSU_MIO_56_POLARITY {Default} \
   CONFIG.PSU_MIO_57_DIRECTION {inout} \
   CONFIG.PSU_MIO_57_POLARITY {Default} \
   CONFIG.PSU_MIO_58_DIRECTION {out} \
   CONFIG.PSU_MIO_58_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_58_POLARITY {Default} \
   CONFIG.PSU_MIO_59_DIRECTION {inout} \
   CONFIG.PSU_MIO_59_POLARITY {Default} \
   CONFIG.PSU_MIO_5_DIRECTION {out} \
   CONFIG.PSU_MIO_5_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_5_POLARITY {Default} \
   CONFIG.PSU_MIO_60_DIRECTION {inout} \
   CONFIG.PSU_MIO_60_POLARITY {Default} \
   CONFIG.PSU_MIO_61_DIRECTION {inout} \
   CONFIG.PSU_MIO_61_POLARITY {Default} \
   CONFIG.PSU_MIO_62_DIRECTION {inout} \
   CONFIG.PSU_MIO_62_POLARITY {Default} \
   CONFIG.PSU_MIO_63_DIRECTION {inout} \
   CONFIG.PSU_MIO_63_POLARITY {Default} \
   CONFIG.PSU_MIO_64_DIRECTION {in} \
   CONFIG.PSU_MIO_64_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_64_POLARITY {Default} \
   CONFIG.PSU_MIO_64_SLEW {fast} \
   CONFIG.PSU_MIO_65_DIRECTION {in} \
   CONFIG.PSU_MIO_65_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_65_POLARITY {Default} \
   CONFIG.PSU_MIO_65_SLEW {fast} \
   CONFIG.PSU_MIO_66_DIRECTION {inout} \
   CONFIG.PSU_MIO_66_POLARITY {Default} \
   CONFIG.PSU_MIO_67_DIRECTION {in} \
   CONFIG.PSU_MIO_67_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_67_POLARITY {Default} \
   CONFIG.PSU_MIO_67_SLEW {fast} \
   CONFIG.PSU_MIO_68_DIRECTION {inout} \
   CONFIG.PSU_MIO_68_POLARITY {Default} \
   CONFIG.PSU_MIO_69_DIRECTION {inout} \
   CONFIG.PSU_MIO_69_POLARITY {Default} \
   CONFIG.PSU_MIO_6_DIRECTION {inout} \
   CONFIG.PSU_MIO_6_DRIVE_STRENGTH {12} \
   CONFIG.PSU_MIO_6_POLARITY {Default} \
   CONFIG.PSU_MIO_6_SLEW {fast} \
   CONFIG.PSU_MIO_70_DIRECTION {out} \
   CONFIG.PSU_MIO_70_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_70_POLARITY {Default} \
   CONFIG.PSU_MIO_71_DIRECTION {inout} \
   CONFIG.PSU_MIO_71_POLARITY {Default} \
   CONFIG.PSU_MIO_72_DIRECTION {inout} \
   CONFIG.PSU_MIO_72_POLARITY {Default} \
   CONFIG.PSU_MIO_73_DIRECTION {inout} \
   CONFIG.PSU_MIO_73_POLARITY {Default} \
   CONFIG.PSU_MIO_74_DIRECTION {inout} \
   CONFIG.PSU_MIO_74_POLARITY {Default} \
   CONFIG.PSU_MIO_75_DIRECTION {inout} \
   CONFIG.PSU_MIO_75_POLARITY {Default} \
   CONFIG.PSU_MIO_76_DIRECTION {out} \
   CONFIG.PSU_MIO_76_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_76_POLARITY {Default} \
   CONFIG.PSU_MIO_76_SLEW {slow} \
   CONFIG.PSU_MIO_77_DIRECTION {inout} \
   CONFIG.PSU_MIO_77_INPUT_TYPE {schmitt} \
   CONFIG.PSU_MIO_77_POLARITY {Default} \
   CONFIG.PSU_MIO_77_SLEW {slow} \
   CONFIG.PSU_MIO_7_DIRECTION {inout} \
   CONFIG.PSU_MIO_7_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_7_POLARITY {Default} \
   CONFIG.PSU_MIO_8_DIRECTION {out} \
   CONFIG.PSU_MIO_8_INPUT_TYPE {cmos} \
   CONFIG.PSU_MIO_8_POLARITY {Default} \
   CONFIG.PSU_MIO_9_DIRECTION {inout} \
   CONFIG.PSU_MIO_9_POLARITY {Default} \
   CONFIG.PSU_MIO_TREE_PERIPHERALS {\
Quad SPI Flash#Quad SPI Flash#GPIO0 MIO#GPIO0 MIO#Quad SPI Flash#Quad SPI\
Flash#GPIO0 MIO#GPIO0 MIO#USB0 Reset#GPIO0 MIO#GPIO0 MIO#GPIO0 MIO#GPIO0\
MIO#GPIO0 MIO#I2C 0#I2C 0#I2C 1#I2C 1#UART 0#UART 0#GPIO0 MIO#GPIO0 MIO#GPIO0\
MIO#GPIO0 MIO#GPIO0 MIO#GPIO0 MIO#Gem 0#Gem 0#Gem 0#Gem 0#Gem 0#Gem 0#Gem 0#Gem\
0#Gem 0#Gem 0#Gem 0#Gem 0#GPIO1 MIO#SD 1#SD 1#SD 1#SD 1#GPIO1 MIO#SD 1#SD 1#SD\
1#SD 1#SD 1#SD 1#SD 1#SD 1#USB 0#USB 0#USB 0#USB 0#USB 0#USB 0#USB 0#USB 0#USB\
0#USB 0#USB 0#USB 0#USB 1#USB 1#USB 1#USB 1#USB 1#USB 1#USB 1#USB 1#USB 1#USB\
1#USB 1#USB 1#MDIO 0#MDIO 0} \
   CONFIG.PSU_MIO_TREE_SIGNALS {\
sclk_out#miso_mo1#gpio0[2]#gpio0[3]#mosi_mi0#n_ss_out#gpio0[6]#gpio0[7]#reset#gpio0[9]#gpio0[10]#gpio0[11]#gpio0[12]#gpio0[13]#scl_out#sda_out#scl_out#sda_out#rxd#txd#gpio0[20]#gpio0[21]#gpio0[22]#gpio0[23]#gpio0[24]#gpio0[25]#rgmii_tx_clk#rgmii_txd[0]#rgmii_txd[1]#rgmii_txd[2]#rgmii_txd[3]#rgmii_tx_ctl#rgmii_rx_clk#rgmii_rxd[0]#rgmii_rxd[1]#rgmii_rxd[2]#rgmii_rxd[3]#rgmii_rx_ctl#gpio1[38]#sdio1_data_out[4]#sdio1_data_out[5]#sdio1_data_out[6]#sdio1_data_out[7]#gpio1[43]#sdio1_wp#sdio1_cd_n#sdio1_data_out[0]#sdio1_data_out[1]#sdio1_data_out[2]#sdio1_data_out[3]#sdio1_cmd_out#sdio1_clk_out#ulpi_clk_in#ulpi_dir#ulpi_tx_data[2]#ulpi_nxt#ulpi_tx_data[0]#ulpi_tx_data[1]#ulpi_stp#ulpi_tx_data[3]#ulpi_tx_data[4]#ulpi_tx_data[5]#ulpi_tx_data[6]#ulpi_tx_data[7]#ulpi_clk_in#ulpi_dir#ulpi_tx_data[2]#ulpi_nxt#ulpi_tx_data[0]#ulpi_tx_data[1]#ulpi_stp#ulpi_tx_data[3]#ulpi_tx_data[4]#ulpi_tx_data[5]#ulpi_tx_data[6]#ulpi_tx_data[7]#gem0_mdc#gem0_mdio_out} \
   CONFIG.PSU_SD1_INTERNAL_BUS_WIDTH {8} \
   CONFIG.PSU_USB3__DUAL_CLOCK_ENABLE {1} \
   CONFIG.PSU__ACT_DDR_FREQ_MHZ {1199.988037} \
   CONFIG.PSU__CRF_APB__ACPU_CTRL__ACT_FREQMHZ {1199.988037} \
   CONFIG.PSU__CRF_APB__ACPU_CTRL__DIVISOR0 {1} \
   CONFIG.PSU__CRF_APB__ACPU_CTRL__FREQMHZ {1200} \
   CONFIG.PSU__CRF_APB__APLL_CTRL__DIV2 {1} \
   CONFIG.PSU__CRF_APB__APLL_CTRL__FBDIV {72} \
   CONFIG.PSU__CRF_APB__APLL_CTRL__FRACDATA {0.000000} \
   CONFIG.PSU__CRF_APB__APLL_FRAC_CFG__ENABLED {0} \
   CONFIG.PSU__CRF_APB__APLL_TO_LPD_CTRL__DIVISOR0 {3} \
   CONFIG.PSU__CRF_APB__DBG_FPD_CTRL__ACT_FREQMHZ {249.997498} \
   CONFIG.PSU__CRF_APB__DBG_FPD_CTRL__DIVISOR0 {2} \
   CONFIG.PSU__CRF_APB__DBG_TRACE_CTRL__DIVISOR0 {5} \
   CONFIG.PSU__CRF_APB__DBG_TSTMP_CTRL__ACT_FREQMHZ {249.997498} \
   CONFIG.PSU__CRF_APB__DBG_TSTMP_CTRL__DIVISOR0 {2} \
   CONFIG.PSU__CRF_APB__DDR_CTRL__ACT_FREQMHZ {599.994019} \
   CONFIG.PSU__CRF_APB__DDR_CTRL__DIVISOR0 {2} \
   CONFIG.PSU__CRF_APB__DDR_CTRL__FREQMHZ {1200} \
   CONFIG.PSU__CRF_APB__DPDMA_REF_CTRL__ACT_FREQMHZ {599.994019} \
   CONFIG.PSU__CRF_APB__DPDMA_REF_CTRL__DIVISOR0 {2} \
   CONFIG.PSU__CRF_APB__DPLL_CTRL__DIV2 {1} \
   CONFIG.PSU__CRF_APB__DPLL_CTRL__FBDIV {72} \
   CONFIG.PSU__CRF_APB__DPLL_CTRL__FRACDATA {0.000000} \
   CONFIG.PSU__CRF_APB__DPLL_FRAC_CFG__ENABLED {0} \
   CONFIG.PSU__CRF_APB__DPLL_TO_LPD_CTRL__DIVISOR0 {3} \
   CONFIG.PSU__CRF_APB__DP_AUDIO_REF_CTRL__ACT_FREQMHZ {24.999750} \
   CONFIG.PSU__CRF_APB__DP_AUDIO_REF_CTRL__DIVISOR0 {63} \
   CONFIG.PSU__CRF_APB__DP_AUDIO_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRF_APB__DP_AUDIO__FRAC_ENABLED {0} \
   CONFIG.PSU__CRF_APB__DP_STC_REF_CTRL__ACT_FREQMHZ {26.922808} \
   CONFIG.PSU__CRF_APB__DP_STC_REF_CTRL__DIVISOR0 {6} \
   CONFIG.PSU__CRF_APB__DP_STC_REF_CTRL__DIVISOR1 {10} \
   CONFIG.PSU__CRF_APB__DP_VIDEO_REF_CTRL__ACT_FREQMHZ {299.997009} \
   CONFIG.PSU__CRF_APB__DP_VIDEO_REF_CTRL__DIVISOR0 {5} \
   CONFIG.PSU__CRF_APB__DP_VIDEO_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRF_APB__DP_VIDEO__FRAC_ENABLED {0} \
   CONFIG.PSU__CRF_APB__GDMA_REF_CTRL__ACT_FREQMHZ {599.994019} \
   CONFIG.PSU__CRF_APB__GDMA_REF_CTRL__DIVISOR0 {2} \
   CONFIG.PSU__CRF_APB__GPU_REF_CTRL__DIVISOR0 {3} \
   CONFIG.PSU__CRF_APB__PCIE_REF_CTRL__DIVISOR0 {6} \
   CONFIG.PSU__CRF_APB__SATA_REF_CTRL__DIVISOR0 {5} \
   CONFIG.PSU__CRF_APB__TOPSW_LSBUS_CTRL__ACT_FREQMHZ {99.999001} \
   CONFIG.PSU__CRF_APB__TOPSW_LSBUS_CTRL__DIVISOR0 {5} \
   CONFIG.PSU__CRF_APB__TOPSW_MAIN_CTRL__ACT_FREQMHZ {533.328003} \
   CONFIG.PSU__CRF_APB__TOPSW_MAIN_CTRL__DIVISOR0 {2} \
   CONFIG.PSU__CRF_APB__VPLL_CTRL__DIV2 {1} \
   CONFIG.PSU__CRF_APB__VPLL_CTRL__FBDIV {64} \
   CONFIG.PSU__CRF_APB__VPLL_CTRL__FRACDATA {0.000000} \
   CONFIG.PSU__CRF_APB__VPLL_FRAC_CFG__ENABLED {0} \
   CONFIG.PSU__CRF_APB__VPLL_TO_LPD_CTRL__DIVISOR0 {2} \
   CONFIG.PSU__CRL_APB__ADMA_REF_CTRL__ACT_FREQMHZ {533.328003} \
   CONFIG.PSU__CRL_APB__ADMA_REF_CTRL__DIVISOR0 {2} \
   CONFIG.PSU__CRL_APB__AFI6_REF_CTRL__DIVISOR0 {3} \
   CONFIG.PSU__CRL_APB__AMS_REF_CTRL__ACT_FREQMHZ {49.999500} \
   CONFIG.PSU__CRL_APB__AMS_REF_CTRL__DIVISOR0 {30} \
   CONFIG.PSU__CRL_APB__AMS_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__CAN0_REF_CTRL__DIVISOR0 {15} \
   CONFIG.PSU__CRL_APB__CAN0_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__CAN1_REF_CTRL__DIVISOR0 {15} \
   CONFIG.PSU__CRL_APB__CAN1_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__CPU_R5_CTRL__ACT_FREQMHZ {499.994995} \
   CONFIG.PSU__CRL_APB__CPU_R5_CTRL__DIVISOR0 {3} \
   CONFIG.PSU__CRL_APB__CPU_R5_CTRL__FREQMHZ {500} \
   CONFIG.PSU__CRL_APB__CPU_R5_CTRL__SRCSEL {IOPLL} \
   CONFIG.PSU__CRL_APB__DBG_LPD_CTRL__ACT_FREQMHZ {249.997498} \
   CONFIG.PSU__CRL_APB__DBG_LPD_CTRL__DIVISOR0 {6} \
   CONFIG.PSU__CRL_APB__DLL_REF_CTRL__ACT_FREQMHZ {1499.984985} \
   CONFIG.PSU__CRL_APB__GEM0_REF_CTRL__ACT_FREQMHZ {124.998749} \
   CONFIG.PSU__CRL_APB__GEM0_REF_CTRL__DIVISOR0 {12} \
   CONFIG.PSU__CRL_APB__GEM0_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__GEM1_REF_CTRL__DIVISOR0 {12} \
   CONFIG.PSU__CRL_APB__GEM1_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__GEM2_REF_CTRL__DIVISOR0 {12} \
   CONFIG.PSU__CRL_APB__GEM2_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__GEM3_REF_CTRL__DIVISOR0 {12} \
   CONFIG.PSU__CRL_APB__GEM3_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__GEM_TSU_REF_CTRL__ACT_FREQMHZ {249.997498} \
   CONFIG.PSU__CRL_APB__GEM_TSU_REF_CTRL__DIVISOR0 {6} \
   CONFIG.PSU__CRL_APB__GEM_TSU_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__GEM_TSU_REF_CTRL__SRCSEL {IOPLL} \
   CONFIG.PSU__CRL_APB__I2C0_REF_CTRL__ACT_FREQMHZ {99.999001} \
   CONFIG.PSU__CRL_APB__I2C0_REF_CTRL__DIVISOR0 {15} \
   CONFIG.PSU__CRL_APB__I2C0_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__I2C1_REF_CTRL__ACT_FREQMHZ {99.999001} \
   CONFIG.PSU__CRL_APB__I2C1_REF_CTRL__DIVISOR0 {15} \
   CONFIG.PSU__CRL_APB__I2C1_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__IOPLL_CTRL__DIV2 {1} \
   CONFIG.PSU__CRL_APB__IOPLL_CTRL__FBDIV {90} \
   CONFIG.PSU__CRL_APB__IOPLL_CTRL__FRACDATA {0.000000} \
   CONFIG.PSU__CRL_APB__IOPLL_FRAC_CFG__ENABLED {0} \
   CONFIG.PSU__CRL_APB__IOPLL_TO_FPD_CTRL__DIVISOR0 {3} \
   CONFIG.PSU__CRL_APB__IOU_SWITCH_CTRL__ACT_FREQMHZ {266.664001} \
   CONFIG.PSU__CRL_APB__IOU_SWITCH_CTRL__DIVISOR0 {4} \
   CONFIG.PSU__CRL_APB__LPD_LSBUS_CTRL__ACT_FREQMHZ {99.999001} \
   CONFIG.PSU__CRL_APB__LPD_LSBUS_CTRL__DIVISOR0 {15} \
   CONFIG.PSU__CRL_APB__LPD_SWITCH_CTRL__ACT_FREQMHZ {533.328003} \
   CONFIG.PSU__CRL_APB__LPD_SWITCH_CTRL__DIVISOR0 {2} \
   CONFIG.PSU__CRL_APB__NAND_REF_CTRL__DIVISOR0 {15} \
   CONFIG.PSU__CRL_APB__NAND_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__PCAP_CTRL__ACT_FREQMHZ {187.498123} \
   CONFIG.PSU__CRL_APB__PCAP_CTRL__DIVISOR0 {8} \
   CONFIG.PSU__CRL_APB__PL0_REF_CTRL__ACT_FREQMHZ {99.999001} \
   CONFIG.PSU__CRL_APB__PL0_REF_CTRL__DIVISOR0 {15} \
   CONFIG.PSU__CRL_APB__PL0_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__PL0_REF_CTRL__SRCSEL {IOPLL} \
   CONFIG.PSU__CRL_APB__PL1_REF_CTRL__ACT_FREQMHZ {99.999001} \
   CONFIG.PSU__CRL_APB__PL1_REF_CTRL__DIVISOR0 {4} \
   CONFIG.PSU__CRL_APB__PL1_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__PL1_REF_CTRL__FREQMHZ {100} \
   CONFIG.PSU__CRL_APB__PL1_REF_CTRL__SRCSEL {RPLL} \
   CONFIG.PSU__CRL_APB__PL2_REF_CTRL__ACT_FREQMHZ {99.999001} \
   CONFIG.PSU__CRL_APB__PL2_REF_CTRL__DIVISOR0 {4} \
   CONFIG.PSU__CRL_APB__PL2_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__PL2_REF_CTRL__FREQMHZ {100} \
   CONFIG.PSU__CRL_APB__PL2_REF_CTRL__SRCSEL {RPLL} \
   CONFIG.PSU__CRL_APB__PL3_REF_CTRL__ACT_FREQMHZ {99.999001} \
   CONFIG.PSU__CRL_APB__PL3_REF_CTRL__DIVISOR0 {4} \
   CONFIG.PSU__CRL_APB__PL3_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__PL3_REF_CTRL__FREQMHZ {100} \
   CONFIG.PSU__CRL_APB__PL3_REF_CTRL__SRCSEL {RPLL} \
   CONFIG.PSU__CRL_APB__QSPI_REF_CTRL__ACT_FREQMHZ {299.997009} \
   CONFIG.PSU__CRL_APB__QSPI_REF_CTRL__DIVISOR0 {5} \
   CONFIG.PSU__CRL_APB__QSPI_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__RPLL_CTRL__DIV2 {1} \
   CONFIG.PSU__CRL_APB__RPLL_CTRL__FBDIV {64} \
   CONFIG.PSU__CRL_APB__RPLL_CTRL__FRACDATA {0.000000} \
   CONFIG.PSU__CRL_APB__RPLL_FRAC_CFG__ENABLED {0} \
   CONFIG.PSU__CRL_APB__RPLL_TO_FPD_CTRL__DIVISOR0 {2} \
   CONFIG.PSU__CRL_APB__SDIO0_REF_CTRL__DIVISOR0 {7} \
   CONFIG.PSU__CRL_APB__SDIO0_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__SDIO1_REF_CTRL__ACT_FREQMHZ {187.498123} \
   CONFIG.PSU__CRL_APB__SDIO1_REF_CTRL__DIVISOR0 {8} \
   CONFIG.PSU__CRL_APB__SDIO1_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__SDIO1_REF_CTRL__SRCSEL {IOPLL} \
   CONFIG.PSU__CRL_APB__SPI0_REF_CTRL__DIVISOR0 {7} \
   CONFIG.PSU__CRL_APB__SPI0_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__SPI1_REF_CTRL__DIVISOR0 {7} \
   CONFIG.PSU__CRL_APB__SPI1_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__TIMESTAMP_REF_CTRL__ACT_FREQMHZ {33.333000} \
   CONFIG.PSU__CRL_APB__TIMESTAMP_REF_CTRL__DIVISOR0 {1} \
   CONFIG.PSU__CRL_APB__UART0_REF_CTRL__ACT_FREQMHZ {99.999001} \
   CONFIG.PSU__CRL_APB__UART0_REF_CTRL__DIVISOR0 {15} \
   CONFIG.PSU__CRL_APB__UART0_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__UART1_REF_CTRL__DIVISOR0 {15} \
   CONFIG.PSU__CRL_APB__UART1_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__USB0_BUS_REF_CTRL__ACT_FREQMHZ {249.997498} \
   CONFIG.PSU__CRL_APB__USB0_BUS_REF_CTRL__DIVISOR0 {6} \
   CONFIG.PSU__CRL_APB__USB0_BUS_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__USB1_BUS_REF_CTRL__ACT_FREQMHZ {249.997498} \
   CONFIG.PSU__CRL_APB__USB1_BUS_REF_CTRL__DIVISOR0 {6} \
   CONFIG.PSU__CRL_APB__USB1_BUS_REF_CTRL__DIVISOR1 {1} \
   CONFIG.PSU__CRL_APB__USB3_DUAL_REF_CTRL__ACT_FREQMHZ {19.999800} \
   CONFIG.PSU__CRL_APB__USB3_DUAL_REF_CTRL__DIVISOR0 {25} \
   CONFIG.PSU__CRL_APB__USB3_DUAL_REF_CTRL__DIVISOR1 {3} \
   CONFIG.PSU__CRL_APB__USB3__ENABLE {1} \
   CONFIG.PSU__DDRC__BG_ADDR_COUNT {1} \
   CONFIG.PSU__DDRC__CL {16} \
   CONFIG.PSU__DDRC__CWL {12} \
   CONFIG.PSU__DDRC__DEVICE_CAPACITY {16384 MBits} \
   CONFIG.PSU__DDRC__DRAM_WIDTH {16 Bits} \
   CONFIG.PSU__DDRC__ROW_ADDR_COUNT {17} \
   CONFIG.PSU__DDRC__SB_TARGET {16-16-16} \
   CONFIG.PSU__DDRC__SPEED_BIN {DDR4_2400R} \
   CONFIG.PSU__DDRC__T_FAW {30.0} \
   CONFIG.PSU__DDRC__T_RAS_MIN {32.0} \
   CONFIG.PSU__DDRC__T_RC {45.32} \
   CONFIG.PSU__DDRC__T_RCD {16} \
   CONFIG.PSU__DDRC__T_RP {16} \
   CONFIG.PSU__DDR_HIGH_ADDRESS_GUI_ENABLE {1} \
   CONFIG.PSU__DDR__INTERFACE__FREQMHZ {600.000} \
   CONFIG.PSU__DISPLAYPORT__LANE0__ENABLE {0} \
   CONFIG.PSU__DISPLAYPORT__LANE1__ENABLE {0} \
   CONFIG.PSU__DISPLAYPORT__PERIPHERAL__ENABLE {0} \
   CONFIG.PSU__DLL__ISUSED {1} \
   CONFIG.PSU__DPAUX__PERIPHERAL__ENABLE {0} \
   CONFIG.PSU__ENET0__FIFO__ENABLE {0} \
   CONFIG.PSU__ENET0__GRP_MDIO__ENABLE {1} \
   CONFIG.PSU__ENET0__GRP_MDIO__IO {MIO 76 .. 77} \
   CONFIG.PSU__ENET0__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__ENET0__PERIPHERAL__IO {MIO 26 .. 37} \
   CONFIG.PSU__ENET0__PTP__ENABLE {0} \
   CONFIG.PSU__ENET0__TSU__ENABLE {0} \
   CONFIG.PSU__FPGA_PL1_ENABLE {0} \
   CONFIG.PSU__FPGA_PL2_ENABLE {0} \
   CONFIG.PSU__FPGA_PL3_ENABLE {0} \
   CONFIG.PSU__GEM0_COHERENCY {0} \
   CONFIG.PSU__GEM0_ROUTE_THROUGH_FPD {0} \
   CONFIG.PSU__GEM__TSU__ENABLE {0} \
   CONFIG.PSU__GPIO0_MIO__IO {MIO 0 .. 25} \
   CONFIG.PSU__GPIO0_MIO__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__GPIO1_MIO__IO {MIO 26 .. 51} \
   CONFIG.PSU__GPIO1_MIO__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__GPIO_EMIO_WIDTH {95} \
   CONFIG.PSU__GPIO_EMIO__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__GPIO_EMIO__PERIPHERAL__IO {95} \
   CONFIG.PSU__GT__PRE_EMPH_LVL_4 {} \
   CONFIG.PSU__GT__VLT_SWNG_LVL_4 {} \
   CONFIG.PSU__HIGH_ADDRESS__ENABLE {1} \
   CONFIG.PSU__I2C0__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__I2C0__PERIPHERAL__IO {MIO 14 .. 15} \
   CONFIG.PSU__I2C1__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__I2C1__PERIPHERAL__IO {MIO 16 .. 17} \
   CONFIG.PSU__LPD_SLCR__CSUPMU__ACT_FREQMHZ {100} \
   CONFIG.PSU__LPD_SLCR__CSUPMU__FREQMHZ {100} \
   CONFIG.PSU__MAXIGP0__DATA_WIDTH {128} \
   CONFIG.PSU__MAXIGP1__DATA_WIDTH {128} \
   CONFIG.PSU__MAXIGP2__DATA_WIDTH {32} \
   CONFIG.PSU__OVERRIDE__BASIC_CLOCK {0} \
   CONFIG.PSU__PL_CLK1_BUF {FALSE} \
   CONFIG.PSU__PL_CLK2_BUF {FALSE} \
   CONFIG.PSU__PL_CLK3_BUF {FALSE} \
   CONFIG.PSU__PMU_COHERENCY {0} \
   CONFIG.PSU__PMU__AIBACK__ENABLE {0} \
   CONFIG.PSU__PMU__EMIO_GPI__ENABLE {0} \
   CONFIG.PSU__PMU__EMIO_GPO__ENABLE {0} \
   CONFIG.PSU__PMU__GPI0__ENABLE {0} \
   CONFIG.PSU__PMU__GPI1__ENABLE {0} \
   CONFIG.PSU__PMU__GPI2__ENABLE {0} \
   CONFIG.PSU__PMU__GPI3__ENABLE {0} \
   CONFIG.PSU__PMU__GPI4__ENABLE {0} \
   CONFIG.PSU__PMU__GPI5__ENABLE {0} \
   CONFIG.PSU__PMU__GPO0__ENABLE {0} \
   CONFIG.PSU__PMU__GPO1__ENABLE {0} \
   CONFIG.PSU__PMU__GPO2__ENABLE {0} \
   CONFIG.PSU__PMU__GPO3__ENABLE {0} \
   CONFIG.PSU__PMU__GPO4__ENABLE {0} \
   CONFIG.PSU__PMU__GPO5__ENABLE {0} \
   CONFIG.PSU__PMU__PERIPHERAL__ENABLE {0} \
   CONFIG.PSU__PMU__PLERROR__ENABLE {0} \
   CONFIG.PSU__PROTECTION__MASTERS {\
USB1:NonSecure;1|USB0:NonSecure;1|S_AXI_LPD:NA;0|S_AXI_HPC1_FPD:NA;0|S_AXI_HPC0_FPD:NA;0|S_AXI_HP3_FPD:NA;0|S_AXI_HP2_FPD:NA;0|S_AXI_HP1_FPD:NA;1|S_AXI_HP0_FPD:NA;1|S_AXI_ACP:NA;0|S_AXI_ACE:NA;0|SD1:NonSecure;1|SD0:NonSecure;0|SATA1:NonSecure;0|SATA0:NonSecure;0|RPU1:Secure;1|RPU0:Secure;1|QSPI:NonSecure;1|PMU:NA;1|PCIe:NonSecure;0|NAND:NonSecure;0|LDMA:NonSecure;1|GPU:NonSecure;1|GEM3:NonSecure;0|GEM2:NonSecure;0|GEM1:NonSecure;0|GEM0:NonSecure;1|FDMA:NonSecure;1|DP:NonSecure;0|DAP:NA;1|Coresight:NA;1|CSU:NA;1|APU:NA;1} \
   CONFIG.PSU__PROTECTION__SLAVES {\
LPD;USB3_1_XHCI;FE300000;FE3FFFFF;1|LPD;USB3_1;FF9E0000;FF9EFFFF;1|LPD;USB3_0_XHCI;FE200000;FE2FFFFF;1|LPD;USB3_0;FF9D0000;FF9DFFFF;1|LPD;UART1;FF010000;FF01FFFF;0|LPD;UART0;FF000000;FF00FFFF;1|LPD;TTC3;FF140000;FF14FFFF;0|LPD;TTC2;FF130000;FF13FFFF;0|LPD;TTC1;FF120000;FF12FFFF;0|LPD;TTC0;FF110000;FF11FFFF;0|FPD;SWDT1;FD4D0000;FD4DFFFF;0|LPD;SWDT0;FF150000;FF15FFFF;0|LPD;SPI1;FF050000;FF05FFFF;0|LPD;SPI0;FF040000;FF04FFFF;0|FPD;SMMU_REG;FD5F0000;FD5FFFFF;1|FPD;SMMU;FD800000;FDFFFFFF;1|FPD;SIOU;FD3D0000;FD3DFFFF;1|FPD;SERDES;FD400000;FD47FFFF;1|LPD;SD1;FF170000;FF17FFFF;1|LPD;SD0;FF160000;FF16FFFF;0|FPD;SATA;FD0C0000;FD0CFFFF;0|LPD;RTC;FFA60000;FFA6FFFF;1|LPD;RSA_CORE;FFCE0000;FFCEFFFF;1|LPD;RPU;FF9A0000;FF9AFFFF;1|LPD;R5_TCM_RAM_GLOBAL;FFE00000;FFE3FFFF;1|LPD;R5_1_Instruction_Cache;FFEC0000;FFECFFFF;1|LPD;R5_1_Data_Cache;FFED0000;FFEDFFFF;1|LPD;R5_1_BTCM_GLOBAL;FFEB0000;FFEBFFFF;1|LPD;R5_1_ATCM_GLOBAL;FFE90000;FFE9FFFF;1|LPD;R5_0_Instruction_Cache;FFE40000;FFE4FFFF;1|LPD;R5_0_Data_Cache;FFE50000;FFE5FFFF;1|LPD;R5_0_BTCM_GLOBAL;FFE20000;FFE2FFFF;1|LPD;R5_0_ATCM_GLOBAL;FFE00000;FFE0FFFF;1|LPD;QSPI_Linear_Address;C0000000;DFFFFFFF;1|LPD;QSPI;FF0F0000;FF0FFFFF;1|LPD;PMU_RAM;FFDC0000;FFDDFFFF;1|LPD;PMU_GLOBAL;FFD80000;FFDBFFFF;1|FPD;PCIE_MAIN;FD0E0000;FD0EFFFF;0|FPD;PCIE_LOW;E0000000;EFFFFFFF;0|FPD;PCIE_HIGH2;8000000000;BFFFFFFFFF;0|FPD;PCIE_HIGH1;600000000;7FFFFFFFF;0|FPD;PCIE_DMA;FD0F0000;FD0FFFFF;0|FPD;PCIE_ATTRIB;FD480000;FD48FFFF;0|LPD;OCM_XMPU_CFG;FFA70000;FFA7FFFF;1|LPD;OCM_SLCR;FF960000;FF96FFFF;1|OCM;OCM;FFFC0000;FFFFFFFF;1|LPD;NAND;FF100000;FF10FFFF;0|LPD;MBISTJTAG;FFCF0000;FFCFFFFF;1|LPD;LPD_XPPU_SINK;FF9C0000;FF9CFFFF;1|LPD;LPD_XPPU;FF980000;FF98FFFF;1|LPD;LPD_SLCR_SECURE;FF4B0000;FF4DFFFF;1|LPD;LPD_SLCR;FF410000;FF4AFFFF;1|LPD;LPD_GPV;FE100000;FE1FFFFF;1|LPD;LPD_DMA_7;FFAF0000;FFAFFFFF;1|LPD;LPD_DMA_6;FFAE0000;FFAEFFFF;1|LPD;LPD_DMA_5;FFAD0000;FFADFFFF;1|LPD;LPD_DMA_4;FFAC0000;FFACFFFF;1|LPD;LPD_DMA_3;FFAB0000;FFABFFFF;1|LPD;LPD_DMA_2;FFAA0000;FFAAFFFF;1|LPD;LPD_DMA_1;FFA90000;FFA9FFFF;1|LPD;LPD_DMA_0;FFA80000;FFA8FFFF;1|LPD;IPI_CTRL;FF380000;FF3FFFFF;1|LPD;IOU_SLCR;FF180000;FF23FFFF;1|LPD;IOU_SECURE_SLCR;FF240000;FF24FFFF;1|LPD;IOU_SCNTRS;FF260000;FF26FFFF;1|LPD;IOU_SCNTR;FF250000;FF25FFFF;1|LPD;IOU_GPV;FE000000;FE0FFFFF;1|LPD;I2C1;FF030000;FF03FFFF;1|LPD;I2C0;FF020000;FF02FFFF;1|FPD;GPU;FD4B0000;FD4BFFFF;0|LPD;GPIO;FF0A0000;FF0AFFFF;1|LPD;GEM3;FF0E0000;FF0EFFFF;0|LPD;GEM2;FF0D0000;FF0DFFFF;0|LPD;GEM1;FF0C0000;FF0CFFFF;0|LPD;GEM0;FF0B0000;FF0BFFFF;1|FPD;FPD_XMPU_SINK;FD4F0000;FD4FFFFF;1|FPD;FPD_XMPU_CFG;FD5D0000;FD5DFFFF;1|FPD;FPD_SLCR_SECURE;FD690000;FD6CFFFF;1|FPD;FPD_SLCR;FD610000;FD68FFFF;1|FPD;FPD_DMA_CH7;FD570000;FD57FFFF;1|FPD;FPD_DMA_CH6;FD560000;FD56FFFF;1|FPD;FPD_DMA_CH5;FD550000;FD55FFFF;1|FPD;FPD_DMA_CH4;FD540000;FD54FFFF;1|FPD;FPD_DMA_CH3;FD530000;FD53FFFF;1|FPD;FPD_DMA_CH2;FD520000;FD52FFFF;1|FPD;FPD_DMA_CH1;FD510000;FD51FFFF;1|FPD;FPD_DMA_CH0;FD500000;FD50FFFF;1|LPD;EFUSE;FFCC0000;FFCCFFFF;1|FPD;Display\
Port;FD4A0000;FD4AFFFF;0|FPD;DPDMA;FD4C0000;FD4CFFFF;0|FPD;DDR_XMPU5_CFG;FD050000;FD05FFFF;1|FPD;DDR_XMPU4_CFG;FD040000;FD04FFFF;1|FPD;DDR_XMPU3_CFG;FD030000;FD03FFFF;1|FPD;DDR_XMPU2_CFG;FD020000;FD02FFFF;1|FPD;DDR_XMPU1_CFG;FD010000;FD01FFFF;1|FPD;DDR_XMPU0_CFG;FD000000;FD00FFFF;1|FPD;DDR_QOS_CTRL;FD090000;FD09FFFF;1|FPD;DDR_PHY;FD080000;FD08FFFF;1|DDR;DDR_LOW;0;7FFFFFFF;1|DDR;DDR_HIGH;800000000;97FFFFFFF;1|FPD;DDDR_CTRL;FD070000;FD070FFF;1|LPD;Coresight;FE800000;FEFFFFFF;1|LPD;CSU_DMA;FFC80000;FFC9FFFF;1|LPD;CSU;FFCA0000;FFCAFFFF;1|LPD;CRL_APB;FF5E0000;FF85FFFF;1|FPD;CRF_APB;FD1A0000;FD2DFFFF;1|FPD;CCI_REG;FD5E0000;FD5EFFFF;1|LPD;CAN1;FF070000;FF07FFFF;0|LPD;CAN0;FF060000;FF06FFFF;0|FPD;APU;FD5C0000;FD5CFFFF;1|LPD;APM_INTC_IOU;FFA20000;FFA2FFFF;1|LPD;APM_FPD_LPD;FFA30000;FFA3FFFF;1|FPD;APM_5;FD490000;FD49FFFF;1|FPD;APM_0;FD0B0000;FD0BFFFF;1|LPD;APM2;FFA10000;FFA1FFFF;1|LPD;APM1;FFA00000;FFA0FFFF;1|LPD;AMS;FFA50000;FFA5FFFF;1|FPD;AFI_5;FD3B0000;FD3BFFFF;1|FPD;AFI_4;FD3A0000;FD3AFFFF;1|FPD;AFI_3;FD390000;FD39FFFF;1|FPD;AFI_2;FD380000;FD38FFFF;1|FPD;AFI_1;FD370000;FD37FFFF;1|FPD;AFI_0;FD360000;FD36FFFF;1|LPD;AFIFM6;FF9B0000;FF9BFFFF;1|FPD;ACPU_GIC;F9010000;F907FFFF;1} \
   CONFIG.PSU__QSPI_COHERENCY {0} \
   CONFIG.PSU__QSPI_ROUTE_THROUGH_FPD {0} \
   CONFIG.PSU__QSPI__GRP_FBCLK__ENABLE {0} \
   CONFIG.PSU__QSPI__PERIPHERAL__DATA_MODE {x1} \
   CONFIG.PSU__QSPI__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__QSPI__PERIPHERAL__IO {MIO 0 .. 5} \
   CONFIG.PSU__QSPI__PERIPHERAL__MODE {Single} \
   CONFIG.PSU__SAXIGP2__DATA_WIDTH {128} \
   CONFIG.PSU__SAXIGP3__DATA_WIDTH {128} \
   CONFIG.PSU__SD1_COHERENCY {0} \
   CONFIG.PSU__SD1_ROUTE_THROUGH_FPD {0} \
   CONFIG.PSU__SD1__CLK_100_SDR_OTAP_DLY {0x3} \
   CONFIG.PSU__SD1__CLK_200_SDR_OTAP_DLY {0x3} \
   CONFIG.PSU__SD1__CLK_50_DDR_ITAP_DLY {0x3D} \
   CONFIG.PSU__SD1__CLK_50_DDR_OTAP_DLY {0x4} \
   CONFIG.PSU__SD1__CLK_50_SDR_ITAP_DLY {0x15} \
   CONFIG.PSU__SD1__CLK_50_SDR_OTAP_DLY {0x5} \
   CONFIG.PSU__SD1__DATA_TRANSFER_MODE {8Bit} \
   CONFIG.PSU__SD1__GRP_CD__ENABLE {1} \
   CONFIG.PSU__SD1__GRP_CD__IO {MIO 45} \
   CONFIG.PSU__SD1__GRP_POW__ENABLE {0} \
   CONFIG.PSU__SD1__GRP_WP__ENABLE {1} \
   CONFIG.PSU__SD1__GRP_WP__IO {MIO 44} \
   CONFIG.PSU__SD1__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__SD1__PERIPHERAL__IO {MIO 39 .. 51} \
   CONFIG.PSU__SD1__RESET__ENABLE {0} \
   CONFIG.PSU__SD1__SLOT_TYPE {SD 3.0} \
   CONFIG.PSU__TSU__BUFG_PORT_PAIR {0} \
   CONFIG.PSU__UART0__BAUD_RATE {115200} \
   CONFIG.PSU__UART0__MODEM__ENABLE {0} \
   CONFIG.PSU__UART0__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__UART0__PERIPHERAL__IO {MIO 18 .. 19} \
   CONFIG.PSU__USB0_COHERENCY {0} \
   CONFIG.PSU__USB0__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__USB0__PERIPHERAL__IO {MIO 52 .. 63} \
   CONFIG.PSU__USB0__REF_CLK_FREQ {100} \
   CONFIG.PSU__USB0__REF_CLK_SEL {Ref Clk3} \
   CONFIG.PSU__USB0__RESET__ENABLE {1} \
   CONFIG.PSU__USB0__RESET__IO {MIO 8} \
   CONFIG.PSU__USB1_COHERENCY {0} \
   CONFIG.PSU__USB1__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__USB1__PERIPHERAL__IO {MIO 64 .. 75} \
   CONFIG.PSU__USB1__REF_CLK_FREQ {100} \
   CONFIG.PSU__USB1__REF_CLK_SEL {Ref Clk3} \
   CONFIG.PSU__USB1__RESET__ENABLE {0} \
   CONFIG.PSU__USB2_0__EMIO__ENABLE {0} \
   CONFIG.PSU__USB2_1__EMIO__ENABLE {0} \
   CONFIG.PSU__USB3_0__EMIO__ENABLE {0} \
   CONFIG.PSU__USB3_0__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__USB3_0__PERIPHERAL__IO {GT Lane0} \
   CONFIG.PSU__USB3_1__EMIO__ENABLE {0} \
   CONFIG.PSU__USB3_1__PERIPHERAL__ENABLE {1} \
   CONFIG.PSU__USB3_1__PERIPHERAL__IO {GT Lane3} \
   CONFIG.PSU__USB__RESET__MODE {Shared MIO Pin} \
   CONFIG.PSU__USB__RESET__POLARITY {Active Low} \
   CONFIG.PSU__USE__IRQ0 {1} \
   CONFIG.PSU__USE__M_AXI_GP0 {1} \
   CONFIG.PSU__USE__M_AXI_GP1 {1} \
   CONFIG.PSU__USE__M_AXI_GP2 {0} \
   CONFIG.PSU__USE__S_AXI_GP2 {1} \
   CONFIG.PSU__USE__S_AXI_GP3 {1} \
   CONFIG.SUBPRESET1 {Custom} \
 ] $zynq_ultra_ps_e_0

  # Create interface connections
  connect_bd_intf_net -intf_net S00_AXI_1 [get_bd_intf_pins ps8_axi_periph/S00_AXI] [get_bd_intf_pins zynq_ultra_ps_e_0/M_AXI_HPM1_FPD]
  connect_bd_intf_net -intf_net adc0_clk_0_1 [get_bd_intf_ports adc0_clk] [get_bd_intf_pins usp_rf_data_converter_0/adc0_clk]
  connect_bd_intf_net -intf_net adc2_clk_0_1 [get_bd_intf_ports adc2_clk] [get_bd_intf_pins usp_rf_data_converter_0/adc2_clk]
  connect_bd_intf_net -intf_net axi_interconnect_0_M00_AXI [get_bd_intf_pins dac_path/PS_MEM_AXI] [get_bd_intf_pins zynq_ultra_ps_e_0/S_AXI_HP1_FPD]
  connect_bd_intf_net -intf_net axi_interconnect_0_M01_AXI [get_bd_intf_pins dac_path/PL_MEM_AXI] [get_bd_intf_pins smartconnect_0/S02_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_1_M00_AXI [get_bd_intf_pins adc_path/PS_MEM_AXI] [get_bd_intf_pins zynq_ultra_ps_e_0/S_AXI_HP0_FPD]
  connect_bd_intf_net -intf_net axi_interconnect_1_M01_AXI [get_bd_intf_pins adc_path/PL_MEM_AXI] [get_bd_intf_pins smartconnect_0/S01_AXI]
  connect_bd_intf_net -intf_net dac0_clk_0_1 [get_bd_intf_ports dac0_clk] [get_bd_intf_pins usp_rf_data_converter_0/dac0_clk]
  connect_bd_intf_net -intf_net dac1_clk_0_1 [get_bd_intf_ports dac1_clk] [get_bd_intf_pins usp_rf_data_converter_0/dac1_clk]
  connect_bd_intf_net -intf_net dac_path_DAC1_AXIS [get_bd_intf_pins dac_path/DAC1_AXIS] [get_bd_intf_pins usp_rf_data_converter_0/s10_axis]
  connect_bd_intf_net -intf_net dac_path_M01_AXIS [get_bd_intf_pins dac_path/DAC0_AXIS] [get_bd_intf_pins usp_rf_data_converter_0/s00_axis]
  connect_bd_intf_net -intf_net ddr4_0_C0_DDR4 [get_bd_intf_ports ddr4_pl] [get_bd_intf_pins ddr4_0/C0_DDR4]
  connect_bd_intf_net -intf_net lmk_clk1_1 [get_bd_intf_ports lmk_clk1] [get_bd_intf_pins clocktreeMTS/lmk_clk1]
  connect_bd_intf_net -intf_net lmk_clk2_1 [get_bd_intf_ports lmk_clk2] [get_bd_intf_pins clocktreeMTS/lmk_clk2]
  connect_bd_intf_net -intf_net ps8_axi_periph_M00_AXI [get_bd_intf_pins dac_path/S_AXI_LITE] [get_bd_intf_pins ps8_axi_periph/M00_AXI]
  connect_bd_intf_net -intf_net ps8_axi_periph_M01_AXI [get_bd_intf_pins adc_path/DMA_AXI_LITE] [get_bd_intf_pins ps8_axi_periph/M01_AXI]
  connect_bd_intf_net -intf_net ps8_axi_periph_M02_AXI [get_bd_intf_pins ps8_axi_periph/M02_AXI] [get_bd_intf_pins usp_rf_data_converter_0/s_axi]
  connect_bd_intf_net -intf_net ps8_axi_periph_M03_AXI [get_bd_intf_pins adc_path/FLOW_AXI_LITE] [get_bd_intf_pins ps8_axi_periph/M03_AXI]
  connect_bd_intf_net -intf_net ps8_axi_periph_M04_AXI [get_bd_intf_pins clocktreeMTS/s_axi_lite] [get_bd_intf_pins ps8_axi_periph/M04_AXI]
  connect_bd_intf_net -intf_net smartconnect_0_M00_AXI [get_bd_intf_pins ddr4_0/C0_DDR4_S_AXI] [get_bd_intf_pins smartconnect_0/M00_AXI]
  connect_bd_intf_net -intf_net sys_clk_ddr4_1 [get_bd_intf_ports sys_clk_ddr4] [get_bd_intf_pins clocktreeMTS/sys_clk_ddr4]
  connect_bd_intf_net -intf_net sysref_in_0_1 [get_bd_intf_ports sysref_in] [get_bd_intf_pins usp_rf_data_converter_0/sysref_in]
  connect_bd_intf_net -intf_net usp_rf_data_converter_0_m00_axis [get_bd_intf_pins adc_path/ADC0_AXIS] [get_bd_intf_pins usp_rf_data_converter_0/m00_axis]
  connect_bd_intf_net -intf_net usp_rf_data_converter_0_m20_axis [get_bd_intf_pins adc_path/ADC1_AXIS] [get_bd_intf_pins usp_rf_data_converter_0/m20_axis]
  connect_bd_intf_net -intf_net usp_rf_data_converter_0_vout00 [get_bd_intf_ports vout00] [get_bd_intf_pins usp_rf_data_converter_0/vout00]
  connect_bd_intf_net -intf_net usp_rf_data_converter_0_vout01 [get_bd_intf_ports vout01] [get_bd_intf_pins usp_rf_data_converter_0/vout01]
  connect_bd_intf_net -intf_net usp_rf_data_converter_0_vout02 [get_bd_intf_ports vout02] [get_bd_intf_pins usp_rf_data_converter_0/vout02]
  connect_bd_intf_net -intf_net usp_rf_data_converter_0_vout03 [get_bd_intf_ports vout03] [get_bd_intf_pins usp_rf_data_converter_0/vout03]
  connect_bd_intf_net -intf_net usp_rf_data_converter_0_vout10 [get_bd_intf_ports vout10] [get_bd_intf_pins usp_rf_data_converter_0/vout10]
  connect_bd_intf_net -intf_net usp_rf_data_converter_0_vout11 [get_bd_intf_ports vout11] [get_bd_intf_pins usp_rf_data_converter_0/vout11]
  connect_bd_intf_net -intf_net usp_rf_data_converter_0_vout12 [get_bd_intf_ports vout12] [get_bd_intf_pins usp_rf_data_converter_0/vout12]
  connect_bd_intf_net -intf_net usp_rf_data_converter_0_vout13 [get_bd_intf_ports vout13] [get_bd_intf_pins usp_rf_data_converter_0/vout13]
  connect_bd_intf_net -intf_net vin0_01_0_1 [get_bd_intf_ports vin0_01] [get_bd_intf_pins usp_rf_data_converter_0/vin0_01]
  connect_bd_intf_net -intf_net vin0_23_0_1 [get_bd_intf_ports vin0_23] [get_bd_intf_pins usp_rf_data_converter_0/vin0_23]
  connect_bd_intf_net -intf_net vin2_01_0_1 [get_bd_intf_ports vin2_01] [get_bd_intf_pins usp_rf_data_converter_0/vin2_01]
  connect_bd_intf_net -intf_net vin2_23_0_1 [get_bd_intf_ports vin2_23] [get_bd_intf_pins usp_rf_data_converter_0/vin2_23]
  connect_bd_intf_net -intf_net zynq_ultra_ps_e_0_M_AXI_HPM0_FPD [get_bd_intf_pins smartconnect_0/S00_AXI] [get_bd_intf_pins zynq_ultra_ps_e_0/M_AXI_HPM0_FPD]

  # Create port connections
  connect_bd_net -net adc_control_1 [get_bd_pins adc_path/adc_control] [get_bd_pins clocktreeMTS/adc_control]
  connect_bd_net -net adc_path_s2mm_introut [get_bd_pins adc_path/s2mm_introut] [get_bd_pins irq_concat/In1]
  connect_bd_net -net clk_block_BUFG_O [get_bd_pins clocktreeMTS/ddr_clk] [get_bd_pins ddr4_0/c0_sys_clk_i] [get_bd_pins reset_block/clk_in1]
  connect_bd_net -net clk_block_clk_out2 [get_bd_pins adc_path/adc_clk] [get_bd_pins clocktreeMTS/rf_clk] [get_bd_pins dac_path/dac_clk] [get_bd_pins reset_block/rf_clk] [get_bd_pins usp_rf_data_converter_0/m0_axis_aclk] [get_bd_pins usp_rf_data_converter_0/m2_axis_aclk] [get_bd_pins usp_rf_data_converter_0/s0_axis_aclk] [get_bd_pins usp_rf_data_converter_0/s1_axis_aclk]
  connect_bd_net -net clocktreeMTS_dest_out [get_bd_pins clocktreeMTS/user_sysref] [get_bd_pins usp_rf_data_converter_0/user_sysref_adc] [get_bd_pins usp_rf_data_converter_0/user_sysref_dac]
  connect_bd_net -net clocktreeMTS_interrupt [get_bd_pins clocktreeMTS/interrupt] [get_bd_pins irq_concat/In3]
  connect_bd_net -net clocktreeMTS_locked [get_bd_pins clocktreeMTS/locked] [get_bd_pins reset_block/dcm_locked]
  connect_bd_net -net dac_control_1 [get_bd_pins clocktreeMTS/dac_control] [get_bd_pins dac_path/dac_control]
  connect_bd_net -net dac_path_mm2s_introut [get_bd_pins dac_path/mm2s_introut] [get_bd_pins irq_concat/In2]
  connect_bd_net -net ddr4_0_c0_ddr4_ui_clk [get_bd_pins adc_path/ddr4_clk] [get_bd_pins dac_path/ddr4_clk] [get_bd_pins ddr4_0/c0_ddr4_ui_clk] [get_bd_pins reset_block/ddr4_clk] [get_bd_pins smartconnect_0/aclk] [get_bd_pins zynq_ultra_ps_e_0/maxihpm0_fpd_aclk] [get_bd_pins zynq_ultra_ps_e_0/saxihp0_fpd_aclk] [get_bd_pins zynq_ultra_ps_e_0/saxihp1_fpd_aclk]
  connect_bd_net -net ddr4_0_c0_ddr4_ui_clk_sync_rst [get_bd_pins ddr4_0/c0_ddr4_ui_clk_sync_rst] [get_bd_pins reset_block/ddr4_rstn]
  connect_bd_net -net ddr4_0_c0_init_calib_complete [get_bd_ports ddr4_led] [get_bd_pins ddr4_0/c0_init_calib_complete]
  connect_bd_net -net reset_block_Res [get_bd_pins ddr4_0/sys_rst] [get_bd_pins reset_block/ddr4_sys_rst]
  connect_bd_net -net reset_block_peripheral_aresetn1 [get_bd_pins adc_path/adc_resetn] [get_bd_pins dac_path/dac_resetn] [get_bd_pins reset_block/rf_resetn] [get_bd_pins usp_rf_data_converter_0/m0_axis_aresetn] [get_bd_pins usp_rf_data_converter_0/m2_axis_aresetn] [get_bd_pins usp_rf_data_converter_0/s0_axis_aresetn] [get_bd_pins usp_rf_data_converter_0/s1_axis_aresetn]
  connect_bd_net -net rst_ddr4_200M_peripheral_aresetn [get_bd_pins adc_path/ddr4_resetn_1] [get_bd_pins dac_path/ddr4_resetn_1] [get_bd_pins ddr4_0/c0_ddr4_aresetn] [get_bd_pins reset_block/ddr4_resetn_1] [get_bd_pins smartconnect_0/aresetn]
  connect_bd_net -net rst_ps8_100M_interconnect_aresetn [get_bd_pins ps8_axi_periph/ARESETN] [get_bd_pins reset_block/ps8_resetn_0]
  connect_bd_net -net rst_ps8_100M_peripheral_aresetn [get_bd_pins adc_path/ps8_resetn] [get_bd_pins clocktreeMTS/s_axi_aresetn] [get_bd_pins dac_path/ps8_resetn] [get_bd_pins ps8_axi_periph/M00_ARESETN] [get_bd_pins ps8_axi_periph/M01_ARESETN] [get_bd_pins ps8_axi_periph/M02_ARESETN] [get_bd_pins ps8_axi_periph/M03_ARESETN] [get_bd_pins ps8_axi_periph/M04_ARESETN] [get_bd_pins ps8_axi_periph/S00_ARESETN] [get_bd_pins reset_block/ps8_resetn_1] [get_bd_pins usp_rf_data_converter_0/s_axi_aresetn]
  connect_bd_net -net usp_rf_data_converter_0_irq [get_bd_pins irq_concat/In0] [get_bd_pins usp_rf_data_converter_0/irq]
  connect_bd_net -net xlconcat_0_dout [get_bd_pins irq_concat/dout] [get_bd_pins zynq_ultra_ps_e_0/pl_ps_irq0]
  connect_bd_net -net xlconstant_0_dout [get_bd_pins usp_rf_data_converter_0/m02_axis_tready] [get_bd_pins usp_rf_data_converter_0/m22_axis_tready] [get_bd_pins xlconstant_0/dout]
  connect_bd_net -net xlconstant_1_dout [get_bd_pins usp_rf_data_converter_0/s01_axis_tvalid] [get_bd_pins usp_rf_data_converter_0/s02_axis_tvalid] [get_bd_pins usp_rf_data_converter_0/s03_axis_tvalid] [get_bd_pins usp_rf_data_converter_0/s11_axis_tvalid] [get_bd_pins usp_rf_data_converter_0/s12_axis_tvalid] [get_bd_pins usp_rf_data_converter_0/s13_axis_tvalid] [get_bd_pins xlconstant_1/dout]
  connect_bd_net -net xlconstant_2_dout [get_bd_pins usp_rf_data_converter_0/s01_axis_tdata] [get_bd_pins usp_rf_data_converter_0/s02_axis_tdata] [get_bd_pins usp_rf_data_converter_0/s03_axis_tdata] [get_bd_pins usp_rf_data_converter_0/s11_axis_tdata] [get_bd_pins usp_rf_data_converter_0/s12_axis_tdata] [get_bd_pins usp_rf_data_converter_0/s13_axis_tdata] [get_bd_pins xlconstant_2/dout]
  connect_bd_net -net xlslice_0_Dout [get_bd_ports lmk_rst] [get_bd_pins xlslice_0/Dout]
  connect_bd_net -net xlslice_1_Dout [get_bd_ports gpio_test] [get_bd_pins xlslice_1/Dout]
  connect_bd_net -net zynq_ultra_ps_e_0_emio_gpio_o [get_bd_pins adc_path/Din] [get_bd_pins clocktreeMTS/Din] [get_bd_pins dac_path/Din] [get_bd_pins xlslice_0/Din] [get_bd_pins xlslice_1/Din] [get_bd_pins zynq_ultra_ps_e_0/emio_gpio_o]
  connect_bd_net -net zynq_ultra_ps_e_0_pl_clk0 [get_bd_pins adc_path/ps8_clk] [get_bd_pins clocktreeMTS/s_axi_aclk] [get_bd_pins dac_path/ps8_clk] [get_bd_pins ps8_axi_periph/ACLK] [get_bd_pins ps8_axi_periph/M00_ACLK] [get_bd_pins ps8_axi_periph/M01_ACLK] [get_bd_pins ps8_axi_periph/M02_ACLK] [get_bd_pins ps8_axi_periph/M03_ACLK] [get_bd_pins ps8_axi_periph/M04_ACLK] [get_bd_pins ps8_axi_periph/S00_ACLK] [get_bd_pins reset_block/ps8_clk] [get_bd_pins usp_rf_data_converter_0/s_axi_aclk] [get_bd_pins zynq_ultra_ps_e_0/maxihpm1_fpd_aclk] [get_bd_pins zynq_ultra_ps_e_0/pl_clk0]
  connect_bd_net -net zynq_ultra_ps_e_0_pl_resetn0 [get_bd_pins reset_block/ps8_rstn] [get_bd_pins zynq_ultra_ps_e_0/pl_resetn0]

  # Create address segments
  assign_bd_address -offset 0xB000A000 -range 0x00001000 -target_address_space [get_bd_addr_spaces zynq_ultra_ps_e_0/Data] [get_bd_addr_segs adc_path/axi_dma_0/S_AXI_LITE/Reg] -force
  assign_bd_address -offset 0xB0002000 -range 0x00001000 -target_address_space [get_bd_addr_spaces zynq_ultra_ps_e_0/Data] [get_bd_addr_segs dac_path/axi_dma_0/S_AXI_LITE/Reg] -force
  assign_bd_address -offset 0xB0020000 -range 0x00001000 -target_address_space [get_bd_addr_spaces zynq_ultra_ps_e_0/Data] [get_bd_addr_segs adc_path/axis_flow_ctrl_0/S00_AXI/S00_AXI_reg] -force
  assign_bd_address -offset 0xB0010000 -range 0x00010000 -target_address_space [get_bd_addr_spaces zynq_ultra_ps_e_0/Data] [get_bd_addr_segs clocktreeMTS/clk_wiz_0/s_axi_lite/Reg] -force
  assign_bd_address -offset 0x001000000000 -range 0x000100000000 -target_address_space [get_bd_addr_spaces zynq_ultra_ps_e_0/Data] [get_bd_addr_segs ddr4_0/C0_DDR4_MEMORY_MAP/C0_DDR4_ADDRESS_BLOCK] -force
  assign_bd_address -offset 0xB0040000 -range 0x00040000 -target_address_space [get_bd_addr_spaces zynq_ultra_ps_e_0/Data] [get_bd_addr_segs usp_rf_data_converter_0/s_axi/Reg] -force
  assign_bd_address -offset 0x001000000000 -range 0x000100000000 -target_address_space [get_bd_addr_spaces adc_path/axi_dma_0/Data_S2MM] [get_bd_addr_segs ddr4_0/C0_DDR4_MEMORY_MAP/C0_DDR4_ADDRESS_BLOCK] -force
  assign_bd_address -offset 0x000800000000 -range 0x000800000000 -target_address_space [get_bd_addr_spaces adc_path/axi_dma_0/Data_S2MM] [get_bd_addr_segs zynq_ultra_ps_e_0/SAXIGP2/HP0_DDR_HIGH] -force
  assign_bd_address -offset 0x00000000 -range 0x80000000 -target_address_space [get_bd_addr_spaces adc_path/axi_dma_0/Data_S2MM] [get_bd_addr_segs zynq_ultra_ps_e_0/SAXIGP2/HP0_DDR_LOW] -force
  assign_bd_address -offset 0xFF000000 -range 0x01000000 -target_address_space [get_bd_addr_spaces adc_path/axi_dma_0/Data_S2MM] [get_bd_addr_segs zynq_ultra_ps_e_0/SAXIGP2/HP0_LPS_OCM] -force
  assign_bd_address -offset 0xC0000000 -range 0x20000000 -target_address_space [get_bd_addr_spaces adc_path/axi_dma_0/Data_S2MM] [get_bd_addr_segs zynq_ultra_ps_e_0/SAXIGP2/HP0_QSPI] -force
  assign_bd_address -offset 0x001000000000 -range 0x000100000000 -target_address_space [get_bd_addr_spaces dac_path/axi_dma_0/Data_MM2S] [get_bd_addr_segs ddr4_0/C0_DDR4_MEMORY_MAP/C0_DDR4_ADDRESS_BLOCK] -force
  assign_bd_address -offset 0x000800000000 -range 0x000800000000 -target_address_space [get_bd_addr_spaces dac_path/axi_dma_0/Data_MM2S] [get_bd_addr_segs zynq_ultra_ps_e_0/SAXIGP3/HP1_DDR_HIGH] -force
  assign_bd_address -offset 0x00000000 -range 0x80000000 -target_address_space [get_bd_addr_spaces dac_path/axi_dma_0/Data_MM2S] [get_bd_addr_segs zynq_ultra_ps_e_0/SAXIGP3/HP1_DDR_LOW] -force
  assign_bd_address -offset 0xFF000000 -range 0x01000000 -target_address_space [get_bd_addr_spaces dac_path/axi_dma_0/Data_MM2S] [get_bd_addr_segs zynq_ultra_ps_e_0/SAXIGP3/HP1_LPS_OCM] -force
  assign_bd_address -offset 0xC0000000 -range 0x20000000 -target_address_space [get_bd_addr_spaces dac_path/axi_dma_0/Data_MM2S] [get_bd_addr_segs zynq_ultra_ps_e_0/SAXIGP3/HP1_QSPI] -force


  # Restore current instance
  current_bd_instance $oldCurInst

  save_bd_design
}
# End of create_root_design()


##################################################################
# MAIN FLOW
##################################################################

create_root_design ""


common::send_gid_msg -ssname BD::TCL -id 2053 -severity "WARNING" "This Tcl script was generated from a block design that has not been validated. It is possible that design <$design_name> may result in errors during validation."

