#!/usr/bin/python3
# -*- coding: utf-8 -*-
import yaml

from . import boot
#───────────────────────────────────────────────────────────────────────
def generate_boot(path_to):
    description_text = """
    Boot item. Contains the executable for actually booting other database utilities."""
    item = {'__id__':       ('_python_str',     '0'),
            '_description': ('_python_str',            description_text),
            'executable':   ('_python_source',   boot.core_as_string())} # type: ignore

    with open(path_to, 'w+') as file:
        yaml.dump(item, file, default_flow_style=False)
#───────────────────────────────────────────────────────────────────────
def generate_config(path_to):
    description_text = """Config item."""

    logo = """
         AWAMMMMM  MMMMMMMMMMMM  MM      MM  MMMMMMMM  MMMMMA
        AWMM            MM       MM      MM  MM        MM    RA
       AW MM            MM       MM      MM  MM        MM     RD
      AW  MM            MM       MM      MM  MM        MM    RW
     AW   MMMMMMM       MM       MMMMMMMMMM  MMMMMMMM  MMWMMW
    AW    MM            MM       MM      MM  MM        MM WA
   AWMMMMMMM            MM       MM      MM  MM        MM  WA
  AW      MM            MM       MM      MM  MM        MM   WA
 AW       MMMMMMM       MM       MM      MM  MMMMMMMM  MM    WA"""
    intro = """
Hello there!

The database has been booted, but it is not really working.

Here, have an interactive python loop instead!"""

    item = {'__id__':       ('_python_str',     '1'),
            '_description': ('_python_str',            description_text),
            'logo':         ('_textart',         logo),
            'intro':        ('_python_str',            intro),
            '_types':       ('_internal_item',  '2'),
            '_metaindex':   ('_internal_item',  '3'),
            '_utilities':   ('_internal_item',  '4')}
    with open(path_to, 'w+') as file:
        yaml.dump(item, file, default_flow_style=False)
#───────────────────────────────────────────────────────────────────────
