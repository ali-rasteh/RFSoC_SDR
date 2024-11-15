from backend import *
from backend import be_np as np, be_scp as scipy
try:
    from rfsoc import RFSoC
except:
    pass
from params import Params_Class
from signal_utilsrfsoc import Signal_Utils_Rfsoc
from tcp_comm import Tcp_Comm_RFSoC, Tcp_Comm_LinTrack, ssh_Com_Piradio, REST_Com_Piradio




def rfsoc_run(params):
    client_rfsoc = None
    client_lintrack = None
    client_piradio = None

    signals_inst = Signal_Utils_Rfsoc(params)
    signals_inst.print("Running the code in mode {}".format(params.mode), thr=1)
    (txtd_base, txtd) = signals_inst.gen_tx_signal()

    if params.use_linear_track:
        client_lintrack = Tcp_Comm_LinTrack(params)
        client_lintrack.init_tcp_client()
        # client_lintrack.return2home()
        # client_lintrack.go2end()

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


    elif params.mode=='client':
        params.show_saved_sigs=len(params.saved_sig_plot)>0
        if not params.show_saved_sigs:
            client_rfsoc=Tcp_Comm_RFSoC(params)
            client_rfsoc.init_tcp_client()

            if params.send_signal:
                # client_rfsoc.transmit_data()
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
                signals_inst.save_signal_channel(client_rfsoc, txtd_base, save_list=params.save_list)
        
        signals_inst.animate_plot(client_rfsoc, client_lintrack, client_piradio, txtd_base, plot_mode=params.animate_plot_mode, plot_level=0)



if __name__ == '__main__':
    
    params = Params_Class()
    rfsoc_run(params)

