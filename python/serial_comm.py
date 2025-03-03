from backend import *
from backend import be_np as np, be_scp as scipy
from SigProc_Comm.general import General





class Serial_Comm(General):
    def __init__(self, params):
        """
        Initialize the connection to the Target.

        :param port: The COM port to connect to (default: 'COM6').
        :param baudrate: The communication baud rate (default: 115200).
        :param timeout: Read timeout in seconds (default: 1).
        """

        super().__init__(params)

        self.port = getattr(params, 'port', 'COM6')
        self.baudrate = getattr(params, 'baudrate', 115200)
        self.timeout = getattr(params, 'timeout', 1)
        self.client = None

        self.print("Serial_Comm Client object created", thr=1)


    def connect(self):
        """Establish a connection to the target."""
        self.client = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        time.sleep(1)  # Wait for target to reset
        if self.client.is_open:
            self.print("Client serial connected!", thr=1)
        else:
            self.print("Client serial connection failed.", thr=0)


    def close(self):
        """Close the connection to the Target."""
        if self.client and self.client.is_open:
            self.client.close()
            self.print("Client serial closed", thr=1)


    def __del__(self):
        self.close()
        self.print("Client object deleted", thr=1)


    def write(self, data):
        """
        Send data to the Target.

        :param data: The string data to send.
        """
        if self.client and self.client.is_open:
            self.client.write(data.encode())  # Convert string to bytes
            self.print("Finished writing to the Serial target", thr=5)


    def read_lines(self, max_lines=None, termination_signal="END"):
        """
        Read multiple lines of data from the Target.

        :param max_lines: Maximum number of lines to read (optional).
        :param termination_signal: A specific message that signals the end of the response.
        :return: A list of lines read from the Target.
        """
        responses = []
        lines_read = 0
        while True:
            if self.client.in_waiting > 0:  # Check if there is data to read
                line = self.client.readline().decode('utf-8').strip()  # Decode bytes to string
                responses.append(line)
                self.print(f"Target: {line}", thr=5)  # Debugging: print to console

                lines_read += 1
                if max_lines and lines_read >= max_lines:
                    break
                if line == termination_signal:  # Stop if termination signal is received
                    break
        self.print("Finished reading from the Serial target", thr=5)
        return responses



class Serial_Comm_TurnTable(Serial_Comm):
    def __init__(self, params):
        """
        Initialize the connection to the Arduino.

        :param port: The COM port to connect to (default: 'COM6').
        :param baudrate: The communication baud rate (default: 115200).
        :param timeout: Read timeout in seconds (default: 1).
        """
        params = params.copy()
        params.port = getattr(params, 'turntable_port', 'COM6')
        params.baudrate = getattr(params, 'turntable_baudrate', 115200)
        params.timeout = getattr(params, 'turntable_timeout', 1)
        super().__init__(params)

        self.print("Serial_Comm_TurnTable Client object created", thr=1)

        # self.connect()


    def return2home(self):
        self.print("Homing procedure..", thr=2)
        self.print("Homing procedure done.", thr=2)


    def move_to_position(self, position):
        self.print(f"Moving to position: {position}", thr=2)
        command = "moveToAngle=" + str(position)
        self.write(command)
        responses = self.read_lines(max_lines=1)
        # block until position is reached:
        isReady = False
        while not isReady:
            if (responses[-1] == "done."):
                isReady = True
            else:
                self.print('waiting..', thr=3)
                time.sleep(0.1)
                responses = self.read_lines(max_lines=1)





