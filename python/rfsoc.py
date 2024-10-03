from backend import *
from backend import be_np as np, be_scp as scipy
from signal_utilsrfsoc import Signal_Utils_Rfsoc
from tcp_comm import Tcp_Comm
try:
    from siversController import *
except:
    pass




class RFSoC(Signal_Utils_Rfsoc):
    def __init__(self, params):
        super().__init__(params)

        self.beam_test = params.beam_test
        self.project = params.project
        self.board = params.board
        self.RFFE = params.RFFE
        self.TCP_port_Cmd = params.TCP_port_Cmd
        self.TCP_port_Data = params.TCP_port_Data
        self.lmk_freq_mhz = params.lmk_freq_mhz
        self.lmx_freq_mhz = params.lmx_freq_mhz
        self.dac_fs = params.fs_tx
        self.adc_fs = params.fs_rx
        self.bit_file_path = params.bit_file_path
        self.mix_freq_dac = params.mix_freq_dac
        self.mix_freq_adc = params.mix_freq_adc
        self.mix_phase_off = params.mix_phase_off
        self.DynamicPLLConfig = params.DynamicPLLConfig
        self.do_mixer_settings = params.do_mixer_settings
        self.do_pll_settings = params.do_pll_settings
        self.run_tcp_server = params.run_tcp_server
        self.verbose_level = params.verbose_level
        self.n_frame_wr=params.n_frame_wr
        self.n_frame_rd=params.n_frame_rd
        self.n_tx_ant = params.n_tx_ant
        
        if self.board=='rfsoc_2x2':
            self.adc_bits = 12
            self.dac_bits = 14
            self.adc_max_fs = 4096e6
            self.dac_max_fs = 6554e6
        elif self.board=='rfsoc_4x2':
            self.adc_bits = 14
            self.dac_bits = 14
            self.adc_max_fs = 5000e6
            self.dac_max_fs = 9850e6

        if 'ddr4' in self.project:
            if self.board=='rfsoc_2x2':
                if 'sounder_bbf' in self.project:
                    self.dac_tile_block_dic = {0: [0], 1:[0]}
                    self.adc_tile_block_dic = {0: [0], 2:[0]}
                    self.dac_tiles_sync = [0,1]
                    self.adc_tiles_sync = [0,2]
                elif 'sounder_if' in self.project:
                    if self.n_tx_ant==1:
                        self.dac_tile_block_dic = {1: [0]}
                        self.dac_tiles_sync = [0]
                    elif self.n_tx_ant==2:
                        self.dac_tile_block_dic = {0: [0], 1:[0]}
                        self.dac_tiles_sync = [0,1]
                    if self.n_rx_ant==1:
                        self.adc_tile_block_dic = {2: [0]}
                        self.adc_tiles_sync = [0,2]
                    elif self.n_rx_ant==2:
                        self.adc_tile_block_dic = {0: [0], 2:[0]}
                        self.adc_tiles_sync = [0,2]
            elif self.board=='rfsoc_4x2':
                if 'sounder_bbf' in self.project:
                    self.dac_tile_block_dic = {0: [0], 2:[0]}
                    self.adc_tile_block_dic = {0: [0], 2:[0]}
                    self.dac_tiles_sync = [0,2]
                    self.adc_tiles_sync = [0,2]
                elif 'sounder_if' in self.project:
                    if self.n_tx_ant==1:
                        self.dac_tile_block_dic = {2: [0]}
                        self.dac_tiles_sync = []
                    elif self.n_tx_ant==2:
                        self.dac_tile_block_dic = {0: [0], 2:[0]}
                        self.dac_tiles_sync = []
                    if self.n_rx_ant==1:
                        self.adc_tile_block_dic = {2: [0]}
                        self.adc_tiles_sync = [0,2]
                    elif self.n_rx_ant==2:
                        self.adc_tile_block_dic = {0: [0], 2:[0]}
                        self.adc_tiles_sync = [0,2]
                    
        else:
            if self.board=='rfsoc_2x2':
                if 'sounder_bbf' in self.project:
                    self.dac_tile_block_dic = {0: [0], 1:[0]}
                    self.adc_tile_block_dic = {0: [0], 2:[0]}
                    self.dac_tiles_sync = []
                    self.adc_tiles_sync = []
                elif 'sounder_if' in self.project:
                    self.dac_tile_block_dic = {1: [0]}
                    self.adc_tile_block_dic = {2: [0]}
                    self.dac_tiles_sync = []
                    self.adc_tiles_sync = []
            elif self.board=='rfsoc_4x2':
                if 'sounder_bbf' in self.project:
                    self.dac_tile_block_dic = {0: [0], 2:[0]}
                    self.adc_tile_block_dic = {0: [0], 2:[0]}
                    self.dac_tiles_sync = []
                    self.adc_tiles_sync = []
                elif 'sounder_if' in self.project:
                    self.dac_tile_block_dic = {2: [0]}
                    self.adc_tile_block_dic = {2: [0]}
                    self.dac_tiles_sync = []
                    self.adc_tiles_sync = []
        self.dac_tile_id = list(self.dac_tile_block_dic.keys())[0]
        self.dac_block_id = self.dac_tile_block_dic[self.dac_tile_id][0]
        self.adc_tile_id = list(self.adc_tile_block_dic.keys())[0]
        self.adc_block_id = self.adc_tile_block_dic[self.adc_tile_id][0]


        if 'ddr4' in self.project:
            if 'sounder_bbf' in self.project:
                self.n_par_strms_tx = 4
                self.n_par_strms_rx = 4
            elif 'sounder_if' in self.project:
                self.n_par_strms_tx = 8
                self.n_par_strms_rx = 4
        else:
            if 'sounder_bbf' in self.project:
                self.n_par_strms_tx = 4
                self.n_par_strms_rx = 4
            elif 'sounder_if' in self.project:
                self.n_par_strms_tx = 4
                self.n_par_strms_rx = 4
        
        if 'ddr4' in self.project:
            if 'sounder_bbf' in self.project:
                self.tx_mode = 2
                self.rx_mode = 1
            elif 'sounder_if' in self.project:
                self.tx_mode = 1
                self.rx_mode = 1
        else:
            if 'sounder_bbf' in self.project:
                self.tx_mode = 1
                self.rx_mode = 1
            elif 'sounder_if' in self.project:
                self.tx_mode = 1
                self.rx_mode = 1

        self.n_skip = 0
        
        self.CLOCKWIZARD_LOCK_ADDRESS = 0x0004
        self.CLOCKWIZARD_RESET_ADDRESS = 0x0000
        self.CLOCKWIZARD_RESET_TOKEN = 0x000A

        self.txtd = None
        self.rxtd = None

        if self.RFFE=='sivers':
            self.init_sivers()
        elif self.RFFE=='piradio':
            pass
        elif self.RFFE=='none':
            pass

        self.load_bit_file()
        self.allocate_input(n_frame=self.n_frame_rd)
        self.allocate_output(n_frame=self.n_frame_wr)
        self.gpio_init()
        self.clock_init()
        self.verify_clock_tree()
        self.init_rfdc()
        if 'ddr4' in self.project:
            self.dac_tiles_sync_hex = 0x0
            for id in self.dac_tiles_sync:
                self.dac_tiles_sync_hex += 0x1 << id
            self.adc_tiles_sync_hex = 0x0
            for id in self.adc_tiles_sync:
                self.adc_tiles_sync_hex += 0x1 << id
            self.init_tile_sync()
            self.sync_tiles(dacTiles=self.dac_tiles_sync_hex, adcTiles=self.adc_tiles_sync_hex)
        self.init_dac()
        self.init_adc()
        if 'sounder_if' in self.project:
            self.set_dac_mixer()
            self.set_adc_mixer()
        self.dma_init()
        if self.run_tcp_server:
            self.tcp_comm = Tcp_Comm(params)
            self.tcp_comm.init_tcp_server()

        self.print("rfsoc initialization done", thr=1)


    def load_bit_file(self, verbose=False):
        self.print("Starting to load the bit-file", thr=1)

        self.ol = Overlay(self.bit_file_path)
        if verbose:
            self.ol.ip_dict
            # ol?

        self.print("Bit-file loading done", thr=1)


    def init_sivers(self):
        self.print("Starting Sivers EVK controller", thr=1)
        allDevices=Ftdi.list_devices()
        Ftdi.show_devices()
        strFTDIdesc = str(allDevices[0][0])
        snStr = strFTDIdesc[strFTDIdesc.find('sn=')+4:strFTDIdesc.find('sn=')+14]
        siverEVKAddr = 'ftdi://ftdi:4232:'+ snStr
        self.print('siverEVKAddr: {}'.format(siverEVKAddr), thr=1)            
        self.siversControllerObj = siversController(siverEVKAddr)
        self.siversControllerObj.init()
        self.print("Sivers EVK controller is loaded", thr=1)


    def run(self):
        # Listen for incoming connections
        self.tcp_comm.TCPServerSocketCmd.listen(1)
        self.tcp_comm.TCPServerSocketData.listen(1)
        
        while True:
            # Wait for a connection
            self.print('\nWaiting for a connection', thr=2)
            self.connectionCMD, addrCMD = self.tcp_comm.TCPServerSocketCmd.accept()
            self.connectionData, addrDATA = self.tcp_comm.TCPServerSocketData.accept()
            self.print('\nConnection established', thr=2)
            
            after_idle_sec=1
            interval_sec=3
            max_fails=5
            self.connectionData.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.connectionData.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
            self.connectionData.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
            self.connectionData.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)
            
            self.connectionCMD.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.connectionCMD.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
            self.connectionCMD.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
            self.connectionCMD.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)            
            
            try:
                while True:
                    try:
                        receivedCMD = self.connectionCMD.recv(self.tcp_comm.tcp_bufferSize)
                        if receivedCMD:
                            self.print("\nClient CMD:{}".format(receivedCMD.decode()), thr=5)
                            responseToCMDinBytes = self.parseAndExecute(receivedCMD)
                            self.connectionCMD.sendall(responseToCMDinBytes)
                        else:
                            break
                    except:
                        break
            finally:
                # Clean up the connection
                self.print('\nConnection is closed.', thr=2)
                self.connectionCMD.close()                  
                self.connectionData.close()


    def parseAndExecute(self, receivedCMD):
        clientMsg = receivedCMD.decode()
        invalidCommandMessage = "ERROR: Invalid command"
        invalidNumberOfArgumentsMessage = "ERROR: Invalid number of arguments"
        successMessage = "Successully executed"
        droppedMessage = "Connection dropped?"
        clientMsgParsed = clientMsg.split()
        if clientMsgParsed[0] == "receiveSamplesOnce":
            if len(clientMsgParsed) == 1:
                iq_data = self.recv_frame_one(n_frame=self.n_frame_rd)
                iq_data = np.array(iq_data).flatten()
                iq_data = iq_data * (2 ** (self.adc_bits + 1) - 1)
                re = iq_data.real.astype(np.int16)
                im = iq_data.imag.astype(np.int16)
                iq_data = np.concatenate((re, im))
                self.connectionData.sendall(iq_data.tobytes())
                responseToCMD = "Success"
            else:
                responseToCMD = invalidNumberOfArgumentsMessage
        if clientMsgParsed[0] == "receiveSamples":
            if len(clientMsgParsed) == 1:
                iq_data = self.recv_frame(n_frame=self.n_frame_rd)
                re = iq_data.real.astype(np.int16)
                im = iq_data.imag.astype(np.int16)
                iq_data = np.concatenate((re, im))
                self.connectionData.sendall(iq_data.tobytes())
                responseToCMD = "Success"
            else:
                responseToCMD = invalidNumberOfArgumentsMessage
        elif clientMsgParsed[0] == "transmitSamples":
            if len(clientMsgParsed) == 1:
                self.send_frame(txtd=self.txtd)
                responseToCMD = 'Success'
            else:
                responseToCMD = invalidNumberOfArgumentsMessage       
        elif clientMsgParsed[0] == "getBeamIndexTX":
            if len(clientMsgParsed) == 1:
                responseToCMD = str(self.siversControllerObj.getBeamIndexTX())
            else:
                responseToCMD = invalidNumberOfArgumentsMessage 
        elif clientMsgParsed[0] == "setBeamIndexTX":
            if len(clientMsgParsed) == 2:
                beamIndex = int(clientMsgParsed[1])
                success, status = self.siversControllerObj.setBeamIndexTX(beamIndex)
                if success == True:
                    responseToCMD = successMessage 
                else:
                    responseToCMD = status 
            else:
                responseToCMD = invalidNumberOfArgumentsMessage  
        elif clientMsgParsed[0] == "getBeamIndexRX":
            if len(clientMsgParsed) == 1:
                responseToCMD = str(self.siversControllerObj.getBeamIndexRX())
            else:
                responseToCMD = invalidNumberOfArgumentsMessage 
        elif clientMsgParsed[0] == "setBeamIndexRX":
            if len(clientMsgParsed) == 2:
                beamIndex = int(clientMsgParsed[1])
                success, status = self.siversControllerObj.setBeamIndexRX(beamIndex)
                if success == True:
                    responseToCMD = successMessage 
                else:
                    responseToCMD = status 
            else:
                responseToCMD = invalidNumberOfArgumentsMessage
        elif clientMsgParsed[0] == "getModeSiver":
            if len(clientMsgParsed) == 1:
                responseToCMD = self.siversControllerObj.getMode()
            else:
                responseToCMD = invalidNumberOfArgumentsMessage 
        elif clientMsgParsed[0] == "setModeSiver":
            if len(clientMsgParsed) == 2:
                mode = clientMsgParsed[1]
                success,status = self.siversControllerObj.setMode(mode)
                if success == True:
                    responseToCMD = successMessage 
                else:
                    responseToCMD = status                  
            else:
                responseToCMD = invalidNumberOfArgumentsMessage    
        elif clientMsgParsed[0] == "getGainRX":
            if len(clientMsgParsed) == 1:
                rx_gain_ctrl_bb1, rx_gain_ctrl_bb2, rx_gain_ctrl_bb3, rx_gain_ctrl_bfrf,agc_int_bfrf_gain_lvl, agc_int_bb3_gain_lvl = self.siversControllerObj.getGainRX()
                responseToCMD = 'rx_gain_ctrl_bb1:' + str(hex(rx_gain_ctrl_bb1)) + \
                                ', rx_gain_ctrl_bb2:' +  str(hex(rx_gain_ctrl_bb2)) + \
                                ', rx_gain_ctrl_bb3:' +   str(hex(rx_gain_ctrl_bb3)) + \
                                ', rx_gain_ctrl_bfrf:' +   str(hex(rx_gain_ctrl_bfrf)) +\
                                ', agc_int_bfrf_gain_lvl:' +   str(hex(agc_int_bfrf_gain_lvl)) +\
                                ', agc_int_bb3_gain_lvl:' +   str(hex(agc_int_bb3_gain_lvl))
            else:
                responseToCMD = invalidNumberOfArgumentsMessage 
        elif clientMsgParsed[0] == "setGainRX":
            if len(clientMsgParsed) == 5:
                rx_gain_ctrl_bb1 = int(clientMsgParsed[1])
                rx_gain_ctrl_bb2 = int(clientMsgParsed[2])
                rx_gain_ctrl_bb3 = int(clientMsgParsed[3])
                rx_gain_ctrl_bfrf = int(clientMsgParsed[4])
                
                success,status = self.siversControllerObj.setGainRX(rx_gain_ctrl_bb1, rx_gain_ctrl_bb2, rx_gain_ctrl_bb3, rx_gain_ctrl_bfrf)
                if success == True:
                    responseToCMD = successMessage 
                else:
                    responseToCMD = status                  
            else:
                responseToCMD = invalidNumberOfArgumentsMessage      
        elif clientMsgParsed[0] == "getGainTX":
            if len(clientMsgParsed) == 1:
                tx_bb_gain, tx_bb_phase, tx_bb_iq_gain, tx_bfrf_gain, tx_ctrl = self.siversControllerObj.getGainTX()
                responseToCMD = 'tx_bb_gain:' + str(hex(tx_bb_gain)) + \
                                ', tx_bb_phase:' +  str(hex(tx_bb_phase)) + \
                                ', tx_bb_gain:' +   str(hex(tx_bb_iq_gain)) + \
                                ', tx_bfrf_gain:' +   str(hex(tx_bfrf_gain)) + \
                                ', tx_ctrl:' +   str(hex(tx_ctrl))
            else:
                responseToCMD = invalidNumberOfArgumentsMessage 
        elif clientMsgParsed[0] == "setGainTX":
            if len(clientMsgParsed) == 5:
                self.print(clientMsgParsed[1], thr=2)
                
                tx_bb_gain = int(clientMsgParsed[1])
                tx_bb_phase = int(clientMsgParsed[2])
                tx_bb_iq_gain = int(clientMsgParsed[3])
                tx_bfrf_gain = int(clientMsgParsed[4])
                
                success,status = self.siversControllerObj.setGainTX(tx_bb_gain, tx_bb_phase, tx_bb_iq_gain, tx_bfrf_gain)
                if success == True:
                    responseToCMD = successMessage 
                else:
                    responseToCMD = status                  
            else:
                responseToCMD = invalidNumberOfArgumentsMessage   
        elif clientMsgParsed[0] == "getCarrierFrequency":
            if len(clientMsgParsed) == 1:
                responseToCMD = str(self.siversControllerObj.getFrequency())
            else:
                responseToCMD = invalidNumberOfArgumentsMessage 
        elif clientMsgParsed[0] == "setCarrierFrequency":
            if len(clientMsgParsed) == 2:
                self.print(clientMsgParsed[1], thr=2)
                fc = float(clientMsgParsed[1])
                success, status = self.siversControllerObj.setFrequency(fc)
                if success == True:
                    responseToCMD = successMessage 
                else:
                    responseToCMD = status 
            else:
                responseToCMD = invalidNumberOfArgumentsMessage
                
        #######################
        else:
            responseToCMD = invalidCommandMessage
        
        responseToCMDInBytes = str.encode(responseToCMD + " (" + clientMsg + ")" )  
        return responseToCMDInBytes
    

    def allocate_input(self, n_frame=1):
        size = self.n_rx_ant * n_frame * self.n_samples * 2
        if 'ddr4' in self.project:
            self.adc_rx_buffer = allocate(shape=(size,), target=self.ol.ddr4_0, dtype=np.int16)
            # self.adc_rx_buffer = allocate(shape=(size,), dtype=np.int16)
        else:
            self.adc_rx_buffer = allocate(shape=(size,), dtype=np.int16)
        self.print("Input buffers allocation done", thr=1)


    def allocate_output(self, n_frame=1):
        size = self.n_tx_ant * n_frame * self.n_samples * 2
        self.dac_tx_buffer = allocate(shape=(size,), dtype=np.int16)
        self.print("Output buffers allocation done", thr=1)


    def gpio_init(self):
        self.gpio_dic = {}

        if 'ddr4' in self.project:
            if self.board=='rfsoc_2x2':
                self.gpio_dic['lmk_reset'] = GPIO(GPIO.get_gpio_pin(84), 'out')
            elif self.board=='rfsoc_4x2':
                self.gpio_dic['lmk_reset'] = GPIO(GPIO.get_gpio_pin(-78+7), 'out')
            self.gpio_dic['dac_mux_sel'] = GPIO(GPIO.get_gpio_pin(3), 'out')
            self.gpio_dic['adc_enable'] = GPIO(GPIO.get_gpio_pin(34), 'out')
            self.gpio_dic['dac_enable'] = GPIO(GPIO.get_gpio_pin(2), 'out')
            self.gpio_dic['adc_reset'] = GPIO(GPIO.get_gpio_pin(32), 'out')
            self.gpio_dic['dac_reset'] = GPIO(GPIO.get_gpio_pin(0), 'out')
            self.gpio_dic['led'] = GPIO(GPIO.get_gpio_pin(80), 'out')
        else:
            self.gpio_dic['dac_mux_sel'] = GPIO(GPIO.get_gpio_pin(0), 'out')
            self.gpio_dic['adc_enable'] = GPIO(GPIO.get_gpio_pin(3), 'out')
            self.gpio_dic['dac_enable'] = GPIO(GPIO.get_gpio_pin(1), 'out')
            self.gpio_dic['adc_reset'] = GPIO(GPIO.get_gpio_pin(2), 'out')
            self.gpio_dic['dac_reset'] = GPIO(GPIO.get_gpio_pin(4), 'out')

        if 'ddr4' in self.project:
            self.gpio_dic['led'].write(0)
            self.gpio_dic['dac_mux_sel'].write(1)
            self.gpio_dic['adc_enable'].write(0)
            self.gpio_dic['dac_enable'].write(0)
            self.gpio_dic['adc_reset'].write(1)
            self.gpio_dic['dac_reset'].write(1)
        else:
            self.gpio_dic['dac_mux_sel'].write(0)
            self.gpio_dic['adc_enable'].write(0)
            self.gpio_dic['dac_enable'].write(0)
            self.gpio_dic['adc_reset'].write(0)
            self.gpio_dic['dac_reset'].write(0)

        self.print("PS-PL GPIOs initialization done", thr=1)


    def clock_init(self):
        if 'ddr4' in self.project:
            self.gpio_dic['lmk_reset'].write(1)
            self.gpio_dic['lmk_reset'].write(0)

        xrfclk.set_ref_clks(lmk_freq=self.lmk_freq_mhz, lmx_freq=self.lmx_freq_mhz)
        self.print("Xrfclk initialization done", thr=1)


    def verify_clock_tree(self):
        if 'ddr4' in self.project:
            status = self.ol.clocktreeMTS.clk_wiz_0.read(self.CLOCKWIZARD_LOCK_ADDRESS)
            if (status != 1):
                raise Exception("The MTS ClockTree has failed to LOCK. Please verify board clocking configuration")
        self.print("Verifying clock tree done", thr=1)


    def init_rfdc(self):
        self.rfdc = self.ol.usp_rf_data_converter_0
        self.print("RFDC initialization done", thr=1)


    def init_tile_sync(self):
        dacTiles = min(self.dac_tiles_sync_hex, 0x1)
        adcTiles = min(self.adc_tiles_sync_hex, 0x1)
        self.sync_tiles(dacTiles=dacTiles, adcTiles=adcTiles)
        self.ol.clocktreeMTS.clk_wiz_0.mmio.write_reg(self.CLOCKWIZARD_RESET_ADDRESS, self.CLOCKWIZARD_RESET_TOKEN)
        time.sleep(0.1)

        # for id in self.dac_tile_block_dic:
        for id in list(set(list(self.dac_tile_block_dic.keys()) + self.dac_tiles_sync)):
            self.rfdc.dac_tiles[id].Reset()

        for toggleValue in range(0,1):
            # for id in self.adc_tile_block_dic:
            for id in list(set(list(self.adc_tile_block_dic.keys()) + self.adc_tiles_sync)):
                self.rfdc.adc_tiles[id].SetupFIFO(toggleValue)
        self.print("Tiles sync initialization done", thr=1)
    

    def sync_tiles(self, dacTiles = 0, adcTiles = 0):
        self.rfdc.mts_dac_config.RefTile = 0  # MTS starts at DAC Tile 228
        self.rfdc.mts_adc_config.RefTile = 0  # MTS starts at ADC Tile 224
        self.rfdc.mts_dac_config.Target_Latency = -1
        self.rfdc.mts_adc_config.Target_Latency = -1
        if dacTiles > 0:
            self.rfdc.mts_dac_config.Tiles = dacTiles # group defined in binary 0b1111
            self.rfdc.mts_dac_config.SysRef_Enable = 1
            self.rfdc.mts_dac()
        else:
            self.rfdc.mts_dac_config.Tiles = 0x0
            self.rfdc.mts_dac_config.SysRef_Enable = 0

        if adcTiles > 0:
            self.rfdc.mts_adc_config.Tiles = adcTiles
            self.rfdc.mts_adc_config.SysRef_Enable = 1
            self.rfdc.mts_adc()
        else:
            self.rfdc.mts_adc_config.Tiles = 0x0
            self.rfdc.mts_adc_config.SysRef_Enable = 0
        self.print("Tiles sync done", thr=1)
    

    def init_dac(self):
        self.dac_tile = self.rfdc.dac_tiles[self.dac_tile_id]
        self.dac_block = self.dac_tile.blocks[self.dac_block_id]

        if 'sounder_if' in self.project and not 'ddr4' in self.project:
            # self.dac_tile.Reset()
            # self.dac_tile.SetupFIFO(True)

            for id in self.dac_tile_block_dic:
                self.rfdc.dac_tiles[id].Reset()
            for id in self.dac_tile_block_dic:
                self.rfdc.dac_tiles[id].SetupFIFO(True)
        self.print("DAC init and reset done", thr=1)


    def init_adc(self):
        self.adc_tile = self.rfdc.adc_tiles[self.adc_tile_id]
        self.adc_block = self.adc_tile.blocks[self.adc_block_id]

        if 'sounder_if' in self.project and not 'ddr4' in self.project:
            # # self.adc_tile.Reset()
            # # self.adc_tile.SetupFIFO(True)
            # for toggleValue in range(0, 1):
            #     self.adc_tile.SetupFIFO(toggleValue)

            # for id in self.adc_tile_block_dic:
            #     self.rfdc.adc_tiles[id].Reset()
            for toggleValue in range(0,1):
                for id in self.adc_tile_block_dic:
                    self.rfdc.adc_tiles[id].SetupFIFO(toggleValue)
        self.print("ADC init and reset done", thr=1)


    def set_dac_mixer(self):
        cofig_str = 'DAC configs: mix_freq: {:.2e}, mix_phase_off: {:.2f}'.format(self.mix_freq_dac, self.mix_phase_off)
        cofig_str += ', DynamicPLLConfig: ' + str(self.DynamicPLLConfig)
        cofig_str += ', do_mixer_settings: ' + str(self.do_mixer_settings)
        self.print(cofig_str, thr=2)

        if self.do_pll_settings:
            self.dac_tile.DynamicPLLConfig(self.DynamicPLLConfig[0], self.DynamicPLLConfig[1], self.DynamicPLLConfig[2])
        # print(self.rfdc.dac_tiles[self.dac_tile_id].blocks[self.dac_block_id].MixerSettings)
        if self.do_mixer_settings:
            self.dac_block.MixerSettings['Freq'] = self.mix_freq_dac/1e6
            self.dac_block.MixerSettings['PhaseOffset'] = self.mix_phase_off
            # self.dac_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_IMMEDIATE
            self.dac_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_TILE
            self.dac_block.UpdateEvent(xrfdc.EVNT_SRC_TILE)

        self.print("DAC Mixer Settings done", thr=1)


    def set_adc_mixer(self):
        cofig_str = 'ADC configs: mix_freq: {:.2e}, mix_phase_off: {:.2f}'.format(self.mix_freq_adc, self.mix_phase_off)
        cofig_str += ', DynamicPLLConfig: ' + str(self.DynamicPLLConfig)
        cofig_str += ', do_mixer_settings: ' + str(self.do_mixer_settings)
        self.print(cofig_str, thr=2)

        if self.do_pll_settings:
            self.adc_tile.DynamicPLLConfig(self.DynamicPLLConfig[0], self.DynamicPLLConfig[1], self.DynamicPLLConfig[2])
        # print(self.rfdc.adc_tiles[self.adc_tile_id].blocks[self.adc_block_id].MixerSettings)
        # attributes = dir(self.rfdc.adc_tiles[self.adc_tile_id].blocks[self.adc_block_id].MixerSettings)
        # for name in attributes:
        #     print(name)
        if self.do_mixer_settings:
            # self.adc_block.NyquistZone = 1
            # self.adc_block.MixerSettings = {
            #     'CoarseMixFreq'  : xrfdc.COARSE_MIX_BYPASS,
            #     'EventSource'    : xrfdc.EVNT_SRC_TILE,
            #     'FineMixerScale' : xrfdc.MIXER_SCALE_1P0,
            #     'Freq'           : -1*mix_freq/1e6,
            #     'MixerMode'      : xrfdc.MIXER_MODE_R2C,
            #     'MixerType'      : xrfdc.MIXER_TYPE_FINE,
            #     'PhaseOffset'    : 0.0
            # }
            self.adc_block.MixerSettings['Freq'] = -1*self.mix_freq_adc/1e6
            self.adc_block.MixerSettings['PhaseOffset'] = self.mix_phase_off
            # self.adc_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_IMMEDIATE
            self.adc_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_TILE
            # self.adc_block.UpdateEvent(xrfdc.EVENT_MIXER)
            self.adc_block.UpdateEvent(xrfdc.EVNT_SRC_TILE)
            # self.adc_block.MixerSettings['Freq'] = -1*self.mix_freq_adc/1e6
        
        self.print("ADC Mixer Settings done", thr=1)


    def dma_init(self):
        if 'ddr4' in self.project:
            self.ol.dac_path.axi_dma_0.set_up_tx_channel()
            self.dma_tx = self.ol.dac_path.axi_dma_0.sendchannel
        else:
            self.dma_tx = self.ol.TX_loop.axi_dma_tx.sendchannel
        self.print("TX DMA setup done", thr=1)

        if 'ddr4' in self.project:
            self.ol.adc_path.axi_dma_0.set_up_rx_channel()
            self.dma_rx = self.ol.adc_path.axi_dma_0.recvchannel
            self.rx_reg = self.ol.adc_path.axis_flow_ctrl_0
        else:
            self.dma_rx = self.ol.RX_Logic.axi_dma_rx.recvchannel
        self.print("RX DMA setup done", thr=1)


    def load_data_to_tx_buffer(self, txtd):
        self.txtd = txtd
        txtd_dac = self.txtd * (2 ** (self.dac_bits + 1) - 1)

        if 'sounder_if' in self.project:
            txtd_dac_interleaved = np.zeros(np.prod(txtd_dac.shape)*2, dtype='int16').reshape(-1, self.n_par_strms_tx//2, 2)
            for i in range(self.n_tx_ant):
                txtd_dac_ant = txtd_dac[i].reshape(-1,self.n_par_strms_tx//2)
                if self.tx_mode==1:
                    txtd_dac_interleaved[i::self.n_tx_ant,:,0] = np.int16(txtd_dac_ant.real)
                    txtd_dac_interleaved[i::self.n_tx_ant,:,1] = np.int16(txtd_dac_ant.imag)
                elif self.tx_mode==2:
                    txtd_dac_interleaved[i::self.n_tx_ant,:,0] = np.int16(txtd_dac_ant.imag)
                    txtd_dac_interleaved[i::self.n_tx_ant,:,1] = np.int16(txtd_dac_ant.real)
                else:
                    raise ValueError('Unsupported TX mode: %d' %(self.tx_mode))
            
        else:
            txtd_dac = txtd_dac.reshape(txtd_dac.shape[0], -1, self.n_par_strms_tx)
            txtd_dac_interleaved = np.zeros((np.prod(txtd_dac.shape)*2//self.n_par_strms_tx, self.n_par_strms_tx), dtype='int16')
            for i in range(self.n_tx_ant):
                if self.tx_mode==1:
                    txtd_dac_interleaved[i*2::self.n_tx_ant*2,:] = np.int16(txtd_dac[i].real)
                    txtd_dac_interleaved[i*2+1::self.n_tx_ant*2,:] = np.int16(txtd_dac[i].imag)
                elif self.tx_mode==2:
                    txtd_dac_interleaved[i*2::self.n_tx_ant*2,:] = np.int16(txtd_dac[i].imag)
                    txtd_dac_interleaved[i*2+1::self.n_tx_ant*2,:] = np.int16(txtd_dac[i].real)
                else:
                    raise ValueError('Unsupported RX mode: %d' %(self.rx_mode))

        self.dac_tx_buffer[:] = txtd_dac_interleaved.flatten()[:]

        self.print("Loading txtd data to DAC TX buffer done", thr=1)


    def load_data_from_rx_buffer(self):
        rx_data = np.array(self.adc_rx_buffer).astype('int16') / (2 ** (self.adc_bits + 1) - 1)
        self.rxtd = []
        
        rx_data = rx_data.reshape(-1, self.n_par_strms_rx)
        for i in range(self.n_rx_ant):
            if self.rx_mode==1:
                rx_data_ant = rx_data[i*2::self.n_rx_ant*2,:] + 1j * rx_data[i*2+1::self.n_rx_ant*2,:]
            elif self.rx_mode==2:
                rx_data_ant = rx_data[i*2+1::self.n_rx_ant*2,:] + 1j * rx_data[i*2::self.n_rx_ant*2,:]
            else:
                raise ValueError('Unsupported RX mode: %d' %(self.rx_mode))
            self.rxtd.append(rx_data_ant.flatten())
        
        self.rxtd = np.array(self.rxtd)
        self.print("Loading rxtd data from ADC RX buffer done", thr=5)


    def send_frame(self, txtd):
        self.load_data_to_tx_buffer(txtd)

        self.gpio_dic['dac_mux_sel'].write(0)
        self.gpio_dic['dac_enable'].write(0)
        if 'ddr4' in self.project:
            self.gpio_dic['dac_reset'].write(1)  # Reset ON
        else:
            self.gpio_dic['dac_reset'].write(0)
        time.sleep(0.5)
        if 'ddr4' in self.project:
            self.gpio_dic['dac_reset'].write(0)  # Reset OFF
        else:
            self.gpio_dic['dac_reset'].write(1)
        self.dma_tx.transfer(self.dac_tx_buffer)
        self.dma_tx.wait()
        self.gpio_dic['dac_mux_sel'].write(1)
        self.gpio_dic['dac_enable'].write(1)

        # self.dma_tx.wait()
        time.sleep(0.1)
        self.print("Frame sent via DAC", thr=1)


    def recv_frame_one(self, n_frame=1):
        # if 'ddr4' in self.project:
        #     self.gpio_dic['led'].write(1)
        if 'ddr4' in self.project:
            # Suspicous code
            self.rx_reg.write(0, self.n_rx_ant * self.n_samples // self.n_par_strms_rx)
            # self.rx_reg.write(0, self.n_samples // self.n_par_strms_rx)
            self.rx_reg.write(4, self.n_skip // self.n_par_strms_rx)
            self.rx_reg.write(8, self.n_rx_ant * n_frame * self.n_samples * 4)      # Must have self.n_rx_ant multiplier to work correctly

            self.gpio_dic['adc_reset'].write(0)
        else:
            self.gpio_dic['adc_enable'].write(0)
            self.gpio_dic['adc_reset'].write(0)  # Reset ON
            time.sleep(0.01)
            self.gpio_dic['adc_reset'].write(1)  # Reset OFF

        self.dma_rx.transfer(self.adc_rx_buffer)
        self.gpio_dic['adc_enable'].write(1)
        self.dma_rx.wait()

        self.gpio_dic['adc_enable'].write(0)

        if 'ddr4' in self.project:
            self.gpio_dic['adc_reset'].write(1)
        else:
            self.gpio_dic['adc_reset'].write(0)

        self.load_data_from_rx_buffer()
        # if 'ddr4' in self.project:
        #     self.gpio_dic['led'].write(0)
        self.print("Frames received from ADC", thr=5)

        return self.rxtd
    

    def recv_frame(self, n_frame=1):
        rxtd = np.zeros((len(self.beam_test), self.n_rx_ant*n_frame*self.n_samples), dtype='complex')

        for i, beam_index in enumerate(self.beam_test):
            if self.RFFE=='sivers':
                self.siversControllerObj.setBeamIndexRX(beam_index)
            self.recv_frame_one(n_frame=n_frame)
            rxtd[i,:] = self.rxtd.flatten()

        rxfd = fft(rxtd, axis=1)
        rxfd = np.roll(rxfd, 1, axis=1)
        Hest = rxfd * np.conj(self.txfd)
        hest = ifft(Hest, axis=1)
        hest = hest.flatten()
        # re = hest.real.astype(np.int16)
        # im = hest.imag.astype(np.int16)

        self.print("Frames received from ADC", thr=5)

        # return np.concatenate((re, im))
        return hest


