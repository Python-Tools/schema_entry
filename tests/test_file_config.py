import sys
from pathlib import Path
src_dir = str(Path(__file__).resolve().parent.parent.joinpath("src"))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from entry_tree import EntryPoint

class ppm(EntryPoint):
    default_config_file_paths=["./test_config.json"]

main = ppm()
@main.regist_callback
def app(config):
    print(config)

main([])