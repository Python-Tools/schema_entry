'''入口树的构造工具.

这个基类的设计目的是为了配置化入口的定义.
通过继承和覆盖基类中的特定字段和方法来实现入口的参数配置读取.

目前的实现可以依次从指定路径下的json文件,环境变量,命令行参数读取需要的数据.
然后校验是否符合设定的json schema规定的模式,在符合模式后执行注册进去的回调函数.

入口树中可以有中间节点,用于分解复杂命令行参数,中间节点不会执行.
他们将参数传递给下一级节点,直到尾部可以执行为止.

Example:
>>> class ppm(EntryPoint):
...     """ppm <subcmd> [<args>]
...     ppm工具的子命令有:
...         工具自身相关:
...         help              展示ppm的帮助说明
...         version           展示ppm的版本
...         reset             将ppm工具的设置初始化
...         cache             管理ppm的缓存
...     """
...     epilog = ''
...     description = '项目脚手架'

>>> main = ppm()

>>> class help(EntryPoint):
...     """帮助信息.
...     ppm help <subcommand>
...     ppm工具的子命令有:
...         工具自身相关:
...         help              展示ppm的帮助说明
...         version           展示ppm的版本
...         reset             将ppm工具的设置初始化
...         cache             管理ppm的缓存
...     """
...     description='查看子命令的帮助说明'

>>> main_help = main.regist_sub(help)
>>> @main_help.regist_callback
... def printconfig(config):
...     print("1231")
...     print(config)

>>> main(["help"])
1231
{}

'''
import os
import sys
import json
import warnings
import argparse
import functools
from pathlib import Path
from typing import Callable, Sequence,List,Dict, Any, Optional

from jsonschema import validate


def _get_parent_tree(c: "EntryPoint", result: List[str]) -> None:
    if c.parent:
        result.append(c.parent.name)
        _get_parent_tree(c.parent, result)
    else:
        return


def get_parent_tree(c: "EntryPoint") -> List[str]:
    """获取父节点树.

    Args:
        c (EntryPoint): 节点类

    Returns:
        List[str]: 父节点树

    """
    result_list: List[str] = []
    _get_parent_tree(c, result_list)
    return list(reversed(result_list))


