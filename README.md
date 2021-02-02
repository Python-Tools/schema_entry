# 简介

程序入口的构造工具.

这个基类的设计目的是为了配置化入口的定义.通过继承和覆盖基类中的特定字段和方法来实现入口的参数配置读取.

目前的实现可以依次从指定路径下的json文件,环境变量,命令行参数读取需要的数据.
然后校验是否符合设定的json schema规定的模式,在符合模式后执行注册进去的回调函数.

入口树中可以有中间节点,用于分解复杂命令行参数,中间节点不会执行.
他们将参数传递给下一级节点,直到尾部可以执行为止.

# 特性

+ 根据子类的名字小写构造命令
+ 根据子类的docstring,`epilog字段`和`description字段`自动构造,命令行说明.
+ 根据子类的`schema字段`和`env_prefix字段`自动构造环境变量的读取规则.
+ 根据子类的`default_config_file_paths字段`自动按顺序读取json,yaml格式配置文件中的参数.
+ 根据`schema字段`构造命令行参数和配置校验
+ 使用装饰器`@as_main`注册获取到配置后执行的函数
+ 通过覆写`parse_commandline_args`方法来定义命令行参数的读取
+ 入口节点可以通过方法`regist_sub`注册子节点

# 安装

```bash
pip install schema_entry
```

# 使用介绍

## 动机

`schema_entry`模块提供了一个基类`EntryPoint`用于构造复杂的程序入口.通常我们的程序入口参数有3个途径:

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
2. 执行节点,比如`docker run`,这种就是`可以执行的节点`.

本模块的基本用法是:

1. 通过继承`EntryPoint`类并覆写其中的字段来定义不同的节点

2. 通过实例化`EntryPoint`的子类并使用其实例方法`regist_subcmd`或者`regist_sub`来定义不同节点的类型和节点的调用顺序

3. 使用`可以执行节点`的实例方法`as_main`(装饰器)来指定不同节点的入口函数.

4. 命令行中按`根节点`到`可以执行节点`的顺序输入构造命令,获取来自配置文件,环境变量,命令行参数中的参数,作为注册入口函数的参数调用入口函数.

### 节点名

我们可以定义`_name`字段为节点命名,如果没有那么节点名则为子类类名的全小写形式.

### 节点的帮助信息

我们可以定义`usage`来定义用法帮助字符串,如果没有定义则会自动构造,中间节点会是`root subcmd ... [subcmd]`;
可执行节点会是`root subcmd ... entry [options]`

### 执行节点

上面说过执行节点的任务有3个:

1. 从配置文件,环境变量,命令行参数获取配置参数
2. [可选]校验配置参数是否符合要求
3. [可选]将配置作为参数引用到程序中.

#### 通过定义`schema字段进行参数校验`

我们可以定义`schema字段`来激活校验功能

```python
class Test_A(EntryPoint):
    default_config_file_paths = [
        "/test_config.json",
        str(Path.home().joinpath(".test_config.json")),
        "./test_config.json"
    ]
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "a": {
                "type": "integer"
            }
        },
        "required": ["a"]
    }
```

`EntryPoint`的子类会在解析获得参数后校验参数字典是否符合schema中定义的模式.

