#!/bin/bash

for f in /etc/profile.d/*.sh; do source $f; done

sudo fuser -k 8080/tcp
sudo fuser -k 8081/tcp

python /home/xilinx/jupyter_notebooks/mmwsdr/server.py
