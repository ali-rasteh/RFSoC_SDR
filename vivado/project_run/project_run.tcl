set project_name "rfsoc_fr3_piradio"
set top_name "rfsoc_fr3_piradio"
set design_name "design_rfsoc_fr3_piradio"
set version_file "/home/sharan/shared/rfsoc_fr3_piradio_version.txt"


set cur_project_name [current_project]
set cur_top_name [get_property top [current_fileset]]
set cur_design_name [lindex [get_bd_designs] 2]
set cur_proj_dir [get_property DIRECTORY [current_project]]
set current_date [clock format [clock seconds] -format {%Y%m%d-%H%M%S}]


if {![file exists $version_file]} {
    puts "Error: Version file does not exist"
    return
}
set version_fd [open $version_file r]
set version [gets $version_fd]
# set version "v1-0-0"
close $version_fd
puts "Version read from the version file: $version"

set version_list [split $version "-"]
set last_index [expr {[llength $version_list] - 1}]
set version_list [lreplace $version_list $last_index $last_index [expr {[lindex $version_list $last_index] + 1}]]
set new_version [join $version_list "-"]
set version_fd [open $version_file w]
puts $version_fd $new_version
close $version_fd
puts "New version written to the version file: $new_version"


set output_filename "${cur_project_name}_${version}_${current_date}"

# Create a project - Modify accordingly if you are using an existing project
# create_project $project_name ./ -force -part xc7z020clg484-1

# set_property top top_name [current_fileset]
# set_property bitstream.file_name "${output_filename}.bit" [current_run]
# set_property -name "project.bitstream.file_name" -value "${output_filename}.bit" -objects [current_project]
set_property BITSTREAM.GENERAL.BITSTREAM_NAME "${output_filename}.bit" [current_bd_design]


# Generate the bitstream
save_bd_design
reset_run synth_1
launch_runs impl_1 -to_step write_bitstream -jobs 6
wait_on_run impl_1


set builds_path "${cur_proj_dir}/builds"
if {[file exists $builds_path] && [file isdirectory $builds_path]} {
    puts "Builds directory already exists"
} else {
    puts "Builds directory does not exist. Creating directory..."
    file mkdir $builds_path
    # puts "Directory created: $builds_path"
}


write_hw_platform -fixed -include_bit -force -file "${builds_path}/${output_filename}.xsa"
write_bd_tcl -force "${cur_proj_dir}/create_bd.tcl"
write_project_tcl -force "${cur_proj_dir}/create_project.tcl"


set bit_file_path "${cur_proj_dir}/${cur_project_name}.runs/impl_1/${cur_top_name}.bit"
set hwh_file_path "${cur_proj_dir}/${cur_project_name}.gen/sources_1/bd/${cur_design_name}/hw_handoff/${cur_design_name}.hwh"
if {[file exists $bit_file_path]} {
    file rename $bit_file_path "${builds_path}/${output_filename}.bit"
    puts "Bit file moved and renamed"
} else {
    puts "Error: The original bit file does not exist"
}
if {[file exists $hwh_file_path]} {
    file rename $hwh_file_path "${builds_path}/${output_filename}.hwh"
    puts "hwh file moved and renamed"
} else {
    puts "Error: The original hwh file does not exist"
}


set builds_file "${builds_path}/builds.txt"
set builds_fd [open $builds_file "a"]
puts $builds_fd $output_filename
close $builds_fd
puts "Appended the build to the builds history file"
