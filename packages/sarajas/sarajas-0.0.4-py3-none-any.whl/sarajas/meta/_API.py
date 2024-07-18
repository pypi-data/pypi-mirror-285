#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pathlib

import yaml
from limedev.CLI import get_main

from . import boot
from . import constructor
from . import texttools

path_meta = pathlib.Path(__file__).parent.absolute()
path_home = path_meta.parent
path_DB = path_home / 'database'
path_0 = path_DB / '0.aedb'

def dump() -> int:
    constructor.generate_boot(path_0)
    return 0

def load() -> int:
    with open(path_0, 'r+') as file:
        item = yaml.load(file, Loader=yaml.Loader)
    return 0

def write():
    with open(path_DB/'__main__.py', 'r+') as file:
        print(file.read())

main = get_main(__name__)
