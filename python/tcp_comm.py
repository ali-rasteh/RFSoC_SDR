from backend import *
from backend import be_np as np, be_scp as scipy
from general import General




class Tcp_Comm(General):
    def __init__(self, params):
        super().__init__(params)

        self.server_ip = getattr(params, 'server_ip', '0.0.0.0')
        self.TCP_port_Cmd = getattr(params, 'TCP_port_Cmd', 8080)
        self.TCP_port_Data = getattr(params, 'TCP_port_Data', 8081)
        self.tcp_localIP = getattr(params, 'tcp_localIP', '0.0.0.0')
        self.tcp_bufferSize = getattr(params, 'tcp_bufferSize', 2**10)
        self.after_idle_sec = 1
        self.interval_sec = 3
        self.max_fails = 5

        self.nbytes = 2

        self.print("Tcp_Comm object init done", thr=5)

    def close(self):
        self.radio_control.close()
        self.radio_data.close()
        self.print("Client object closed", thr=1)

    def __del__(self):
        self.close()
        self.print("Client object deleted", thr=1)

    def init_tcp_server(self):
        ## TCP Server
        self.print("Starting TCP server", thr=1)
        
        ## Command
        self.TCPServerSocketCmd = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)# Create a datagram socket
        self.TCPServerSocketCmd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.TCPServerSocketCmd.bind((self.tcp_localIP, self.TCP_port_Cmd)) # Bind to address and ip
        
        ## Data
        self.TCPServerSocketData = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)         # Create a datagram socket
        self.TCPServerSocketData.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.TCPServerSocketData.bind((self.tcp_localIP, self.TCP_port_Data))                # Bind to address and ip

        bufsize = self.TCPServerSocketData.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) 
        # self.print ("Buffer size [Before]:%d" %bufsize, thr=2)
        self.print("TCP server is up", thr=1)
    
    def run_tcp_server(self, call_back_func):
        # Listen for incoming connections
        self.TCPServerSocketCmd.listen(1)
        self.TCPServerSocketData.listen(1)
        
        while True:
            # Wait for a connection
            self.print('\nWaiting for a connection', thr=2)
            self.connectionCMD, addrCMD = self.TCPServerSocketCmd.accept()
            self.connectionData, addrDATA = self.TCPServerSocketData.accept()
            self.print('\nConnection established', thr=2)
            
            
            self.connectionData.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.connectionData.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, self.after_idle_sec)
            self.connectionData.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, self.interval_sec)
            self.connectionData.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, self.max_fails)
            
            self.connectionCMD.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.connectionCMD.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, self.after_idle_sec)
            self.connectionCMD.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, self.interval_sec)
            self.connectionCMD.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, self.max_fails)            
            
            try:
                while True:
                    try:
                        receivedCMD = self.connectionCMD.recv(self.tcp_bufferSize)
                        if receivedCMD:
                            self.print("\nClient CMD:{}".format(receivedCMD.decode()), thr=5)
                            responseToCMDinBytes = call_back_func(receivedCMD)
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

    def init_tcp_client(self):
        self.radio_control = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.radio_control.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.radio_control.connect((self.server_ip, self.TCP_port_Cmd))

        self.radio_data = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.radio_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.radio_data.connect((self.server_ip, self.TCP_port_Data))

        self.print("Client succesfully connected to the server", thr=1)



