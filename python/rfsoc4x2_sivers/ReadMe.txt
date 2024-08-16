====================================================================

Files description:

Each of folders RFSoC2x2 and RFSoC4x2 includes the Vivado projects for the corresponding board. Each folder contains two projects
one in Vivado version 2022.1 and another in version 2023.2. They are basocally the same project in different Vivado versions. Pynq is only
compatible with version 2022.1 so it's essential to use the corresponding project to make sure you face no problems.
Foler RFSoC4x2 also includes "RFSoC4x2 Python codes.zip" which contains all the required python scripts, jupyter notebooks, and prepared
Vivado xsa files to run the channel sounding in RFSoC4x2. There is also a "Clock configs" folder which contains the required clock configuratios
for LMK and LMX chips on RFSoC4x2 which are used by the xrfclk package in the code to do the required clock configurations.

====================================================================

Steps to prepare a RFSoC4x2 board to be tested by Notis project:
A very good source of information is provided in https://github.com/nyu-wireless/mmwsdr and https://github.com/nyu-wireless/mmwsdr/tree/main/Lessons%20for%20RFSoC

- Download the RFSoC4x2 image from https://www.pynq.io/boards.html. We have tested with v3.0.1 but newer versions should be also OK if there is any.
- Turn on RFSoC4x2 board.
- Put all the python codes in the corresponding project folder on the board. you can use /home/xilinx/jupyter_notebooks/ folder to create a folder for
  your project.
- Put the clock configurations files in this folder on RFSoC4x2: /usr/local/share/pynq-venv/lib/python3.10/site-packages/xrfclk/
- Provide internet connection to the board by connecting it to a server/worksattion and providing internet through that. 
- Install RFSoC-MTS package according to instructions on https://github.com/Xilinx/RFSoC-MTS/tree/main.
- If you need to change the Vivado project, change it and compile it again. Then export the .xsa file and put it in the project folder on RFSoC4x2 with
  the name "rfsoc4x2.xsa". To modify the Vivado project make sure to add board files under XILINX_INSTALL_PATH/data/boards/.
- Other steps are like RFSoC2x2 according to Notis Readme files except that you should use server_4x2.py instead of server.py. Also for debugging
  purposes you may use TxDebug_4x2.ipynb and RxDebug_4x2.ipynb

====================================================================

Changes made in RFSoC4x2 Vivado project compared to RFSoC2x2:
- First the board and Zynq type is modified to RFSoC4x2 and all the IPs are updated according to the new board.
- Then the RF data converter IP is reconfigured according to RFSoC4x2 ports specifications, etc but very similar to RFSoC2x2.
- The constraints file is modified according to RFSoC4x2 specifications and using the RFSoC4x2 BSP.
- The other parts of the design are not touched.
- Then you need to generate the bitstream and export the .xsa file from the project (or .bit and .hwh files together).


Changes made to the python scripts:
Changes in server_4x2.py compared to server.py in RFSoC2x2:
- The "run_sivers" flag is added to make it possible to run the code with or without running sivers configurations.
- The name of overlay is changed to "rfsoc4x2.xsa" to use the RFSoC4x2 Vivado project's exported xsa.
- Tiles sync configurations are accordingly changed to RFSoC requirements in the "init_tile_sync" and "sync_tiles" functions.
- The "lmk_reset" index in "init_gpio" function is changed as "lmk_reset" is connected to PS in RFSoC4x2.
- The "send" function is modified to add support for 'Sinusoid' and 'ChannelSounder' modes.
- The "receiveSamplesOnce" command is added in the "parseAndExecute" function.


Other changes needed to make the board ready:
- The LMK clock chip on RFSoC4x2 is different from RFSoC2x2. So the LMK and LMX clock chips need to be reconfigured according to the new board.
  To do this we need to use TI Tics Pro software to generate clock configuration files for the corresponding part numbers and put it in the location
  explained earlier. New clock configurations are generated and provided in these files.
  
====================================================================