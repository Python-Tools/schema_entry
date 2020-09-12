import sys
from pathlib import Path
src_dir = str(Path(__file__).resolve().parent.parent.joinpath("src"))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from entry_tree import EntryPoint


class ppm(EntryPoint):
    """ppm <subcmd> [<args>]
    ppm工具的子命令有:
        工具自身相关:
        help              展示ppm的帮助说明
        version           展示ppm的版本
        reset             将ppm工具的设置初始化
        cache             管理ppm的缓存
    """
    epilog = ''
    description = '项目脚手架'

main = ppm()


class help(EntryPoint):
    """帮助信息.
    ppm help <subcommand>
    ppm工具的子命令有:
        工具自身相关:
        help              展示ppm的帮助说明
        version           展示ppm的版本
        reset             将ppm工具的设置初始化
        cache             管理ppm的缓存
    """
    description='查看子命令的帮助说明'

main_help = main.regist_sub(help)
@main_help.regist_callback
def printconfig(config):
    print("1231")
    print(config)

main(["help"])