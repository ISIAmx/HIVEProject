

import sys

from . import api
import json


def throwError(errorMessage):
    api.output({'error': errorMessage})
    return json.dumps({'error': errorMessage})
