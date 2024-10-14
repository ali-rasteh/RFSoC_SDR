from backend import *
from backend import be_np as np, be_scp as scipy


class General(object):
    def __init__(self, params):
        self.verbose_level = getattr(params, 'verbose_level', 5)
        self.plot_level = getattr(params, 'plot_level', 5)
        self.figs_dir = getattr(params, 'figs_dir', None)
        self.logs_dir = getattr(params, 'logs_dir', None)
        self.data_dir = getattr(params, 'data_dir', None)
        self.random_str = getattr(params, 'random_str', '')
        
        self.import_cupy = getattr(params, 'import_cupy', False)
        self.use_cupy = getattr(params, 'use_cupy', False)
        self.gpu_id = getattr(params, 'gpu_id', 0)

        self.use_torch = getattr(params, 'use_torch', False)
        if self.use_torch:
            self.init_device_torch()
        else:
            self.device = None


    def print(self, text='', thr=0):
        if self.verbose_level>=thr:
            print(text)


    def gen_random_str(self, length=6):
        letters = string.ascii_letters + string.digits
        self.random_str = ''.join(random.choice(letters) for i in range(length))
        self.print("Random string for this run: {}".format(self.random_str),thr=0)
        return self.random_str


    def print_info(self, params):
        self.print_params(params)

        now = datetime.datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        # Get the latest Git commit ID
        try:
            latest_commit_id = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode('utf-8')
        except subprocess.CalledProcessError:
            latest_commit_id = "No Git repository found or Git command failed."

        # Print the formatted date, time, and latest commit ID
        self.print(f"Current Date and Time: {current_datetime}",thr=0)
        self.print(f"Latest Git Commit ID: {latest_commit_id}",thr=0)


    def print_params(self, params):
        self.print("Run parameters:",thr=0)
        for attr in dir(params):
            if not callable(getattr(params, attr)) and not attr.startswith("__"):
                self.print(f"{attr} = {getattr(params, attr)}",thr=0)
        self.print('\n',thr=0)


    def init_device_torch(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.print('Torch device: {}'.format(self.device),thr=0)


    def cupy_plt_plot(self, *args, **kwargs):
        args = list(args)

        # Apply np.sqrt to the first two arguments
        if len(args) > 0:
            args[0] = self.numpy_transfer(args[0], dst='numpy')
        if len(args) > 1:
            args[1] = self.numpy_transfer(args[1], dst='numpy')

        plt.plot(*args, **kwargs)
        # plt.show()


    def cupy_gpu_init(self):
        if self.use_cupy and self.import_cupy:
            self.check_gpu_usage()
            self.print_gpu_memory()
            self.warm_up_gpu()
            self.gpu_cpu_compare()


    def check_cupy_gpu(self, gpu_id=0):
        if not self.import_cupy:
            return False
        try:
            import cupy as cp
            # Check if CuPy is installed
            self.print("CuPy version: {}".format(cp.__version__),thr=0)

            num_gpus = cp.cuda.runtime.getDeviceCount()
            self.print(f"Number of GPUs available: {num_gpus}",thr=0)

            # Check if the GPU is available
            cp.cuda.Device(gpu_id).compute_capability
            self.print("GPU {} is available".format(gpu_id),thr=0)

            self.print('GPU {} properties: {}'.format(gpu_id, cp.cuda.runtime.getDeviceProperties(gpu_id)),thr=0)
            return True
        except ImportError:
            self.print("CuPy is not installed.",thr=0)
        except:
            self.print("GPU is not available or CUDA is not installed correctly.",thr=0)
        return False


    def get_gpu_device(self):
        if self.use_cupy:
            import cupy as cp
            return cp.cuda.Device(self.gpu_id)
        else:
            return None


    def check_gpu_usage(self):
        import cupy as cp
        with cp.cuda.Device(self.gpu_id) as device:
            self.print(f"Current device: {device}",0)


    def print_gpu_memory(self):
        import cupy as cp
        with cp.cuda.Device(self.gpu_id):
            mempool = cp.get_default_memory_pool()
            self.print("Used GPU memory: {} bytes".format(mempool.used_bytes()),thr=0)
            self.print("Total GPU memory: {} bytes".format(mempool.total_bytes()),thr=0)


    # Initialize and warm-up
    def warm_up_gpu(self):
        self.print('Starting GPU warmup.', thr=0)
        import cupy as cp
        with cp.cuda.Device(self.gpu_id):
            start = time.time()
            _ = cp.array([1, 2, 3])
            _ = cp.array([4, 5, 6])
            a = cp.random.rand(1000, 1000)
            _ = cp.dot(cp.array([[1, 2], [3, 4]]), cp.array([[5, 6], [7, 8]]))
            _ = cp.dot(a, a)
            cp.cuda.Stream.null.synchronize()
            end = time.time()
        self.print("GPU warmup time: {}".format(end-start),thr=0)


    # Perform computation
    def gpu_cpu_compare(self, size=20000):
        self.print('Starting CPU and GPU times compare.', thr=0)
        import cupy as cp
        # Generate data
        a_cpu = numpy.random.rand(size, size).astype(float)
        b_cpu = numpy.random.rand(size, size).astype(float)

        # Measure CPU time for comparison
        start = time.time()
        result_cpu = numpy.dot(a_cpu, b_cpu)
        end = time.time()
        cpu_time = end - start
        self.print("CPU time: {}".format(cpu_time),thr=0)

        with cp.cuda.Device(self.gpu_id):
            # Transfer data to GPU
            a_gpu = cp.asarray(a_cpu)
            b_gpu = cp.asarray(b_cpu)

            # Measure GPU time
            start = time.time()
            result_gpu = cp.dot(a_gpu, b_gpu)
            cp.cuda.Stream.null.synchronize()  # Ensure all computations are finished
            end = time.time()
            gpu_time = end - start
            self.print("GPU time: {}".format(gpu_time), thr=0)

        return gpu_time, cpu_time


    def numpy_transfer(self, arrays, dst='numpy'):

        if self.import_cupy:
            if isinstance(arrays, list):
                out = []
                for i in range(len(arrays)):
                    if dst == 'numpy' and not isinstance(arrays[i], numpy.ndarray):
                        out.append(np.asnumpy(arrays[i]))
                    elif dst == 'context' and not isinstance(arrays[i], np.ndarray):
                        out.append(np.asarray(arrays[i]))
            else:
                if dst=='numpy' and not isinstance(arrays, numpy.ndarray):
                    out = np.asnumpy(arrays)
                elif dst=='context' and not isinstance(arrays, np.ndarray):
                    out = np.asarray(arrays)
        else:
            out = arrays
        return out


    def unique_list(self, input_list):
        seen = set()
        input_list = [x for x in input_list if not (x in seen or seen.add(x))]
        return input_list

