from backend import *
from tcp_comm import Tcp_Comm_LinTrack
from general import General



class Params_Class(object):
    def __init__(self):
        # parser = argparse.ArgumentParser()
        # parser.add_argument("--output_mode", type=str, default="dc", help="Type of the Raspberry Pi hat output to use")
        # parser.add_argument("--lintrack_server_ip", type=str, default="0.0.0.0", help="TCP server IP")
        # parser.add_argument("--dis_per_rev", type=int, default=8, help="Distance on the linear track per stepper motor revolution")
        # parser.add_argument("--pulse_per_rev", type=int, default=400, help="Pulse needed on the logic for each revolution of the stepper motor")
        # parser.add_argument("--pulse_freq", type=float, default=1600, help="Pulse frequency of the logic circuit")
        # parser.add_argument("--plot_level", type=int, default=0, help="level of plotting outputs")
        # parser.add_argument("--verbose_level", type=int, default=0, help="level of printing output")
        # parser.add_argument("--run_tcp_server", action="store_true", default=False, help="If true, runs the TCP server")
        # params = parser.parse_args()
        params = SimpleNamespace()
        params.overwrite_configs=True

        if params.overwrite_configs:
            self.output_mode = 'dc'
            self.tcp_localIP = "0.0.0.0"
            self.tcp_bufferSize=2**10
            self.TCP_port_Cmd=8080
            self.TCP_port_Data=8081
            self.seed=100
            self.run_tcp_server=True
            self.position_file_path = os.path.join(os.getcwd(), 'position.txt')
            self.dis_coeff = 0.972
            self.overhead_time = 0.0018+0.0061+0.0001
            self.lintrack_server_ip = '0.0.0.0'
            
            self.dis_per_rev = 8
            self.pulse_per_rev = 400
            self.pulse_freq = 1600
            self.verbose_level = 5
            self.plot_level = 5




