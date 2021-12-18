
from time import time, sleep
import json

from oscpy.client import OSCClient


ip = '127.0.0.1'
port = 8000
osc_client = OSCClient(ip, port)

json_file = './json/cap_2021_12_18_05_02.json'

with open(json_file) as f:
    raw_data = f.read()

datas = json.loads(raw_data)
t = datas[0][0]
print(t)

for data in datas:
    # # print(data)
    tag = str(data[1]).encode('utf-8')
    # # print(tag, type(tag))
    # # msg = [x for x in data[2]]
    # # print(msg, type(msg))
    osc_client.send_message(tag, data[2])
    sleep(data[0] - t)
