import io
import json
import subprocess
import threading
from datetime import datetime

from ascript.ios.developer import ws

run_process = None


def run_worker(cmds, module_space):
    global run_process

    if run_process is not None:
        run_process.kill()

    run_process = subprocess.Popen(cmds, cwd=module_space, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # ws.send_message("启动成功")
    while True:
        for line in io.TextIOWrapper(run_process.stdout, encoding='utf-8'):
            # msgstr = line.strip()
            line = line.replace("\n","").replace("\r\n","").replace("\r","")
            msg = {"msg": line, "type": "i", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            # print(json.dumps(msg))
            ws.send_message(json.dumps(msg))

        for line in io.TextIOWrapper(run_process.stderr, encoding='utf-8'):
            line = line.replace("\n", "").replace("\r\n", "").replace("\r", "")
            msg = {"msg": line, "type": "e", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            print(line)
            ws.send_message(json.dumps(msg))

        if run_process.poll() is not None:
            break

    ws.send_message("运行结束")
    run_process = None


def run_script(cmd, module_space):
    threading.Thread(target=run_worker, args=(cmd, module_space)).start()
