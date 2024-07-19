import time, urllib3, sys, os
from threading import Thread, Lock

from ryry import ryry_webapi
from ryry import store
from ryry import taskUtils

lock = Lock()
def print_progress_bar(iteration, total, name, idx, total_bars):
    length=50
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    with lock:        
        sys.stdout.write(f'\0337')  # Save cursor position
        sys.stdout.write(f'\033[{total_bars-idx+1}A')  # Move cursor up to the specific progress bar line
        sys.stdout.write(f'\r{name}: |{bar}| {percent}% Complete')
        sys.stdout.write(f'\0338')  # Restore cursor position
        sys.stdout.flush()
    
class TaskThread(Thread):
    params = False
    idx = 0
    call_back = None
    def __init__(self, idx, total, func, params, callback):
        super().__init__()
        self.idx = idx
        self.total = total
        self.func = func
        self.checkUUID = None
        self.checking = False
        self.checkCount = 0
        self.params = params
        self.call_back = callback
        if self.call_back == None:
            raise Exception("need callback function")
        self.start()
    def run(self):
        self.checking = False
        self.result = False, "Unknow"
        if len(self.func) > 0:
            self.checkUUID = ryry_webapi.createTask(self.func, self.params)
            print("")
            self.checking = True
            self.checkCount = 0
            time.sleep(5)
            while self.checking and self.checkCount < 200:
                finish, success, data, progress = ryry_webapi.checkTask(self.checkUUID)
                print_progress_bar(progress, 100, f"Task{self.idx} {self.func}", self.idx+1, self.total)
                if finish:
                    self.checking = False
                    if success:
                        self.call_back(self.idx, data)
                        return
                self.checkCount += 1
                time.sleep(3)
        else:
            print(f"widget {self.func} not found")
        self.call_back(self.idx, None)
        
    def __del__(self):
        if self.checking and self.checkUUID:
            ryry_webapi.TaskCancel(self.checkUUID)
        
class Task:
    thread_data = {}

    def __init__(self, func: str, multi_params: list[dict], fromUUID=None):
        urllib3.disable_warnings()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        realTaskUUID = fromUUID
        if realTaskUUID == None or len(realTaskUUID) <= 0:
            realTaskUUID = taskUtils.taskInfoWithFirstTask()
            
        def _callback(idx, data):
            self.thread_data[str(idx)]["result"] = data
        idx = 0
        for param in multi_params:
            param["fromUUID"] = realTaskUUID
            self.thread_data[str(idx)] = {
                "thread" :  TaskThread(idx, len(multi_params), func, param, _callback),
                "result" : None
            }
            idx+=1
            time.sleep(1)
        
    def call(self):
        for t in self.thread_data.keys():
            self.thread_data[t]["thread"].join()
        result = []
        for t in self.thread_data.keys():
            result.append(self.thread_data[t]["result"])
        return result
    