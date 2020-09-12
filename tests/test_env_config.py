import sys
import os
from pathlib import Path
src_dir = str(Path(__file__).resolve().parent.parent.joinpath("src"))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from entry_tree import EntryPoint

class ppm(EntryPoint):
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "examples":[
            {
                "a": 123.1
            },
        ],
        "type": "object",
        "properties": {
            "a": {
                "type": "number"
            }
        },
        "required": [ "a"]
    }

main = ppm()
@main.regist_callback
def app(config):
    print(config)

os.environ['PPM_A']="123.1"

main([])