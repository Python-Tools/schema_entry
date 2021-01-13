# 0.0.7

## 新特性

+ 可以通过设置字段`config_file_only_get_need`来控制从配置文档中读取数据时是全量读取还是根据schema的定义读取.默认为`True`
+ 默认新增一个命令行flag`--config/-c`来指定一个路径用于读取配置文件,其行为和默认位置配置文件一致.

# 0.0.6

## 修复bug

+ 修复了每一级子命令都会打印epilog的bug

## 新特性

+ `array`类型的参数现在也可以被作为命令行中的noflag字段了.它的输入行为使用`nargs="+"`的形式

# 0.0.5

## 修复bug

+ 修复了`array`类型无法设置`enum`的问题

# 0.0.4

## 修复bug

+ `verify_schema`被设置为False时不会抛出警告
+ 对环境变量的解析不会再有`None`
+ 环境变量不会再解析默认值

## 新特性

+ 中间节点的的`--help`命令会在底部展示子命令的简介.简介内容为子命令的`docstring`

# 0.0.3

## 修复bug

+ array类型的协议定义无法解析item的问题

# 0.0.2

## 新增功能

+ array类型可以设置默认值

# 0.0.1

## 新增功能

+ 实现了如下基本功能
    + `default_config_file_paths字段`可以读取yaml格式的配置文件

# 0.0.0

## 新增功能

+ 实现了如下基本功能
    + 根据子类的名字构造命令
    + 入口节点可以通过方法`regist_sub`和`regist_subcmd`注册子节点
    + 根据子类的docstring,`epilog字段`和`description字段`自动构造,命令行说明.
    + 根据子类的`schema字段`和`env_prefix字段`自动构造环境变量的读取规则.
    + 根据子类的`default_config_file_paths字段`自动按顺序读取json格式配置文件中的参数.
    + 根据`schema字段`校验配置
    + 根据`schema字段`构造命令行参数
    + 使用装饰器`as_main`注册获取到配置后执行的函数
