import subprocess
import atexit
import platform
import numpy as np
import traceback
import pandas as pd
import os
import threading
import time
import importlib
import importlib.resources as resources

class ebFRET_controller:

    def __init__(self,
                 ebfret_dir: str = resources.files(importlib.import_module(f'ebFRET')),
                 num_workers: int = 2,):

        self.engine = None
        atexit.register(self.cleanup)  # Register cleanup method to be called on exit

        self.ebfret_dir = os.path.normpath(ebfret_dir)
        self.matlab_installed = False

        self.ebfret_handle = None
        self.ebfret_running = False

        self.num_workers = num_workers
        self.lock = threading.Lock()

    def check_ebfret_dir(self):

        directory_status = False

        if os.path.exists(self.ebfret_dir):
            for root, dir, files in os.walk(self.ebfret_dir):
                if "ebFRET.m" in files:
                    directory_status = True
            if directory_status == True:
                print("ebFRET directory found: " + self.ebfret_dir)
            else:
                print("ebFRET directory does not contain ebFRET.m: " + self.ebfret_dir)
        else:
            print("ebFRET directory not exist: " + self.ebfret_dir)

        return directory_status

    def check_matlab_engine_installed(self):
        try:
            import matlab.engine
            print("MATLAB engine API for Python is installed.")
            self.matlab_installed = True
            return True
        except ImportError:
            self.print_notification("MATLAB engine API for Python is not installed.")
            return False

    def check_matlab_running(self):
        try:
            if platform.system() == "Windows":
                procs = subprocess.check_output("tasklist").decode("utf-8")
                return "MATLAB.exe" in procs
            else:  # Linux and macOS
                procs = subprocess.check_output(["ps", "aux"]).decode("utf-8")
                return "matlab" in procs.lower()
        except Exception as e:
            print(f"Error checking if MATLAB is running: {e}")
            return False

    def start_engine(self):

        if self.matlab_installed == True:
            try:
                import matlab.engine

                matlab_session = matlab.engine.find_matlab()

                if len(matlab_session) > 0:
                    try:
                        self.engine = matlab.engine.start_matlab(matlab_session[0])
                        print("Connected to existing MATLAB engine")
                    except:
                        self.engine = matlab.engine.start_matlab()
                        print("MATLAB engine started")

                else:
                    self.engine = matlab.engine.start_matlab()
                    print("MATLAB engine started")

                return True
            except Exception as e:
                print(f"Error starting MATLAB engine: {e}")
                self.close_engine()
                return False

    def start_parrallel_pool(self):

        try:

            if self.engine:
                self.engine.parpool('local', self.num_workers, nargout=0)
        except:
            self.close_engine()

    def stop_parrallel_pool(self):

        try:
            if self.engine:
                print("Stopping MATLAB parallel pool")
                self.engine.eval("poolobj = gcp('nocreate');", nargout=0)
                self.engine.eval("if ~isempty(poolobj), delete(poolobj); end", nargout=0)
                print("MATLAB parallel pool stopped")
        except:
            self.close_engine()


    def _start_ebfret(self):
        
        self.ebfret_handle = self.engine.ebFRET()
        
        
    def start_ebfret(self, threaded = True):

        if self.engine == None:
            self.start_engine()

        if self.engine:
            
            print("starting ebFRET...")
            
            self.engine.cd(self.ebfret_dir, nargout=0)

            self.engine.eval("addpath(genpath('" + self.ebfret_dir + "'))", nargout=0)
            self.engine.addpath(self.engine.genpath("\python"), nargout=0)

            if threaded == True:
                
                ebfret_thread = threading.Thread(target=self._start_ebfret)
                ebfret_thread.start()
                
                with self.lock:
                    while not self.check_ebfret_running():
                        time.sleep(0.1)

                    print("ebFRET started")
            else:
                self._start_ebfret
            

    def check_ebfret_running(self):

        ebfret_running = False
        if self.engine and self.ebfret_handle:
            try:
                ebfret_running = self.engine.isvalid(self.ebfret_handle)
            except:
                print("ebFRET closed")

        return ebfret_running


    def dev(self, data):
        
        if self.engine:
            
            self.engine.cd(self.ebfret_dir, nargout=0)

            self.engine.eval("addpath(genpath('" + self.ebfret_dir + "'))", nargout=0)
            self.engine.addpath(self.engine.genpath("\python"), nargout=0)
            
            correct_format, mode = self.check_data_format(data)
            
            if mode == "FRET":
            
                data = [[[float(value) for value in inner] for inner in middle] for middle in data]
                
                dataDD = [dat[0] for dat in data]
                dataDA = [dat[1] for dat in data]
                
                self.engine.ebfret.python.python_load_fret_data("test.txt",dataDD, dataDA, nargout=0)
                
        else:
            print("no engine")
        


    def check_data_format(self, data):
        
        correct_format = True
        mode = ""
        
        for arr_index, arr in enumerate(data):
            if not isinstance(arr, np.ndarray):  # Check if the element is a NumPy array
                try:
                    arr = np.array(arr)
                    data[arr_index] = arr
                except:
                    correct_format = False
                    break

            if len(arr.shape) == 1:
                mode = "Efficiency"
                
                data = [[float(y) for y in x] for x in data]
            
            else:
                if arr.shape[-1] == 1:
                    mode = "Efficiency"
                    
                elif arr.shape[-1] == 2:
                    mode = "FRET"
                        
                else:
                    correct_format = False
                    break
                
        if correct_format == False:
            print("input data must be a list of numpy arryas of shape (N,2), (N,1) or (N,)")
        else:

            if mode == "Efficiency":
                
                data = [[float(y) for y in x] for x in data]
                
            elif mode == "FRET":
                
                fret_data = [dat.T.tolist() for dat in data]
                
                dataDD = [dat[0] for dat in fret_data]
                dataDA = [dat[1] for dat in fret_data]
                
                dataDD = [[float(y) for y in x] for x in dataDD]
                dataDA = [[float(y) for y in x] for x in dataDA]
                
                data = [dataDD, dataDA]
                
            else:
                correct_format = False
            
        return correct_format, mode, data


    def python_import_ebfret_data(self, data=[], file_name="temp.tif"):
        
        try:
            
            correct_format, mode, data = self.check_data_format(data)

            if correct_format == True:
                                
                if mode == "FRET":
                    
                    print("ebFRET importing Dual Channel data")
                    
                    if self.engine and self.ebfret_handle:
                        self.engine.ebfret.python.python_load_fret_data(self.ebfret_handle, file_name, data[0], data[1], nargout=0)
                else:
                    
                    print("ebFRET importing Single Channel data")

                    if self.engine and self.ebfret_handle:
                        self.engine.ebfret.python.python_load_efficiency_data(self.ebfret_handle, file_name, data, nargout=0)

        except:
            self.stop_parrallel_pool()
            self.close_ebfret()
            self.close_engine()
            print(traceback.format_exc())
            
        return data

    def run_ebfret_analysis(self, min_states=2, max_states=6):
        try:
            self.ebfret_states = []

            if self.engine and self.ebfret_handle:
                self.engine.ebfret.python.python_run_ebayes(self.ebfret_handle, min_states, max_states, nargout=0)
                self.ebfret_states = self.engine.ebfret.python.python_export_traces(self.ebfret_handle, min_states, max_states)

                self.ebfret_states = np.array(self.ebfret_states)
                
                self.ebfret_states = pd.DataFrame(self.ebfret_states, columns=["N States", "Trace Index", "State", "Signal"])

        except:
            self.close_engine()

        return self.ebfret_states

    def close_ebfret(self):
        if self.engine and self.ebfret_handle:
            self.engine.ebfret.python.python_close_ebfret(self.ebfret_handle, nargout=0)
            self.ebfret_handle = None
            self.close_engine()

    def close_engine(self):
        if self.engine:
            try:
                if self.ebfret_handle:
                    self.close_ebfret()
                self.engine.quit()
                self.engine = None
                print("MATLAB engine closed")
            except Exception as e:
                print(f"Error closing MATLAB engine: {e}")

    def cleanup(self):
        self.close_ebfret()
        self.close_engine()

def launch_ebfret_instance():

    controller = ebFRET_controller()
    controller.start_ebfret()

    return controller


