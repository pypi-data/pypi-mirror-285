import sys

import requests
from ascript.ios import wda


def guess_client(device_id:str = None):
    response = requests.get("http://127.0.0.1:9097/api/device")
    if response.status_code == 200:
        data = response.json()
        if data["data"] and len(data["data"]) > 0:
            for device in data["data"]:
                # print(device)
                if device_id:
                    if device["Identifier"] == device_id:
                        print("指定设备:", device)
                        return wda.Client(f"http://127.0.0.1:{device['port']}")
                else:
                    if device["statue"] == 0:
                        print("猜测运行:", device)
                        return wda.Client(f"http://127.0.0.1:{device['port']}")


client = None

try:
    if len(sys.argv) > 1:
        client = guess_client(sys.argv[1])
    else:
        client = guess_client()
except Exception as e:
    print(e)


def init_client(host: str = "http://127.0.0.1", port: int = None):
    client = wda.Client(f"{host}:{port}")


class R:
    work_space = None
    client = None

    def __init__(self):
        pass


class Device:
    @staticmethod
    def display():
        return client.window_size()