class LinearTrack(General):
    def __init__(self, params):
        super().__init__(params)

        self.run_tcp_server = params.run_tcp_server
        self.output_mode = params.output_mode
        self.dis_per_rev = params.dis_per_rev
        self.pulse_per_rev = params.pulse_per_rev
        self.pulse_freq = params.pulse_freq
        self.dis_coeff = params.dis_coeff
        self.overhead_time = params.overhead_time
        self.position_file_path = params.position_file_path
        self.total_length = 1500      # length of the linear track in mm
        self.plate_length = 125
        self.travel_length = self.total_length - self.plate_length
        self.margin2edge = 5

        self.travel_length -= 2*self.margin2edge

        if self.output_mode == 'stepper':
            self.kit = stepper.StepperMotor(microsteps=2)
        elif self.output_mode == 'dc':
            self.kit = MotorKit(i2c=board.I2C(), pwm_frequency = self.pulse_freq)

        self.pulse_pwm = self.kit.motor1
        self.direction_out = self.kit.motor3

        self.reset()

        self.position = self.read_position()
        
        if self.run_tcp_server:
            self.tcp_comm = Tcp_Comm_LinTrack(params)
            self.tcp_comm.init_tcp_server()


    def run_tcp(self):
        self.print("Running TCP server", thr=1)
        self.tcp_comm.run_tcp_server(self.parse_and_execute)


    def parse_and_execute(self, receivedCMD):
        clientMsg = receivedCMD.decode()
        invalidCommandMessage = "ERROR: Invalid command"
        invalidNumberOfArgumentsMessage = "ERROR: Invalid number of arguments"
        successMessage = "Successully executed"
        droppedMessage = "Connection dropped?"
        clientMsgParsed = clientMsg.split()

        if clientMsgParsed[0] == "Move":
            if len(clientMsgParsed) == 2:
                self.print(clientMsgParsed[1], thr=2)
                distance = float(clientMsgParsed[1])
                success, status = self.displace(distance)
                if success == True:
                    responseToCMD = successMessage 
                else:
                    responseToCMD = status 
            else:
                responseToCMD = invalidNumberOfArgumentsMessage

        elif clientMsgParsed[0] == "Return2home":
            if len(clientMsgParsed) == 1:
                success, status = self.return2home()
                if success == True:
                    responseToCMD = successMessage 
                else:
                    responseToCMD = status 
            else:
                responseToCMD = invalidNumberOfArgumentsMessage

        elif clientMsgParsed[0] == "Go2end":
            if len(clientMsgParsed) == 1:
                success, status = self.go2end()
                if success == True:
                    responseToCMD = successMessage 
                else:
                    responseToCMD = status 
            else:
                responseToCMD = invalidNumberOfArgumentsMessage

        else:
            responseToCMD = invalidCommandMessage
        
        responseToCMDInBytes = str.encode(responseToCMD + " (" + clientMsg + ")" )  
        return responseToCMDInBytes


    def calibrate(self, mode='start'):
        self.print("Calibrating the linear track with mode {}".format(mode), thr=1)
        while True:
            dis = float(input("Enter the distance to move in mm: "))
            if dis == 0:
                if mode == 'start':
                    self.position = 0.0
                elif mode == 'end':
                    self.position = self.travel_length
                self.write_position(self.position)
                break
            self.displace(dis, pos_check=False)

        self.print("Calibration complete", thr=1)

    
    def interactive_move(self):
        self.print("Starting interactive move", thr=1)
        while True:
            dis = float(input("Enter the distance to move in mm: "))
            if dis == 0:
                break
            self.displace(dis)


    def read_position(self):
        with open(self.position_file_path,'r') as f:
            self.position = float(f.readline(4))
        return self.position


    def write_position(self, position):
        with open(self.position_file_path,'w') as f:
            f.write(str(position))


    def set_direction(self, direction='forward'):
        if direction=='forward':
            self.direction_out.throttle = 0.0
        elif direction=='backward':
            self.direction_out.throttle = 1.0
    

    def move(self, move_time=0.0):
        self.pulse_pwm.throttle = 0.5
        sleep_time = max(move_time-self.overhead_time, 0.0)
        time.sleep(sleep_time)
        self.stop()

    # def move(self, move_time=0.1):
    #     for i in range(int(move_time/delay)):
    #         kit.stepper1.onestep(style=stepper.DOUBLE)
    #         step_motor.onestep(style=stepper.DOUBLE)
    #         time.sleep(delay)
    

    def dis2time(self, dis=0.0):
        dis = self.dis_coeff * dis
        t = dis * (self.pulse_per_rev) / (self.pulse_freq * self.dis_per_rev)
        return t


    def time2dis(self, t=0.0):
        dis = t * (self.pulse_freq * self.dis_per_rev) / (self.pulse_per_rev)
        dis = dis / self.dis_coeff
        return dis


    def position_check(self, dis=0.0):
        """
        The position valye is maintained and stored to keep track 
        of where the linear track's gantry plate is positioned and can
        be used to bring the plate back to home position(if needed)
        """
        position = self.position + dis
        if position > self.travel_length or position < 0:
            raise Exception("Gantry plate already at the edge")
            success = False
        else:
            success = True

        self.print(f"The new distance from home is {position}mm", thr=2)
        return success, position
        

    def displace(self, dis=0.0, pos_check=True):
        self.print(f"Displacing by {dis}mm", thr=1)
        if pos_check:
            result, position = self.position_check(dis)
        else:
            result = True
            position = 0.0

        if result:
            direction = 'forward' if dis>=0 else 'backward'
            self.set_direction(direction)
            move_time = self.dis2time(abs(dis))
            self.move(move_time = move_time)

            self.position = position
            self.write_position(self.position)

            success = True
            status = None
        else:
            success = False
            status = "invalid_distance"
        return success, status


    def return2home(self):
        self.print("Returning to home position", thr=1)
        dis_from_home = self.position

        success = True
        status = None
        if dis_from_home > 0:
            success, status = self.displace(-1 * dis_from_home)
        elif dis_from_home == 0:
            print("Gantry plate already at home")
        else:
            raise Exception("The position status variable is negative. Please check the position file")

        return success, status
    

    def go2end(self):
        self.print("Going to the end of the linear track", thr=1)
        dis_from_end = self.travel_length - self.position

        success = True
        status = None
        if dis_from_end > 0:
            success, status = self.displace(dis_from_end)
        elif dis_from_end == 0:
            print("Gantry plate already at the end")
        else:
            raise Exception("The position status variable is negative for gotoend. Please check the position file")

        return success, status
    

    def back_and_forth(self, distance=100.0, margin=100.0, repeats=8, delay=2.0):
        self.print("Moving back and forth", thr=1)
        direction = 'forward'
        rep_id = 0

        while True:
            time.sleep(delay)
            rep_id += 1

            if direction=='forward':
                dir = 1
            elif direction=='backward':
                dir = -1
            else:
                raise Exception("Invalid direction")
            dist = distance * dir
            success, status = self.displace(dist)
            if success == False:
                break
            
            if rep_id>=repeats:
                rep_id = 0
                if direction == 'forward':
                    direction = 'backward'
                elif direction == 'backward':
                    direction = 'forward'

            if self.position >= self.travel_length - margin:
                rep_id = 0
                direction = 'backward'
            elif self.position <= margin:
                rep_id = 0
                direction = 'forward'

            if rep_id == 0:
                time.sleep(5*delay)


    

    def stop(self):
        self.pulse_pwm.throttle = 0.0
        self.direction_out.throttle = 0.0


    def reset(self):
        self.print("Resetting the linear track", thr=1)
        self.kit.motor1.throttle = 0.0
        self.kit.motor2.throttle = 0.0
        self.kit.motor3.throttle = 0.0
        self.kit.motor4.throttle = 0.0



# def on_program_exit():
#     kit = MotorKit(i2c=board.I2C())
#     kit.motor1.throttle = 0.0
#     kit.motor2.throttle = 0.0
#     kit.motor3.throttle = 0.0
#     kit.motor4.throttle = 0.0
#     print("Exiting the program")




def lintrack_run(params):
    lt = LinearTrack(params)

    atexit.register(lt.reset)
    # atexit.register(on_program_exit)

    # lt.calibrate(mode='start')
    # lt.calibrate(mode='end')
    # lt.return2home()
    # lt.go2end()

    lt.interactive_move()
    # lt.back_and_forth(distance=100.0, margin=100.0, repeats=8, delay=3.0)

    if params.run_tcp_server:
        lt.run_tcp()





if __name__ == '__main__':
    params = Params_Class()
    lintrack_run(params)