当然schema字段也不能乱写,它的规则是json schema的一个子集:

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "properties": {
            "type": "object",
            "minProperties": 1,
            "additionalProperties": False,
            "patternProperties": {
                "^\\w+$": {
                    "oneOf": [
                        {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "boolean"
                                },
                                "default": {
                                    "type": "boolean",
                                },
                                "const": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                },
                                "$comment": {
                                    "type": "string"
                                },
                                "title": {
                                    "type": "string",
                                    "pattern": "^[a-b]|[d-z]$"
                                }
                            }
                        },
                        {
                            "type": "object",
                            "additionalProperties": false,
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "string"
                                },
                                "default": {
                                    "type": "string",
                                },
                                "const": {
                                    "type": "string"
                                },
                                "enum": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                "maxLength": {
                                    "type": "integer",
                                    "minimum": 0
                                },
                                "minLength": {
                                    "type": "integer",
                                    "minimum": 0
                                },
                                "pattern": {
                                    "type": "string"
                                },
                                "format": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                },
                                "$comment": {
                                    "type": "string"
                                },
                                "title": {
                                    "type": "string",
                                    "pattern": r"^[a-b]|[d-z]$"
                                }
                            }
                        },
                        {
                            "type": "object",
                            "additionalProperties": false,
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "number"
                                },
                                "default": {
                                    "type": "number",
                                },
                                "const": {
                                    "type": "number"
                                },
                                "enum": {
                                    "type": "array",
                                    "items": {
                                        "type": "number"
                                    }
                                },
                                "maximum": {
                                    "type": "number",
                                },
                                "exclusiveMaximum": {
                                    "type": "number",
                                },
                                "minimum": {
                                    "type": "number",

                                },
                                "exclusiveMinimum": {
                                    "type": "number",

                                },
                                "description": {
                                    "type": "string"
                                },
                                "$comment": {
                                    "type": "string"
                                },
                                "title": {
                                    "type": "string",
                                    "pattern": "^[a-b]|[d-z]$"
                                }
                            }
                        },
                        {
                            "type": "object",
                            "additionalProperties": false,
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "integer"
                                },
                                "default": {
                                    "type": "integer",
                                },
                                "const": {
                                    "type": "integer"
                                },
                                "enum": {
                                    "type": "array",
                                    "items": {
                                        "type": "integer"
                                    }
                                },
                                "maximum": {
                                    "type": "integer",
                                },
                                "exclusiveMaximum": {
                                    "type": "integer",
                                },
                                "minimum": {
                                    "type": "integer",

                                },
                                "exclusiveMinimum": {
                                    "type": "integer",

                                },
                                "description": {
                                    "type": "string"
                                },
                                "$comment": {
                                    "type": "string"
                                },
                                "title": {
                                    "type": "string",
                                    "pattern": "^[a-b]|[d-z]$"
                                }
                            }
                        },
                        {
                            "type": "object",
                            "additionalProperties": false,
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "array"
                                },
                                "default": {
                                    "type": "array",
                                    "items": {
                                        "type": ["string", "number", "integer"]
                                    }
                                },
                                "items": {
                                    "type": "object",
                                    "required": ["type"],
                                    "additionalProperties": false,
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["string", "number", "integer"]
                                        },
                                        "enum":{
                                            "type": "array"
                                        }
                                    }
                                },
                                "description": {
                                    "type": "string"
                                },
                                "$comment": {
                                    "type": "string"
                                },
                                "title": {
                                    "type": "string",
                                    "pattern": "^[a-b]|[d-z]$"
                                }
                            }
                        }
                    ]

                }
            }
        },
        "type": {
            "type": "string",
            "const": "object"
        },
        "required": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }

    },
    "required": ["properties", "type"]
}
```

简而言之就是:

1. 最外层必须有`properties`和`type`字段且`type`字段必须为`object`,可以有`required`字段
2. 最外层`properties`中的字段名必须是由`数字`,`字母`和`_`组成,
3. 字段类型只能是`string`,`boolean`,`number`,`integer`,`array`之一
4. 字段类型如果为`array`则内部必须要有`items`且`items`中必须有`type`字段,且该`type`字段的值必须为`string`,`number`,`integer`之一


如果我们不想校验,那么可以设置`verify_schema`为`False`强行关闭这个功能.

#### 从定义的schema中获取默认配置

我们在定义schema时可以在`"properties"`字段定义的模式描述中通过`default`字段指定描述字段的默认值

```python
class Test_A(EntryPoint):
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "a_a": {
                "type": "number"
                "default": 10.1
            }
        },
        "required": ["a_a"]
    }
```

这样即便没有其他输入这个参数也会有这个默认值兜底

#### 从指定配置文件中读取配置

我们可以使用字段`default_config_file_paths`指定从固定的几个路径中读取配置文件,配置文件支持`json`和`yaml`两种格式.
我们也可以通过字段`config_file_only_get_need`定义从配置文件中读取配置的行为(默认为`True`),
 当置为`True`时我们只会在配置文件中读取schema中定义的字段,否则则会加载全部字段.

也可以通过设置`load_all_config_file = True`来按设定顺序读取全部预设的配置文件位置

默认配置文件地址是一个列表,会按顺序查找读取,只要找到了满足条件的配置文件就会读取.

```python
from pathlib import Path
from schema_entry import EntryPoint

class Test_A(EntryPoint):

    default_config_file_paths = [
        "/test_config.json",
        str(Path.home().joinpath(".test_config.json")),
        "./test_config.json",
        "./test_config_other.json"
    ]
```

##### 指定特定命名的配置文件的解析方式

可以使用`@regist_config_file_parser(config_file_name)`来注册如何解析特定命名的配置文件.这一特性可以更好的定制化配置文件的读取

```python
class Test_AC(EntryPoint):
    load_all_config_file = True
    default_config_file_paths = [
        "./test_config.json",
        "./test_config1.json",
        "./test_other_config2.json"
    ]
root = Test_AC()

@root.regist_config_file_parser("test_other_config2.json")
def _1(p: Path) -> Dict[str, Any]:
    with open(p) as f:
        temp = json.load(f)
    return {k.lower(): v for k, v in temp.items()}

