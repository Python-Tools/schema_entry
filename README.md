# 简介

入口树的构造工具.

这个基类的设计目的是为了配置化入口的定义.通过继承和覆盖基类中的特定字段和方法来实现入口的参数配置读取.

目前的实现可以依次从指定路径下的json文件,环境变量,命令行参数读取需要的数据.
然后校验是否符合设定的json schema规定的模式,在符合模式后执行注册进去的回调函数.

入口树中可以有中间节点,用于分解复杂命令行参数,中间节点不会执行.
他们将参数传递给下一级节点,直到尾部可以执行为止.


# 特性

+ 根据子类的名字构造命令
+ 根据子类的docstring,`epilog字段`和`description字段`自动构造,命令行说明.
+ 根据子类的`schema字段`和`env_prefix字段`自动构造环境变量的读取规则.
+ 根据子类的`default_config_file_paths字段`自动按顺序读取json格式配置文件中的参数.
+ 根据`schema字段`校验配置
+ 使用装饰器`regist_runner`注册获取到配置后执行的函数
+ 通过覆写`parse_commandline_args`方法来定义命令行参数的读取
+ 入口节点可以通过方法`regist_sub`注册子节点

# 安装

# 文档

# 使用介绍

## 动机

`entry_tree`模块提供了一个基类`EntryPoint`用于构造复杂的程序入口.通常我们的程序入口参数有3个途径:

1. 配置文件
2. 环境变量
3. 命令行参数

在docker广泛应用之前可能用的最多的是命令行参数.但在docker大行其道的现在,配置文件(docker config)和环境变量(environment字段)变得更加重要.

随之而来的是参数的校验问题,python标准库`argparse`本身有不错的参数约束能力,但配置文件中的和环境变量中的参数就需要额外校验了.

这个项目的目的是简化定义入口这个非常通用的业务,将代码尽量配置化.

## 使用方法

首先我们来分析下一个入口形式.

通常一个程序的入口可能简单也可能复杂,但无非两种

1. 中间节点,比如`docker stack`, 它本质上并不执行操作,它只是表示要执行的是关于子模块的操作.当单独执行这条命令时实际上它什么都没做,它下面的子命令`git submodule add`这类才是实际可以执行的节点.而我定义这种中间节点单独被执行应该打印其帮助说明文本.
2. 执行节点,比如`docker run`,这种就是可以执行的节点.

### 执行节点

上面说过执行节点的任务有3个:

1. 从配置文件,环境变量,命令行参数获取配置参数
2. [可选]校验配置参数是否符合要求
3. [可选]将配置作为参数引用到程序中.

#### 从配置文件中读取配置参数

默认配置文件地址是一个列表,会按顺序查找读取,只要找到了满足条件的配置文件就会读取.

```python
from pathlib import Path
from entry_tree import EntryPoint

class ppm(EntryPoint):
    default_config_file_paths=[
        "/test_config.json",
        str(Path.Home().joinpath(".test_config.json")),
        "./test_config.json"
    ]

```

#### 从环境变量中读取配置参数

要从环境变量中读取配置必须设置`schema`字段,`EntryPoint`会按照其中`properties`字段定义的字段范围和字段类型解析环境变量.

环境变量key的规则为`前缀_字段名的大写`.前缀的默认值为`...父节命令节点的父命令节点大写_父节命令节点大写_子命令节点大写`.
我们也可以通过设定`env_prefix`字段来替换默认前缀,替换的前缀依然会被转化为大写.


```python
class ppm(EntryPoint):
    env_prefix = "app"
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
```

如果我们不希望从环境变量中解析配置,那么也可以设置`parse_env`为`False`

#### 从命令行参数中获取配置参数

从命令行参数中获取配置我们就需要复写方法`def parse_commandline_args(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> Dict[str, Any]`来实现了.

注意参数`parser`是已经创建好了但还未定义flag的命令行参数解析器,这个解析器的`useage`,`epilog`和`description`会由类中定义的docstring,`epilog`和`description`决定;`argv`则为传到节点处时剩下的命令行参数(每多一个节点就会从左侧摘掉一个命令行参数).

```python
class ppm(EntryPoint):
    """ppm <subcmd> [<args>]"""
    epilog = ""
    description = "项目脚手架"
    def parse_commandline_args(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> Dict[str, Any]:
        """默认端点不会再做命令行解析,如果要做则需要在继承时覆盖此方法."""
        parser.add_argument('a', type=int, help='a')
        args = parser.parse_args(argv)
        return vars(args)
```

#### 配置的读取顺序

配置的读取顺序为`配置文件`->`环境变量`->`命令行参数`

```python
class ppm(EntryPoint):
    """ppm <subcmd> [<args>]"""
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
    default_config_file_paths=["./test_config.json"]
    epilog = ""
    description = "项目脚手架"
    def parse_commandline_args(self, parser: argparse.ArgumentParser, argv: Sequence[str]) -> Dict[str, Any]:
        """默认端点不会再做命令行解析,如果要做则需要在继承时覆盖此方法."""
        parser.add_argument('a', type=float, help='a')
        args = parser.parse_args(argv)
        return vars(args)
```

像上面的定义,我们就会先查看`./test_config.json`,再查看环境变量,最后看定义好的命令行参数.

#### 校验配置

只要定义了`schema`那么默认我们就会校验配置是否符合定义.如果我们不想校验,那么可以设置`verify_schema`为`False`强行关闭这个功能.

#### 注册入口的执行函数

可以通过装饰器`regist_runner`来注册入口真正要执行的函数.同时可以通过装饰器`regist_before_running`和`regist_after_running`来注册在执行入口函数前后要执行的钩子.钩子和执行函数之间使用上下文参数`ctx`来传递中间值.



#### 直接从节点对象中获取配置

### 中间节点

中间节点并不能执行程序,它只是用于描述一个范围内的命令集合,因此它的作用就是充当`help`指令.我们定义中间节点并不能执行.但必须有至少一个子节点才是中间节点.因此即便一个节点定义了上面的配置,只要它有子节点就不会按上面的执行流程执行.


#### 注册子节点

#### 使用中间节点