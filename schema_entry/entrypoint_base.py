"""入口类的抽象基类."""
import abc
import argparse
from typing import Callable, Sequence, Dict, Any, Optional


class EntryPointABC(abc.ABC):
    """程序入口类

    Attributes::
        epilog (str): 命令行展示介绍时的epilog部分
        description (str): 命令行展示介绍时的介绍部分
        parent (Optional["EntryPointABC"]): 入口节点的父节点.Default None
        schema (Optional[Dict[str, Any]]): 入口节点的设置需要满足的json schema对应字典.Default None
        verify_schema (bool): 获得设置后节点是否校验设置是否满足定义的json schema模式
        default_config_file_paths (Sequence[str]): 设置默认的配置文件位置.
        env_prefix (str): 设置环境变量的前缀
        parse_env (bool): 展示是否解析环境变量

    """
    epilog: str
    description: str
    parent: Optional["EntryPointABC"]

    schema: Optional[Dict[str, Any]]
    verify_schema: bool

    default_config_file_paths: Sequence[str]
    env_prefix: Optional[str]
    parse_env: bool

    _subcmds: Dict[str, "EntryPointABC"]
    _main: Optional[Callable[[Dict[str, Any]], None]]
    _config: Dict[str, Any]

    @abc.abstractproperty
    def name(self) -> str:
        """实例的名字.

        实例名字就是它的构造类名.
        """

    @abc.abstractproperty
    def prog(self) -> str:
        """命令路径."""

    @abc.abstractproperty
    def config(self) -> Dict[str, Any]:
        """执行配置.

        配置为只读数据.
        """

    @abc.abstractmethod
    def regist_subcmd(self, subcmd: "EntryPointABC") -> None:
        """注册子命令.

        Args:
            subcmd (EntryPointABC): 子命令的实例

        """
    @abc.abstractmethod
    def regist_sub(self, subcmdclz: type) -> "EntryPointABC":
        '''注册子命令.

        Args:
            subcmdclz (EntryPointABC): 子命令的定义类

        Returns:
            [EntryPointABC]: 注册类的实例

        '''
    @abc.abstractmethod
    def as_main(self, func: Callable[[Dict[str, Any]], None]) -> Callable[[Dict[str, Any]], None]:
        """注册函数在解析参数成功后执行.

        执行顺序按被注册的顺序来.

        Args:
            func (Callable[[Dict[str,Any]],None]): 待执行的参数.

        """

    @abc.abstractmethod
    def __call__(self, argv: Sequence[str]) -> None:
        """执行命令.

        如果当前的命令节点不是终点(也就是下面还有子命令)则传递参数到下一级;
        如果当前节点已经是终点则解析命令行参数,环境变量,指定路径后获取参数,然后构造成配置,并检验是否符合定义的json schema模式.
        然后如果通过验证并有注册执行函数的话则执行注册的函数.

        Args:
            argv (Sequence[str]): [description]

        """
    @abc.abstractmethod
    def pass_args_to_sub(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> None:
        """解析复杂命令行参数并将参数传递至下一级."""

    @abc.abstractmethod
    def parse_commandline_args(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> Dict[str, Any]:
        '''默认端点不会再做命令行解析,如果要做则需要在继承时覆盖此方法.

        Args:
            parser (argparse.ArgumentParser): 命令行解析对象
            argv (Sequence[str]): 待解析的参数列表

        Returns:
            Dict[str, Any]: 配置

        '''

    @abc.abstractmethod
    def parse_env_args(self) -> Dict[str, Any]:
        """从环境变量中读取配置.

        必须设定json schema,且parse_env为True才能从环境变量中读取配置.
        程序会读取schema结构,并解析其中的`properties`字段.如果没有定义schema则不会解析环境变量.

        如果是列表型的数据,那么使用`,`分隔,如果是object型的数据,那么使用`key:value;key:value`的形式分隔

        Returns:
            Dict[str,Any]: 环境变量中解析出来的参数.

        """

    @abc.abstractmethod
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

    @abc.abstractmethod
    def validat_config(self) -> bool:
        """校验配置.

        在定义好schema,解析到config并且verify_schema为True后才会进行校验.


        Returns:
            bool: 是否通过校验

        """

    @abc.abstractmethod
    def do_main(self) -> None:
        """执行入口函数."""

    @abc.abstractmethod
    def parse_args(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> None:
        """解析获取配置

        配置的加载顺序为: 指定路径的配置文件->环境变量->命令行参数

        在加载完配置后校验是否满足schema的要求.

        Args:
            parser (argparse.ArgumentParser): [description]
            argv (Sequence[str]): [description]
        """