#!/usr/bin/env python3

import os
import json
import zipfile




def make_archive_bad(path="test.zip"):
    # This doesn't work
    with zipfile.ZipFile(path, "x") as z:
        with z.open("config.json", "w") as c:
            print(type(c))
            json.dump(config, c, indent=2)

        with z.open("data.json", "w") as d:
            for row in data(config):
                d.write(json.dumps(row))
                d.write("\n")


def make_archive_annoying(path="test.zip"):
    # This does work but is annoying
    # Also note, this will write to the root of the archive, and when unzipped will not
    # unzip to a directory but rather into the same directory as the zip file
    with zipfile.ZipFile(path, "x") as z:
        with z.open("config.json", "w") as c:
            c.write(json.dumps(config, indent=2).encode("utf-8"))

        with z.open("data.json", "w") as d:
            for row in data(config):
                d.write(json.dumps(row).encode("utf-8"))
                d.write("\n".encode("utf-8"))


class Zipr(object):

    def __enter__(self):
        # Makes this thing a context manager
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Makes this thing a context manager
        self.close()

    def close(self):
        self.zobj.close()


class ZipArchive(Zipr):

    def __init__(self, path, mode="r"):
        self.zobj = zipfile.ZipFile(
            path, mode, compression=zipfile.ZIP_STORED,
            allowZip64=True, compresslevel=None
        )
        self.root, _ = os.path.splitext(os.path.basename(path))

    def open(self, path, mode='r'):
        # Write into a directory instead of the root of the zip file
        path = os.path.join(self.root, path)
        return ZipArchiveFile(self.zobj.open(path, mode))


class ZipArchiveFile(Zipr):

    def __init__(self, zobj, encoding="utf-8"):
        self.zobj = zobj
        self.encoding = encoding

    def write(self, data):
        if isinstance(data, str):
            data = data.encode(self.encoding)
        self.zobj.write(data)


def make_archive(path="test.zip"):
    # Less annoying make archive with workaround classes
    with ZipArchive(path, "x") as z:
        with z.open("cap_2021_12_18_10_53.json", "w") as c:
            json.dump(config, c, indent=2)

        with z.open("data.json", "w") as d:
            for row in data(config):
                d.write(json.dumps(row))
                d.write("\n")


def make_archive_stream(path="test.zip"):
    # Attempts to open the internal zip file for appending, to stream data in.
    # But this doesn't work because you can't open an internal zip object for appending
    with ZipArchive(path, "x") as z:
        with z.open("config.json", "w") as c:
            json.dump(config, c, indent=2)

        cache = []
        for i, row in enumerate(data(config)):
            cache.append(json.dumps(row))

            # dump cache every 5 rows
            if i%5 == 0:
                with z.open("data.json", "a") as d:
                    for row in cache:
                        d.write(row+"\n")
                cache = []

        if len(cache) > 0:
            with z.open("data.json", "a") as d:
                for row in cache:
                    d.write(row+"\n")



if __name__ == "__main__":
    make_archive()