class EntryPoint:
    """入口类基类."""

    epilog: str = ""
    description: str = ""
    parent: Optional["EntryPoint"] = None

    schema: Optional[Dict[str, Any]] = None

    default_config_file_paths: Sequence[str] = []
    env_prefix: Optional[str] = None

    _subcmds: Dict[str, "EntryPoint"]
    _callbacks: List[Callable[[Dict[str, Any]], None]]
    _config: Dict[str, Any]

    def __init__(self) -> None:
        self._subcmds = {}
        self._callbacks = []
        self._config = {}

    @property
    def name(self) -> str:
        """实例的名字.

        实例名字就是它的构造类名.
        """
        return self.__class__.__name__

    @property
    def prog(self) -> str:
        """命令路径."""
        parent_list = get_parent_tree(self)
        parent_list.append(self.name)
        return " ".join(parent_list)

    @property
    def config(self) -> Dict[str, Any]:
        """执行配置."""
        return self._config

    def regist_subcmd(self, subcmd: "EntryPoint") -> None:
        """注册子命令.

        Args:
            subcmd (EntryPoint): 子命令的实例

        """
        subcmd.parent = self
        self._subcmds[subcmd.name] = subcmd

    def regist_sub(self, subcmdclz: type) -> "EntryPoint":
        """注册子命令.

        Args:
            subcmdclz (EntryPoint): 子命令的定义类

        Returns:
            [EntryPoint]: 注册类的实例

        """
        instance = subcmdclz()
        self.regist_subcmd(instance)
        return instance

    def regist_callback(self, func: Callable[[Dict[str, Any]], None]) -> Callable[[Dict[str, Any]], None]:
        """注册函数在解析参数成功后执行.

        执行顺序按被注册的顺序来.

        Args:
            func (Callable[[Dict[str,Any]],None]): 待执行的参数.

        """
        @functools.wraps(func)
        def warp(config: Dict[str, Any]) -> None:
            return func(config)

        self._callbacks.append(warp)
        return warp

    def __call__(self, argv: Sequence[str]) -> None:
        """执行命令.

        如果当前的命令节点不是终点(也就是下面还有子命令)则传递参数到下一级;
        如果当前节点已经是终点则解析命令行参数,环境变量,指定路径后获取参数,然后构造成配置,并检验是否符合定义的json schema模式.
        然后如果通过验证并有注册执行函数的话则执行注册的函数.

        Args:
            argv (Sequence[str]): [description]

        """
        parser = argparse.ArgumentParser(
            prog=self.prog,
            epilog=self.epilog,
            description=self.description,
            usage=self.__doc__)
        if len(self._subcmds) != 0:
            self.pass_args_to_sub(parser, argv)
        else:
            self.parse_args(parser, argv)

    def pass_args_to_sub(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> None:
        """解析复杂命令行参数并将参数传递至下一级."""
        parser.add_argument('subcmd', help='执行子命令')
        args = parser.parse_args(argv[0:1])
        if self._subcmds.get(args.subcmd):
            self._subcmds[args.subcmd](argv[1:])
        else:
            print(f'未知的子命令 {argv[1:]}')
            parser.print_help()
            sys.exit(1)

    def parse_commandline_args(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> Dict[str, Any]:
        """默认端点不会再做命令行解析,如果要做则需要在继承时覆盖此方法."""
        return {}

    def _parse_env_args_by_type(self, value_str: str, info: Dict[str, Any]) -> Any:
        t = info.get("type")
        if not t:
            return value_str
        elif t == "string":
            return value_str
        elif t == "number":
            return float(value_str)
        elif t == "integer":
            return int(value_str)
        elif t == "boolean":
            value_u = value_str.upper()
            return True if value_u == "TRUE" else False
        elif t == "array":
            item_info = info.get("items")
            if not item_info:
                return value_str.split(",")
            else:
                return [self._parse_env_args_by_type(i, item_info) for i in value_str.split(",")]
        elif t == "object":
            properties = info.get("properties")
            if not properties:
                result = {}
                for i in value_str.split(";"):
                    key, value = i.split(":")
                    result[key] = value
                return result
            else:
                result = {}
                for i in value_str.split(";"):
                    key, value_s = i.split(":")
                    item_info = properties.get(key)
                    if not item_info:
                        result[key] = value_s
                    else:
                        result[key] = self._parse_env_args_by_type(value_s, item_info)
                return result
        elif t == "null":
            return None
        else:
            warnings.warn(f"未知的数据类型{t}")
            return value_str

    def _parse_env_args(self, key: str, info: Dict[str, Any]) -> Any:
        if self.env_prefix:
            env_prefix = self.env_prefix.upper()
        else:
            env_prefix = self.prog.replace(" ", "_").upper()
        env = os.environ.get(f"{env_prefix}_{key.upper()}")
        if not env:
            if info.get("default"):
                env = info.get("default")
            else:
                env = None
        else:
            env = self._parse_env_args_by_type(env, info)
        return env

    def parse_env_args(self) -> Dict[str, Any]:
        """从环境变量中读取配置.

        必须设定json schema才能从环境变量中读取配置.
        程序会读取schema结构,并解析其中的`properties`字段.如果没有定义schema则不会解析环境变量.

        如果是列表型的数据,那么使用`,`分隔,如果是object型的数据,那么使用`key:value;key:value`的形式分隔

        Returns:
            Dict[str,Any]: 环境变量中解析出来的参数.

        """
        properties: Dict[str, Any]
        if self.schema:
            properties = self.schema.get("properties", {})
            result = {}
            for key, info in properties.items():
                value = self._parse_env_args(key, info)
                result.update({
                    key: value
                })
            return result
        else:
            return {}

    def parse_configfile_args(self) -> Dict[str, Any]:
        """从指定的配置文件队列中构造配置参数.

        目前只支持json格式的配置文件.
        指定的配置文件路径队列中第一个json格式且存在的配置文件将被读取解析.
        一旦读取到了配置后面的路径将被忽略.

        Args:
            argv (Sequence[str]): 配置的可能路径

        Returns:
            Dict[str,Any]: 从配置文件中读取到的配置

        """
        if len(self.default_config_file_paths) == 0:
            return {}
        else:
            for p_str in self.default_config_file_paths:
                p = Path(p_str)
                if p.is_file():
                    if p.suffix == ".json":
                        with open(p, "r", encoding="utf-8") as f:
                            result = json.load(f)
                        return result
                    else:
                        warnings.warn(f"跳过不支持的配置格式的文件{str(p)}")
                        continue
            else:
                warnings.warn(f"配置文件的指定路径都不可用.")
                return {}

    def validat_config(self) -> bool:
        """校验配置.

        Returns:
            bool: 是否通过校验

        """
        if self.schema and self.config:
            try:
                validate(instance=self.config, schema=self.schema)
            except Exception as e:
                warnings.warn(str(e))
                return False
            else:
                return True
        else:
            warnings.warn("必须有schema和config才能校验.")
            return True

    def do_callback(self) -> None:
        """执行回调."""
        for callback in self._callbacks:
            callback(self.config)

    def parse_args(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> None:
        """解析参数.

        解析顺序: 指定的文件->环境变量->命令行参数.

        执行顺序: 解析配置->校验配置->执行回调

        Args:
            argv (Sequence[str]): 命令行参数.

        """
        file_config = self.parse_configfile_args()
        self._config.update(file_config)
        env_config = self.parse_env_args()
        self._config.update(env_config)
        cmd_config = self.parse_commandline_args(parser, argv)
        self._config.update(cmd_config)
        if self.validat_config():
            self.do_callback()
