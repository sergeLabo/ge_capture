
# # import zlib, json, base64
import gzip
import json
from datetime import datetime


def json_zip(j):

    j = {zlib.compress(json.dumps(j).encode('utf-8')).decode('ascii')}

    return j

def un_json_zip(zzz):
    return json.loads(zlib.decompress(b64decode(zzz['base64(zip(o))'])))

def do_save(zzz):
    dt_now = datetime.now()
    dt = dt_now.strftime("%Y_%m_%d_%H_%M")

    with open("test.zip", "w") as fd:
        fd.write(zzz)

def save(jsonfilename, data):
    with gzip.open(jsonfilename, 'wt', encoding='UTF-8') as zipfile:
        json.dump(data, zipfile)

def read(jsonfilename):
    with gzip.open(jsonfilename, 'rt', encoding='UTF-8') as zipfile:
        my_object = json.load(zipfile)


if __name__ == '__main__':

    with open("cap_2021_12_18_10_53.json") as f:
        data = f.read()
    save('test_1', data)
