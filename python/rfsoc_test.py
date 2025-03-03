from backend import *
from backend import be_np as np, be_scp as scipy
try:
    from rfsoc import RFSoC
except:
    pass
from params import Params_Class
from signal_utilsrfsoc import Signal_Utils_Rfsoc
from tcp_comm import Tcp_Comm_RFSoC, Tcp_Comm_LinTrack, ssh_Com_Piradio, REST_Com_Piradio, Tcp_Comm_Controller
from serial_comm import Serial_Comm_TurnTable




def rfsoc_run(params):
    client_rfsoc = None
    client_lintrack = None
    client_turntable = None
    client_piradio = None
    client_controller = None

    signals_inst = Signal_Utils_Rfsoc(params)
    if params.save_parameters:
        params.save_parameters = False
        signals_inst.save_class_attributes_to_json(params, params.params_save_path)
    if params.load_parameters:
        signals_inst.load_class_attributes_from_json(params, params.params_path)
        params.initialize()

    signals_inst.print("Running the code in mode {}".format(params.mode), thr=1)
    (txtd_base, txtd) = signals_inst.gen_tx_signal()

    if params.use_linear_track:
        client_lintrack = Tcp_Comm_LinTrack(params)
        client_lintrack.init_tcp_client()
        # client_lintrack.return2home()
        # client_lintrack.go2end()

    if params.use_turntable:
        client_turntable = Serial_Comm_TurnTable(params)
        client_turntable.connect()

    if params.control_piradio:
        # client_piradio = ssh_Com_Piradio(params)
        # client_piradio.init_ssh_client()
        # client_piradio.initialize()
        client_piradio = REST_Com_Piradio(params)
        client_piradio.set_frequency(params.fc)

    if params.mode=='server':
        rfsoc_inst = RFSoC(params)
        rfsoc_inst.txtd = txtd
        if params.send_signal:
            rfsoc_inst.send_frame(txtd)
        if params.recv_signal:
            rfsoc_inst.recv_frame_one(n_frame=params.n_frame_rd)
            signals_inst.rx_operations(txtd_base, rfsoc_inst.rxtd)
        if params.run_tcp_server:
            rfsoc_inst.run_tcp()


    elif 'client' in params.mode:

        if 'master' in params.mode:
            client_controller = Tcp_Comm_Controller(params)
            client_controller.init_tcp_client()
            client_controller.set_frequency(params.fc)
        elif 'slave' in params.mode:
            controller = Tcp_Comm_Controller(params)
            controller.init_tcp_server()
            controller.obj_piradio = client_piradio
            controller.obj_rfsoc = client_rfsoc
            controller.run_tcp_server(controller.parse_and_execute)


        params.show_saved_sigs=len(params.saved_sig_plot)>0
        if params.control_rfsoc and not params.show_saved_sigs:
            client_rfsoc=Tcp_Comm_RFSoC(params)
            client_rfsoc.init_tcp_client()

            if params.send_signal:
                # client_rfsoc.transmit_data_default()
                # client_rfsoc.transmit_data(txtd)
                pass

            if params.RFFE=='sivers':
                client_rfsoc.set_frequency(params.fc)
                if params.send_signal:
                    client_rfsoc.set_mode('RXen0_TXen1')
                    client_rfsoc.set_tx_gain()
                elif params.recv_signal:
                    client_rfsoc.set_mode('RXen1_TXen0')
                    client_rfsoc.set_rx_gain()

            signals_inst.calibrate_rx_phase_offset(client_rfsoc)
            if params.nf_param_estimate:
                signals_inst.create_near_field_model()

            if 'channel' in params.save_list or 'signal' in params.save_list:
                signals_inst.save_signal_channel(client_rfsoc, client_piradio, client_controller, txtd_base, save_list=params.save_list)
        
        

        if not 'slave' in params.mode:
            signals_inst.animate_plot(client_rfsoc, client_lintrack, client_turntable, client_piradio, client_controller, txtd_base, plot_mode=params.animate_plot_mode, plot_level=0)


if __name__ == '__main__':
    
    params = Params_Class()
    rfsoc_run(params)

