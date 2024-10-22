sudo gpioset 0 2=1
sudo gpioset 0 3=1

# Set to 0 for 20dB attenuation on the TX IF path.
# This is used when the IF transmitter is high power (USRP)
# Set to 1 (no attenuation) when connecting to a low-power IF source like the RFSoC
sudo gpioset 0 6=0


cd ./spi
sudo ./setupspi.py

sudo ./program_spi.py ltc5594 tx0 ./registers/ltc5594/regs.txt
sudo ./program_spi.py ltc5594 tx1 ./registers/ltc5594/regs.txt

sudo ./program_spi.py adrf6520 tx0 bypass
sudo ./program_spi.py adrf6520 tx1 bypass
sudo ./program_spi.py adrf6520 rx0 bypass
sudo ./program_spi.py adrf6520 rx1 bypass

sudo ./program_spi.py lmx2820 hf ./registers/lmx2820/10GHz_pow3.txt
sudo ./program_spi.py lmx2820 lf ./registers/lmx2820/1GHz.txt

sudo ./program_spi.py ltc2668 -- 7 0.85
sudo ./program_spi.py ltc2668 -- 8 0.85
sudo ./program_spi.py ltc2668 -- 5 0.55
sudo ./program_spi.py ltc2668 -- 6 0.55

# 10 GHz
sudo ./program_spi.py ltc2668 -- 0 -0.054	# TX Ch1 Q Correction
sudo ./program_spi.py ltc2668 -- 2 0.178	# TX Ch1 I Correction
sudo ./program_spi.py ltc2668 -- 1 -0.054	# TX Ch2 Q Correction
sudo ./program_spi.py ltc2668 -- 3 0.178	# TX Ch2 I Correction

