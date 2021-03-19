

import sys

from . import api


def throwError(errorMessage):
    api.output({"error": errorMessage})
    sys.exit()
