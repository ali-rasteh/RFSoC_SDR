from backend import *
from backend import be_np as np, be_scp as scipy
from params import Params_Class
from tcp_comm import Scp_Com




# Main function
def main(params):

    # Configuration
    target = 'rfsoc'        # 'rfsoc' or 'raspi'

    host_base_addr = "~/ali/sounder_rfsoc/RFSoC_SDR/"
    # host_base_addr = "/Users/alira/OneDrive/Desktop/Current_works/Channel_sounding/RFSoC_SDR_copy/"

    local_dir = "./"

    params.host = "192.168.3.130"
    params.username = "wirelesslab914"
    # params.username = "alira"
    params.password = ''




    if target == 'rfsoc':
        remote_files = ["python/params.py", "python/rfsoc_test.py", "python/rfsoc.py", 
                        "python/signal_utilsrfsoc.py", "python/signal_utils.py",
                        "python/near_field.py", "python/general.py", "python/backend.py", 
                        "python/tcp_comm.py", "python/requirements.txt"]
        # remote_files.extend(["vivado/sounder_fr3_if_ddr4_mimo_4x2/builds/project_v1-0-58_20241001-150336.bit", 
        #                 "vivado/sounder_fr3_if_ddr4_mimo_4x2/builds/project_v1-0-58_20241001-150336.hwh"])
    elif target == 'raspi':
        remote_files = ["python/linear_track/lin_track_cntrl.py", "python/linear_track/position.txt", 
                  "python/backend.py", "python/tcp_comm.py", "python/general.py"]
    
    if target == 'rfsoc':
        params_to_modify = {"backend.py": {"import_pynq": True, "import_torch": False,
                            "import_sklearn": False, "import_cv2": False, "import_sivers": False, "import_adafruit": False}}  
    elif target == 'raspi':
        params_to_modify = {"backend.py": {"import_pynq": False, "import_torch": False,
                        "import_sklearn": False, "import_cv2": False, "import_sivers": False, "import_adafruit": True}}
        
    if target == 'rfsoc':
        files_to_convert = {"rfsoc_test.py": "rfsoc_test.ipynb"}



    params.password = 'nyu@1234'
    scp_client = Scp_Com(params)

    # Ensure the local directory exists
    os.makedirs(local_dir, exist_ok=True)

    remote_files_ = [os.path.join(host_base_addr, file) for file in remote_files]

    for file in remote_files:
        file = file.split('/')[-1]
        local_file = os.path.join(local_dir, file)
        if os.path.exists(local_file):
            os.remove(local_file)

    for item in os.listdir(local_dir):
        item_path = os.path.join(local_dir, item)
        try:
            # Remove directories
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            # Remove files
            elif os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.islink(item_path):
                os.unlink(item_path)
            # print(f"Deleted: {item_path}")
        except Exception as e:
            print(f"Error deleting {item_path}: {e}")

    scp_client.download_files(remote_files_, local_dir)

    for file in params_to_modify:
        for param in params_to_modify[file]:
            local_script_path = os.path.join(local_dir, file)
            scp_client.modify_text_file(local_script_path, param, params_to_modify[file][param])

    for file in files_to_convert:
        file_1 = os.path.join(local_dir, file)
        file_2 = os.path.join(local_dir, files_to_convert[file])
        scp_client.convert_file_format(file_1, file_2)




if __name__ == "__main__":
    params = Params_Class()
    main(params)

