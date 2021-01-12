"""入口树的构造工具.

这个基类的设计目的是为了配置化入口的定义.
通过继承和覆盖基类中的特定字段和方法来实现入口的参数配置读取.

目前的实现可以依次从指定路径下的json文件,环境变量,命令行参数读取需要的数据.
然后校验是否符合设定的json schema规定的模式,在符合模式后执行注册进去的回调函数.

入口树中可以有中间节点,用于分解复杂命令行参数,中间节点不会执行.
他们将参数传递给下一级节点,直到尾部可以执行为止.

"""
import os
import sys
import json
import warnings
import argparse
import functools
from copy import deepcopy
from pathlib import Path
from typing import Callable, Sequence, Dict, List, Any, Tuple
from jsonschema import validate
from yaml import load as yaml_load

from .protocol import SUPPORT_SCHEMA
from .utils import get_parent_tree, parse_value_string_by_schema, parse_schema_as_cmd
from .entrypoint_base import EntryPointABC


class EntryPoint(EntryPointABC):
    epilog = ""
    usage = ""
    _name = ""
    parent = None

    schema = None
    verify_schema = True

    default_config_file_paths: List[str] = []
    config_file_only_get_need = True
    env_prefix = None
    parse_env = True

    argparse_check_required = False
    argparse_noflag = None

    def _check_schema(self) -> None:
        if self.schema is not None:
            try:
                validate(instance=self.schema, schema=SUPPORT_SCHEMA)
            except Exception as e:
                warnings.warn(str(e))
                raise e
                # sys.exit(1)

    def __init__(self) -> None:
        self._check_schema()
        self._subcmds = {}
        self._main = None
        self._config = {}

    @ property
    def name(self) -> str:
        return self._name if self._name else self.__class__.__name__.lower()

    @ property
    def prog(self) -> str:
        parent_list = get_parent_tree(self)
        parent_list.append(self.name)
        return " ".join(parent_list)

    @ property
    def config(self) -> Dict[str, Any]:
        return deepcopy(self._config)

    def regist_subcmd(self, subcmd: EntryPointABC) -> None:
        subcmd.parent = self
        self._subcmds[subcmd.name] = subcmd

    def regist_sub(self, subcmdclz: type) -> EntryPointABC:
        instance = subcmdclz()
        self.regist_subcmd(instance)
        return instance

    def as_main(self, func: Callable[..., None]) -> Callable[..., None]:
        @ functools.wraps(func)
        def warp(*args: Any, **kwargs: Any) -> None:
            return func(*args, **kwargs)

        self._main = warp
        return warp

    def __call__(self, argv: Sequence[str]) -> None:
        if not self.usage:
            if len(self._subcmds) == 0:
                self.usage = f"{self.prog} [options]"
            else:
                self.usage = f"{self.prog} [subcmd]"
        parser = argparse.ArgumentParser(
            prog=self.prog,
            epilog=self.epilog,
            description=self.__doc__,
            usage=self.usage)
        if len(self._subcmds) != 0:
            if self.epilog:
                epilog = self.epilog
            else:
                epilog = "子命令描述:\n" + "\n".join([f"{subcmd}\t{ins.__doc__}" for subcmd, ins in self._subcmds.items()])
            parser = argparse.ArgumentParser(
                prog=self.prog,
                epilog=epilog,
                description=self.__doc__,
                usage=self.usage,
                formatter_class=argparse.RawDescriptionHelpFormatter)
            self.pass_args_to_sub(parser, argv)
        else:
            parser = argparse.ArgumentParser(
                prog=self.prog,
                epilog=self.epilog,
                description=self.__doc__,
                usage=self.usage)
            self.parse_args(parser, argv)

    def pass_args_to_sub(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> None:
        scmds = list(self._subcmds.keys())
        scmdss = ",".join(scmds)
        parser.add_argument('subcmd', help=f'执行子命令，可选的子命有{scmdss}')
        args = parser.parse_args(argv[0:1])
        if self._subcmds.get(args.subcmd):
            self._subcmds[args.subcmd](argv[1:])
        else:
            print(f'未知的子命令 `{argv[0]}`')
            parser.print_help()
            sys.exit(1)

    def _make_commandline_parse_by_schema(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        if self.schema is None:
            raise AttributeError("此处不该被执行")
        else:
            properties: Dict[str, Any] = self.schema.get("properties", {})
            requireds: List[str] = self.schema.get("required", [])
            for key, prop in properties.items():
                required = False
                noflag = False
                if self.argparse_noflag == key:
                    noflag = True
                else:
                    if self.argparse_check_required and key in requireds:
                        required = True
                parser = parse_schema_as_cmd(key, prop, parser, required=required, noflag=noflag)
            return parser

    def _parse_commandline_args_by_schema(self,
                                          parser: argparse.ArgumentParser,
                                          argv: Sequence[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if self.schema:
            parser = self._make_commandline_parse_by_schema(parser)
        args = parser.parse_args(argv)
        config_file_res: Dict[str, Any] = {}
        cmd_res: Dict[str, Any] = {}
        for key, value in vars(args).items():
            if key == "config":
                if value:
                    p = Path(value)
                    if not p.is_file():
                        warnings.warn(f"{str(p)}不是文件")
                        continue
                    if p.suffix == ".json":
                        config_file_res = self.parse_json_configfile_args(p)
                    elif p.suffix == ".yml":
                        config_file_res = self.parse_yaml_configfile_args(p)
                    else:
                        warnings.warn(f"跳过不支持的配置格式的文件{str(p)}")
                        continue
                else:
                    continue
            else:
                if value is not None:
                    cmd_res.update({
                        key: value
                    })
        return config_file_res, cmd_res

    def parse_commandline_args(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """解析命令行获得参数

        Args:
            parser (argparse.ArgumentParser): 命令行解析器
            argv (Sequence[str]): 命令行参数序列

        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: 命令行指定配置文件获得的参数,其他命令行参数获得的参数
        """

        parser.add_argument("-c", "--config", type=str, help='指定配置文件位置')
        return self._parse_commandline_args_by_schema(parser, argv)

    def _parse_env_args(self, key: str, info: Dict[str, Any]) -> Any:
        if self.env_prefix:
            env_prefix = self.env_prefix.upper()
        else:
            env_prefix = self.prog.replace(" ", "_").upper()
        key = key.replace("-", "_")
        env = os.environ.get(f"{env_prefix}_{key.upper()}")
        if not env:
            env = None
        else:
            env = parse_value_string_by_schema(info, env)
        return env

    def parse_env_args(self) -> Dict[str, Any]:
        properties: Dict[str, Any]
        if self.schema and self.parse_env:
            properties = self.schema.get("properties", {})
            result = {}
            for key, info in properties.items():
                value = self._parse_env_args(key, info)
                if value is not None:
                    result.update({
                        key: value
                    })
            return result
        else:
            return {}

    def parse_json_configfile_args(self, p: Path) -> Dict[str, Any]:
        with open(p, "r", encoding="utf-8") as f:
            result = json.load(f)
        if self.config_file_only_get_need and self.schema is not None and self.schema.get("properties") is not None:
            needs = list(self.schema.get("properties").keys())
            res = {}
            for key in needs:
                if result.get(key) is not None:
                    res[key] = result.get(key)
            return res
        return result

    def parse_yaml_configfile_args(self, p: Path) -> Dict[str, Any]:
        with open(p, "r", encoding="utf-8") as f:
            result = yaml_load(f)
        if self.config_file_only_get_need and self.schema is not None and self.schema.get("properties") is not None:
            needs = list(self.schema.get("properties").keys())
            res = {}
            for key in needs:
                if result.get(key) is not None:
                    res[key] = result.get(key)
            return res
        return result

    def parse_configfile_args(self) -> Dict[str, Any]:
        if not self.default_config_file_paths:
            return {}
        for p_str in self.default_config_file_paths:
            p = Path(p_str)
            if p.is_file():
                if p.suffix == ".json":
                    return self.parse_json_configfile_args(p)
                elif p.suffix == ".yml":
                    return self.parse_yaml_configfile_args(p)
                else:
                    warnings.warn(f"跳过不支持的配置格式的文件{str(p)}")
        else:
            warnings.warn("配置文件的指定路径都不可用.")
            return {}

    def validat_config(self) -> bool:
        if self.verify_schema:
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
        else:
            return True

    def do_main(self) -> None:
        if self._main is None:
            print("未注册main函数")
            sys.exit(1)
        else:
            config = self.config
            self._main(**config)

    def parse_default(self) -> Dict[str, Any]:
        if self.schema:
            prop = self.schema.get("properties")
            if prop:
                return {key: sch.get("default") for key, sch in prop.items() if sch.get("default")}
            return {}
        return {}

    def parse_args(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> None:
        # 默认配置
        default_config = self.parse_default()
        self._config.update(default_config)
        # 默认配置文件配置
        file_config = self.parse_configfile_args()
        self._config.update(file_config)
        # 命令行指定配置文件配置
        cmd_config_file_config, cmd_config = self.parse_commandline_args(parser, argv)
        self._config.update(cmd_config_file_config)
        # 环境变量配置
        env_config = self.parse_env_args()
        self._config.update(env_config)
        # 命令行指定配置
        self._config.update(cmd_config)
        if self.validat_config():
            self.do_main()
        else:
            sys.exit(1)
