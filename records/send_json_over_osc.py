
from time import time, sleep
import json

from oscpy.client import OSCClient


ip = '127.0.0.1'
port = 8000
osc_client = OSCClient(ip, port)

json_file = './json/cap_2021_12_18_10_53.json'

with open(json_file) as f:
    raw_data = f.read()

datas = json.loads(raw_data)

while 1:
    for i, data in enumerate(datas):
        tag = str(data[1]).encode('utf-8')
        # data = [1639821118.589486, '/depth', [3392]]
        # # print(tag)
        if tag == b'/depth':
            print(data[2])
            osc_client.send_message(tag, data[2])

        if i > 0:
            # j'attends entre 2 time enregistré
            sleep(data[0] - datas[i-1][0])

# Pour un pushde plus
