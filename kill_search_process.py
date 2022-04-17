import os
import psutil
import signal

def kill_md5_thread():
    # return
    pids = psutil.pids()
    for pid in pids:
        try:
            process_name = psutil.Process(pid).name()
            # print("check: " + str(pid) + " - " + process_name)
            if (
                process_name == "md5_birthdaysearch"
                or process_name == "md5_diffpathbackward"
                or process_name == "md5_diffpathconnect"
                or process_name == "md5_diffpathforward"
                or process_name == "md5_diffpathhelper"
                or process_name == "md5_fastcoll"
            ):
                os.kill(pid, signal.SIGKILL)
                print("Killed: " + str(pid) + " - " + process_name)
        except:
            pass

kill_md5_thread()