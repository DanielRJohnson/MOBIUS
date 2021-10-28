#!/usr/bin/env python
import pandas as pd
import os
import asyncio
import websockets
import socket
import json
from time import gmtime, strftime

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


hostname = socket.gethostname()
IPAddr = get_ip()
print("Your Computer Name is: " + hostname)
print("Your Computer IP Address is: " + IPAddr)
print(
    "* Enter {0}:5000 in the app.\n"
    "* Press the 'Set IP Address' button.\n"
    "* Select the sensors to stream.\n"
    "* Update the 'update interval' by entering a value in ms.".format(IPAddr))
reading_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

async def echo(websocket, path):
    async for message in websocket:
        if path == '/accelerometer':
            acc_data = await websocket.recv()
            acc_json = json.loads(acc_data)

            # for csv
            acc_values = acc_json.values()
            data_df = pd.DataFrame([list(acc_values)], columns=["SensorName", "Timestamp", "x", "y", "z", "payload"])
            fpath = "raw_data/accelerometer/acc_" + reading_time + ".csv"
            data_df.to_csv(fpath, mode='a', header=not os.path.exists(fpath))
            print("Acc Data Appended")

        elif path == '/gyroscope':
            gyro_data = await websocket.recv()
            gyro_json = json.loads(gyro_data)

            # for csv
            gyro_values = gyro_json.values()
            data_df = pd.DataFrame([list(gyro_values)], columns=["SensorName", "Timestamp", "x", "y", "z", "payload"])
            fpath = "raw_data/gyroscope/gyro_" + reading_time + ".csv"
            data_df.to_csv(fpath, mode='a', header=not os.path.exists(fpath))
            print("Gyro Data Appended")

        else:
            pass

asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, '0.0.0.0', 5000, max_size=1_000_000_000))
asyncio.get_event_loop().run_forever()
