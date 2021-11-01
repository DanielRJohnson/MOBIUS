#!/usr/bin/env python
import pandas as pd
import os
import asyncio
import websockets
import socket
import json
import time

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
reading_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

acc_fpath = "raw_data/accelerometer/acc_" + reading_time + ".csv"
complete_acc_df = pd.DataFrame()

gyro_fpath = "raw_data/gyroscope/gyro_" + reading_time + ".csv"
complete_gyro_df = pd.DataFrame()

gyro = False
accel = False
async def echo(websocket, path):
    global gyro
    global accel
    global complete_acc_df
    global complete_gyro_df
    async for message in websocket:
        if path == '/accelerometer':
            accel = True
            if gyro:     
                now = time.time()
                acc_json = json.loads(message)

                assert (acc_json["SensorName"] == "Accelerometer"), "RECEIVED GYROSCOPE MESSAGE WITH ACCELEROMETER PATH"

                acc_values = acc_json.values()
                data_df = pd.DataFrame([list(acc_values)], columns=["SensorName", "Timestamp", "x", "y", "z", "payload"])
                complete_acc_df = pd.concat([complete_acc_df, data_df])
                print("Acc Data Appended in", (time.time() - now) * 1000, "milliseconds")

        elif path == '/gyroscope':
            gyro = True
            if accel:
                now = time.time()
                gyro_json = json.loads(message)

                assert (gyro_json["SensorName"] == "Gyroscope"), "RECEIVED ACCELEROMETER MESSAGE WITH GYROSCOPE PATH"

                gyro_values = gyro_json.values()
                data_df = pd.DataFrame([list(gyro_values)], columns=["SensorName", "Timestamp", "x", "y", "z", "payload"])
                complete_gyro_df = pd.concat([complete_gyro_df, data_df])
                print("Gyro Data Appended", (time.time() - now) * 1000, "milliseconds")
        else:
            pass

try:
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(echo, '0.0.0.0', 5000, max_size=1_000_000_000))
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    complete_acc_df.to_csv(acc_fpath, index=None)
    complete_gyro_df.to_csv(gyro_fpath, index=None)
    print("\nWrote Dataframes to /raw_data/")
    exit()