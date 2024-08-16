> Download the rx.img
I would recommend to use google chrome, because I think that otherbrowsers might have a problem with big files.

> Burn the rx.img to both SD Cards
In Linux we can do the following. Insert the SD card in the computer
$ sudo fdisk -l

Disk /dev/sdd: 14.84 GiB, 15931539456 bytes, 31116288 sectors
Disk model: USB3.0 CRW   -SD
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xbc7f45e1

$ sudo dd if=~/Downloads/rx.img of=/dev/sdd 

In Windows, I think that we can use Rufus (https://rufus.ie/en/)

> The image will have a static ip address of 10.1.1.30. Therefore, we need to change at least one of the nodes. 
To change the static ip address we need to follow these steps:
 1) Insert the SD card to a computer. This should appear as two filesystems (PYNQ and root)
 2) Open the root file system
 3) Edit the /etc/network/interfaces.d/eth0 and modify the address
 4) Safely unmount the drive

> Run the receiver (10.1.1.30). 
$ python rx.py

The recv function will return the time-domain pdps from 17 receiver BF directions. Right now the program will just plot the pdps. 

> Run the transmitter (10.1.1.40)
$ python tx.py

TODO: Update registers to match the best performance for the EVKs we have at VTT.
TODO: Use the functions set_rx_gain and set_tx_gain to improve link distance.

Parameters:
Carrier frequency: 57.51 GHz (We cannot do lower than that, given that our bandwidth is less than 1GHz we should be okay)
Bandwidth: 983.04 MHz
Number of subcarriers: 1024
Number of occupied subcarriers: 800 (We can increase or decrease this parameter)


> Replace the files in /home/xilinx/jupyter_notebooks/mmwsdr
upload either using the web interface or scp the following files:
- run.sh
- server.py
- txtd.npy
- RxDebug.ipynb