```

如果想在定义子类时固定好,也可以定义`_config_file_parser_map:Dict[str,Callable[[Path], Dict[str, Any]]]`

```python
def test_other_config2_parser( p: Path) -> Dict[str, Any]:
    with open(p) as f:
        temp = json.load(f)
    return {k.lower(): v for k, v in temp.items()}
class Test_AC(EntryPoint):
    load_all_config_file = True
    default_config_file_paths = [
        "./test_config.json",
        "./test_config1.json",
        "./test_other_config2.json"
    ]
    _config_file_parser_map = {
        "test_other_config2.json": test_other_config2_parser
    }

root = Test_AC()

```

#### 从环境变量中读取配置参数

要从环境变量中读取配置必须设置`schema`字段,`EntryPoint`会按照其中`properties`字段定义的字段范围和字段类型解析环境变量.

环境变量key的规则为`前缀_字段名的大写`.前缀的默认值为`...父节命令节点的父命令节点大写_父节命令节点大写_子命令节点大写`.
我们也可以通过设定`env_prefix`字段来替换默认前缀,替换的前缀依然会被转化为大写.

```python
class Test_A(EntryPoint):
    env_prefix = "app"
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "a_a": {
                "type": "number"
            }
        },
        "required": ["a_a"]
    }
```

如果我们不希望从环境变量中解析配置,那么也可以设置`parse_env`为`False`

#### 从命令行参数中获取配置参数

当我们定义好`schema`后所有schema中定义好的参数都可以以`--xxxx`的形式从命令行中读取,需要注意schema中定义的字段中`_`会被修改为`-`.
如果定义的字段模式中含有`title`字段,则使用title字段作为命令行缩写即`-x`的形式

这个命令行读取是使用的标准库`argparse`,构造出的解析器中`useage`,`epilog`和`description`会由类中定义的`usage`,`epilog`和docstring决定;`argv`则为传到节点处时剩下的命令行参数(每多一个节点就会从左侧摘掉一个命令行参数).

通常情况下构造的命令行解析器全部都是可选项,如果我们希望指定`schema`中一项是没有`--`的那种配置,那么可以在定义类时指定`argparse_noflag`为想要的字段,如果希望命令行中校验必填项则可以在定义类时指定`argparse_check_required=True`.需要注意如果一个字段被指定为了`noflag`那么它就是必填项了.

```python
class Test_A(EntryPoint):
    argparse_noflag = "a"
    argparse_check_required=True
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "a": {
                "type": "number"
            },
            "b": {
                "type": "number"
            }
        },
        "required": ["a","b"]
    }
```

命令行中默认使用`-c`/`--config`来指定读取配置文件,它的读取行为受上面介绍的从自定义配置文件中读取配置的设置影响.

#### 配置的读取顺序

配置的读取顺序为`schema中定义的default值`->`配置指定的配置文件路径`->`命令行指定的配置文件`->`环境变量`->`命令行参数`,而覆盖顺序则是反过来.

#### 注册入口的执行函数

我们使用实例的装饰器方法`as_main`来实现对执行节点入口函数的注册,注册的入口函数会在解析好参数后执行,其参数就是解析好的`**config`

```python

root = Test_A()
@root.as_main
def main(a,b):
    print(a)
    print(b)

```

另一种指定入口函数的方法是重写子类的`do_main(self)->None`方法

```python
class Test_A(EntryPoint):
    argparse_noflag = "a"
    argparse_check_required=True
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "a": {
                "type": "number"
            },
            "b": {
                "type": "number"
            }
        },
        "required": ["a","b"]
    }
    def do_main(self)->None:
        print(self.config)
```

#### 直接从节点对象中获取配置

节点对象的`config`属性会在每次调用时copy一份当前的配置值,config是不可写的.

```python
print(root.config)
```

### 中间节点

中间节点并不能执行程序,它只是用于描述一个范围内的命令集合,因此它的作用就是充当`help`指令.我们定义中间节点并不能执行.但必须有至少一个子节点才是中间节点.因此即便一个节点定义了上面的配置,只要它有子节点就不会按上面的执行流程执行.

利用中间节点我们可以构造出非常复杂的启动命令树.

#### 注册子节点

中间节点的注册有两个接口

+ `regist_subcmd`用于注册一个已经实例化的子节点

    ```python
    class A(EntryPoint):
        pass

    class B(EntryPoint):
        pass

    a = A()

    b = B()

    a.regist_subcmd(b)
    ```

+ `regist_sub`用于注册一个子节点类,它会返回被注册的节点的一个实例

    ```python
    class A(EntryPoint):
        pass

    class B(EntryPoint):
        pass

    a = A()
    b =a.regist_sub(B)
    ```
