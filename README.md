# RFSoC_SDR

## Steps to do measurements on FR3:

- Assemble Vivaldi antennas using appropriate spacers to tune the antenna spacing needed for the target frequency.
- Install Vivaldi antennas on a fixed structure.
- Connect the RF ports of the Pi-Radio FR3 Tranceiver to the Vivaldi antennas. Please be consistent in antennas port indexing. No passive elements are needed on the RF port if you're connecting them to antennas. But if you're using a cable to connect RF ports you need at least 20dB attenuator.
- Connect the IF ports of the Pi-Radio to the RFSoC4x2. The RFSoC4x2 outout ports 1,2 are DAC_A, DAC_B respectively. Also its input ports 1,2 are ADC_B and ADC_D respectively. Please connect them to the right port numbers on the Pi-Radio. On the transmitter side, connect a DC blocker and a DC-1300 MHz filter on the RFSoC4x2 ports. On the receive side connect a DC blocker, a DC-1300 MHz filter and a 20dB attenuator on each port.
- Power on the Pi-Radio FR3 Tranceiver.
- Connect to the Pi-Radio board by running `ssh ubuntu@192.168.137.51` in the Linux shell. The password is `temppwd`
- run `./do_everything.sh` to configure the board on the right frequency. At this point the Pi-Radio FR3 Tranceiver is ready to use.
- Power on the RFSoC4x2. Wait until you see the IP address information shown on the LCD.
- Connect the RFSoC4x2 to your laptop/PC using a USB cable.
- Open the RFSoC web interface using a web browser on [This Link](http://192.168.3.1:9090/lab/)
- Put all the python scripts along with the last version of the FPGA bit-file (which is used in the code) on the RFSoC in a new folder.
- Run the rfsoc_test.py script using a jupyter notebook or using `python rfsoc_test.py`. When you see `Waiting for a connection` in the log, the RFSoC4x2 is ready.
- refine the configurations in the `rfsoc_test.py` file on your system/PC and run the script using `python rfsoc_test.py`.
- First time you run the system you need to do phase calibration on the receiver, so when the script shows a message about the calibration, follow the instructions to run the calibration.
- Finally the script should receive the measurements, do the needed processing and show the animation plots.
- You can also save the signal and channel responses by adding appropriate elements to the save_list parameter.
