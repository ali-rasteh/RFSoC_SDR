"""
This script is used to copy and modify files from a remote host to a local directory.
It supports two targets: 'rfsoc' and 'raspi', each with its own set of files and parameters to modify.
Functions:
    main(params):
        Main function to handle the file copying and modification process.
        Args:
            params (Params_Class): An instance of Params_Class containing configuration parameters.
Usage:
    Run this script directly to copy and modify files based on the specified target.
    You can modify parameters at the beginning of the main function to customize the behavior.
    Example:
        python copy_files.py
"""

from backend import *
from backend import be_np as np, be_scp as scipy
from params import Params_Class
from tcp_comm import Scp_Com





class File_Utils(Scp_Com):

    def __init__(self, params):
        super().__init__(params)

        # Configuration
        self.target = 'rfsoc'        # 'rfsoc' or 'raspi'

        self.host_base_addr = "/home/wirelesslab914/ali/sounder_rfsoc/RFSoC_SDR/python/"
        # self.host_base_addr = "/Users/alira/OneDrive/Desktop/Current_works/Channel_sounding/RFSoC_SDR_copy/"
        # self.host_base_addr = "/home/wirelesslab914/ali/RFSoC_SDR/python"

        self.host = ""
        self.username = "wirelesslab914"
        # self.username = "alira"

        self.password = ""




        self.local_dir = "./"
        self.verbose_level = 5

        if self.target == 'rfsoc':
            self.remote_files = ["*.py", "*.txt", "SigProc_Comm/*.py"]
            # self.remote_files.extend(["../vivado/sounder_fr3_if_ddr4_mimo_4x2/builds/project_v1-0-58_20241001-150336.bit", 
            #                 "../vivado/sounder_fr3_if_ddr4_mimo_4x2/builds/project_v1-0-58_20241001-150336.hwh"])
        elif self.target == 'raspi':
            self.remote_files = ["*.py", "*.txt", "SigProc_Comm/*.py", "linear_track/*.py", "linear_track/*.txt"]
        
        if self.target == 'rfsoc':
            self.params_to_modify = {"backend.py": {"import_pynq": True, "import_torch": False,
                                "import_sklearn": False, "import_cv2": False, "import_sivers": False, "import_adafruit": False}}  
        elif self.target == 'raspi':
            self.params_to_modify = {"backend.py": {"import_pynq": False, "import_torch": False,
                            "import_sklearn": False, "import_cv2": False, "import_sivers": False, "import_adafruit": True}}
            
        if self.target == 'rfsoc':
            self.files_to_convert = {"rfsoc_test.py": "rfsoc_test.ipynb"}





    def download_files(self):

        # Ensure the local directory exists
        if not os.path.exists(self.local_dir):
            print(f"Local directory {self.local_dir} does not exist. Creating it.")
            os.makedirs(self.local_dir, exist_ok=True)


        # self.remote_files_ = [os.path.join(host_base_addr, file) for file in remote_files]
        self.remote_files_ = self.remote_files.copy()



        for pattern in self.remote_files:
            local_files = glob.glob(os.path.join(self.local_dir, pattern))
            # file = file.split('/')[-1]
            for file in local_files:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Deleted: {file}")

        for item in os.listdir(self.local_dir):
            item_path = os.path.join(self.local_dir, item)
            try:
                # Remove directories
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                # Remove files
                elif os.path.isfile(item_path):
                    continue
                    # os.remove(item_path)
                elif os.path.islink(item_path):
                    os.unlink(item_path)
                print(f"Deleted: {item_path}")
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")

        # self.download_files(remote_files_, local_dir)
        self.download_files_with_pattern(self.host_base_addr, self.remote_files_, self.local_dir)




    def modify_files(self):

        changed = False
        for file in self.params_to_modify:
            local_script_path = os.path.join(self.local_dir, file)
            for param in self.params_to_modify[file]:
                result = self.modify_text_file(local_script_path, param, self.params_to_modify[file][param])
                if result:
                    changed = True


        for file in self.files_to_convert:
            file_1 = os.path.join(self.local_dir, file)
            file_2 = os.path.join(self.local_dir, self.files_to_convert[file])
            self.convert_file_format(file_1, file_2)

        
        return changed






if __name__ == "__main__":

    params = Params_Class()
    file_utils = File_Utils(params)
    file_utils.download_files()
    file_utils.modify_files()




