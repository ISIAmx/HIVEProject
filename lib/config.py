import os

from yaml import safe_load
from munch import munchify

with open(os.path.join(os.path.split(__file__)[0],
                       "../config/config.yaml.default"), "r") as f:
    config = munchify(safe_load(f))


def load_credentials():
    credentials = Munch()
    with open(os.path.join(_project_root, "credentials.txt")) as credfile:
        credentials.username = credfile.readline().strip()
        credentials.posting = credfile.readline().strip()
        credentials.active = credfile.readline().strip()
    return credentials
