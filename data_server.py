#!/usr/bin/env python
import asyncio
import websockets
import socket

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

# TODO format into csv
async def echo(websocket, path):
    async for message in websocket:
        if path == '/accelerometer':
            data = await websocket.recv()
            print(data)
            f = open("accelerometer.txt", "a")
            f.write(data+"\n")

        elif path == '/gyroscope':
            data = await websocket.recv()
            print(data)
            f = open("gyroscope.txt", "a")
            f.write(data+"\n")

        else:
            pass

asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, '0.0.0.0', 5000, max_size=1_000_000_000))
asyncio.get_event_loop().run_forever()
