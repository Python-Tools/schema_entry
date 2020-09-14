import sys
import os
from pathlib import Path
from typing import Sequence, Dict, Any
import argparse
src_dir = str(Path(__file__).resolve().parent.parent.joinpath("src"))
if src_dir not in sys.path:
    sys.path.append(src_dir)
from entry_tree import EntryPoint

class ppm(EntryPoint):
    """ppm <subcmd> [<args>]

    """
    epilog = ''
    description = '项目脚手架'
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "examples": [
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
        "required": ["a"]
    }

    def parse_commandline_args(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> Dict[str, Any]:
        """默认端点不会再做命令行解析,如果要做则需要在继承时覆盖此方法."""
        parser.add_argument('a', type=float, help='a')
        args = parser.parse_args(argv)
        return vars(args)


main = ppm()
@main.regist_callback
def app(config):
    print(config)


os.environ['PPM_A'] = "123.1"
print(main.prog)
main(["123"])
main(["-h"])
