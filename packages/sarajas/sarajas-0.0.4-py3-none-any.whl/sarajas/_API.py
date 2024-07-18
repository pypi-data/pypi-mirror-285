import pathlib

import yaml
from limedev.CLI import get_main

from . import meta
# ======================================================================
ASH = 'Æ'
file_extension = 'aedb'
PATH_BASE = pathlib.Path(__file__).parent.absolute()
PATH_DATA = PATH_BASE/ 'database'
ASCII_TITLE = """
      AWAMMMMM  MMMMMMMMMMMM  MM      MM  MMMMMMMM  MMMMA    MMMMA     MMMMMA
     AWMM            MM       MM      MM  MM        MM   RA  MM   MA   MM   MA
    AW MM            MM       MM      MM  MM        MM   RW  MM    MA  MM   MW
   AW  MMMMMMM       MM       MMMMMMMMMM  MMMMMMMM  MMWMW    MM    MM  MMMMMX
  AWMMMMM            MM       MM      MM  MM        MM WA    MM    MW  MM   MA
 AW    MM            MM       MM      MM  MM        MM  WA   MM   MM   MM   MW
AW     MMMMMMM       MM       MM      MM  MMMMMMMM  MM   WA  MMMMV     MMMMMV
"""

# ======================================================================

def _load_by_name(ID: str):
    """Loads item by its name."""
    path_file = PATH_DATA / (ID + '.' + file_extension)
    with open(path_file, 'r+') as file:
        item = yaml.load(file, Loader=yaml.Loader)
    return item
# ======================================================================
def _execute_from_item(item, arguments=None):
    exec(item['executable'][1])
# ======================================================================
def boot(bootitem: str = '0'):
    """Boots the database from the file containing boot source."""
    item = _load_by_name(ID = bootitem)
    _execute_from_item(item)


def generate() -> int:
    """Generates boot and configuration."""
    meta.constructor.generate_boot(PATH_DATA / '0.aedb')
    meta.constructor.generate_config(PATH_DATA / '1.aedb')
    return 0

def load() -> int:
    with open(meta.path_0, 'r+') as file:
        item = yaml.load(file, Loader=yaml.Loader)
    return 0


def write() -> int:
    with open(meta.path_DB/'__main__.py', 'r+') as file:
        print(file.read())
    return 0
# ======================================================================
main = get_main(__name__)
