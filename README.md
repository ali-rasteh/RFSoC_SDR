# RFSoC_SDR

## Steps to bring up a RFSoC4x2:

- A very good source of information is provided in [This Link](https://github.com/nyu-wireless/mmwsdr) and [This Link](https://github.com/nyu-wireless/mmwsdr/tree/main/Lessons%20for%20RFSoC)

- Download the RFSoC4x2 image from [here](https://www.pynq.io/boards.html). This repo is tested with v3.0.1 but newer versions should be also OK unless they are not backward compatible.
- Program the RFSoC4x2 image to the provided SD-card usign Rufus (in windows) or any other similar softwares in your specific OS.
- Put the SD-card in RFSoC4x2 and power it on. Wait until you see the IP address information shown on the LCD.
- Connect the RFSoC4x2 to your laptop/PC using a USB cable.
- Open the RFSoC web interface using a web browser on [This Link](http://192.168.3.1:9090/lab/)
- Put all the python scripts from [here](https://github.com/ali-rasteh/RFSoC_SDR/tree/main/python) in the corresponding project folder on the board. you can create a folder for your project at `/home/xilinx/jupyter_notebooks/`.
- Put the clock configurations files from [this folder in the Repo](https://github.com/ali-rasteh/RFSoC_SDR/tree/main/rfsoc/rfsoc4x2_clock_configs) in this folder on RFSoC4x2: `/usr/local/share/pynq-venv/lib/python3.10/site-packages/xrfclk/`
- Provide internet connection to the board by connecting it to a server/PC and routing the traffic or by any other methods you like. 
- Install RFSoC-MTS package according to instructions in [this linke](https://github.com/Xilinx/RFSoC-MTS/tree/main)
- Put the latest version of the RFSoC4x2 FPGA image files from [here](https://github.com/ali-rasteh/RFSoC_SDR/tree/main/vivado/sounder_fr3_if_ddr4_mimo_4x2/builds) in your project folder beside the python scritps. You only need to transfer the `.bit` and `.hwh` files.


## Steps to do measurements on FR3 using Pi-Radio FR3 Transceiver:

- Assemble Vivaldi antennas using appropriate spacers to tune the antenna spacing needed for the target frequency.
- Install Vivaldi antennas on a fixed structure.
- Connect the RF ports of the Pi-Radio FR3 Transceiver to the Vivaldi antennas. Please be consistent in antennas port indexing. No passive elements are needed on the RF port if you're connecting them to antennas. But if you're using a cable to connect RF ports you need at least 20dB attenuator.
- Connect the IF ports of the Pi-Radio to the RFSoC4x2. The RFSoC4x2 outout ports 1,2 are DAC_A, DAC_B respectively. Also its input ports 1,2 are ADC_B and ADC_D respectively. Please connect them to the right port numbers on the Pi-Radio. On the transmitter side, connect a DC blocker and a DC-1300 MHz filter on the RFSoC4x2 ports. On the receive side connect a DC blocker, a DC-1300 MHz filter and a 20dB attenuator on each port.
- Power on the Pi-Radio FR3 Transceiver.
- Connect to the Pi-Radio board by running `ssh ubuntu@192.168.137.51` in the Linux shell. The password is `temppwd`
- run `./do_everything.sh` to configure the board on the right frequency. At this point the Pi-Radio FR3 Transceiver is ready to use.
- Alternatively you can connect to the board's Web GUI at [This Link](http://192.168.137.51:5006) and configure all needed parameters.
- Connect the RFSoC4x2 to your laptop/PC using a USB cable.
- Open the RFSoC web interface using a web browser on [This Link](http://192.168.3.1:9090/lab/)
- Run the rfsoc_test.py script on the RFSoC4x2 using a jupyter notebook or using `python rfsoc_test.py`. When you see `Waiting for a connection` in the log, the RFSoC4x2 is ready.
- refine the configurations in the `rfsoc_test.py` file on your system/PC and run the script using `python rfsoc_test.py`.
- First time you run the system you need to do phase calibration on the receiver, so when the script shows a message about the calibration, follow the instructions to run the calibration.
- Finally the script should receive the measurements, do the needed processing and show the animation plots.
- You can also save the signal and channel responses by adding appropriate elements to the save_list parameter.