class Tcp_Comm_RFSoC(Tcp_Comm):
    def __init__(self, params):
        params.server_ip = params.rfsoc_server_ip
        super().__init__(params)

        self.fc = params.fc
        self.beam_test = params.beam_test
        self.adc_bits = params.adc_bits
        self.dac_bits = params.dac_bits
        self.RFFE = params.RFFE
        self.n_frame_rd = params.n_frame_rd
        self.n_samples = params.n_samples
        self.n_tx_ant = params.n_tx_ant
        self.n_rx_ant = params.n_rx_ant

        if self.RFFE=='sivers':
            self.tx_bb_gain = 0x3
            self.tx_bb_phase = 0x0
            self.tx_bb_iq_gain = 0x77
            self.tx_bfrf_gain = 0x7F
            self.rx_gain_ctrl_bb1 = 0x33
            self.rx_gain_ctrl_bb2 = 0x00
            self.rx_gain_ctrl_bb3 = 0x33
            self.rx_gain_ctrl_bfrf = 0x7F

        self.nread = self.n_rx_ant * self.n_frame_rd * self.n_samples

        self.print("Tcp_Comm_RFSoC object init done", thr=1)

    def set_mode(self, mode):
        if mode == 'RXen0_TXen1' or mode == 'RXen1_TXen0' or mode == 'RXen0_TXen0':
            self.radio_control.sendall(b"setModeSiver "+str.encode(str(mode)))
            data = self.radio_control.recv(1024)
            self.print("Result of set_mode: {}".format(data),thr=1)
            return data
        
    def set_frequency(self, fc):
        self.radio_control.sendall(b"setCarrierFrequency "+str.encode(str(fc)))
        data = self.radio_control.recv(1024)
        self.print("Result of set_frequency: {}".format(data),thr=1)
        return data

    def set_tx_gain(self):
        self.radio_control.sendall(b"setGainTX " + str.encode(str(int(self.tx_bb_gain)) + " ") \
                                                    + str.encode(str(int(self.tx_bb_phase)) + " ") \
                                                    + str.encode(str(int(self.tx_bb_iq_gain)) + " ") \
                                                    + str.encode(str(int(self.tx_bfrf_gain))))
        data = self.radio_control.recv(1024)
        self.print("Result of set_tx_gain: {}".format(data),thr=1)
        return data

    def set_rx_gain(self):
        self.radio_control.sendall(b"setGainRX " + str.encode(str(int(self.rx_gain_ctrl_bb1)) + " ") \
                                                    + str.encode(str(int(self.rx_gain_ctrl_bb2)) + " ") \
                                                    + str.encode(str(int(self.rx_gain_ctrl_bb3)) + " ") \
                                                    + str.encode(str(int(self.rx_gain_ctrl_bfrf))))
        data = self.radio_control.recv(1024)
        self.print("Result of set_rx_gain: {}".format(data),thr=1)
        return data

    def transmit_data(self):
        self.radio_control.sendall(b"transmitSamples")
        data = self.radio_control.recv(1024)
        self.print("Result of transmit_data: {}".format(data),thr=1)
        return data

    def receive_data(self, mode='once'):
        if mode=='once':
            nbeams = 1
            self.radio_control.sendall(b"receiveSamplesOnce")
        elif mode=='beams':
            nbeams = len(self.beam_test)
            self.radio_control.sendall(b"receiveSamples")
        nbytes = nbeams * self.nbytes * self.nread * 2
        buf = bytearray()

        while len(buf) < nbytes:
            data = self.radio_data.recv(nbytes)
            buf.extend(data)
        data = np.frombuffer(buf, dtype=np.int16)
        data = data/(2 ** (self.adc_bits + 1) - 1)
        rxtd = data[:self.nread*nbeams] + 1j*data[self.nread*nbeams:]
        rxtd = rxtd.reshape(nbeams, self.n_rx_ant, self.nread//self.n_rx_ant)
        return rxtd
    


class Tcp_Comm_LinTrack(Tcp_Comm):
    def __init__(self, params):
        params.server_ip = params.lintrack_server_ip
        super().__init__(params)

        self.print("Tcp_Comm_LinTrack object init done", thr=1)

    def move(self, distance=0.0):
        self.radio_control.sendall(b"Move "+str.encode(str(distance)))
        data = self.radio_control.recv(1024)
        self.print("Result of move_forward: {}".format(data), thr=1)
        return data
    
    def return2home(self):
        self.radio_control.sendall(b"Return2home")
        data = self.radio_control.recv(1024)
        self.print("Result of Return2home: {}".format(data), thr=1)
        return data
    
    def go2end(self):
        self.radio_control.sendall(b"Go2end")
        data = self.radio_control.recv(1024)
        self.print("Result of Go2end: {}".format(data), thr=1)
        return data

    

class ssh_Com(General):
    def __init__(self, params):
        super().__init__(params)

        self.host = getattr(params, 'host', '0.0.0.0')
        self.port = getattr(params, 'port', 22)
        self.username = getattr(params, 'username', 'root')
        self.password = getattr(params, 'password', ' root')

        self.print("ssh_Com object init done", thr=1)


    def init_ssh_client(self):
        try:
            # Initialize SSH client
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the remote server
            self.client.connect(hostname=self.host, port=self.port, username=self.username, password=self.password)

        except paramiko.AuthenticationException:
            print("Authentication failed. Please check your credentials.")
        except paramiko.SSHException as e:
            print(f"SSH Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        self.print("ssh_Com client init done", thr=1)


    def close(self):
        self.client.close()
        self.print("SSH Client object closed", thr=1)


    def __del__(self):
        self.close()
        self.print("SSH Client object deleted", thr=1)


    def exec_command(self, command, verif_keyword='done'):
        # Execute the command
        stdin, stdout, stderr = self.client.exec_command(command)

        # Capture command output and errors
        output = stdout.read().decode()
        errors = stderr.read().decode()

        if errors:
            self.print(f"Error: {errors}", thr=3)
        else:
            self.print(f"Command Output:\n{output}", thr=3)

        # Search for the keyword in the output
        if verif_keyword in output:
            self.print(f"Keyword '{verif_keyword}' found in the output.", thr=3)
            result = True
        else:
            self.print(f"Keyword '{verif_keyword}' not found in the output.", thr=3)
            result = False

        return result
    


class ssh_Com_Piradio(ssh_Com):
    def __init__(self, params):
        params.host = params.piradio_host
        params.port = params.piradio_port
        params.username = params.piradio_username
        params.password = params.piradio_password
        super().__init__(params)

        self.print("ssh_Com_Piradio object init done", thr=1)


    def set_frequency(self, fc=6.0e9, verif_keyword='done'):
        command = f"ls"
        result = self.exec_command(command, verif_keyword=verif_keyword)
        if result:
            self.print(f"Frequency set to {fc/1e9} GHz", thr=3)
        else:
            self.print(f"Failed to set frequency to {fc/1e9} GHz", thr=0)
