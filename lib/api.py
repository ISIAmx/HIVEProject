

import json


def output(values):
    print("Content-Type: application/json")
    print()
    print(json.dumps(values))
    
