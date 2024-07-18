#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import zlib
#───────────────────────────────────────────────────────────────────────
def strcompress(string, level=-1):
    return base64.b64encode(zlib.compress(string.encode(),level)).decode()
#───────────────────────────────────────────────────────────────────────
def strdecompress(string):
    return zlib.decompress(base64.b64decode(string.encode())).decode()
#───────────────────────────────────────────────────────────────────────
def filepath2string(path):
    with open(path, 'r+') as file:
        string = file.read()
    return string
#───────────────────────────────────────────────────────────────────────
