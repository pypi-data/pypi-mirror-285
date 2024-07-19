import sys
import json
from icecream import ic

print("SCRIPT TO TEST")
ic(sys.argv)

def something_werid(*args,**kargs):
    ic(kargs)


deserialized = json.loads(sys.argv[1])
something_werid(**deserialized)
