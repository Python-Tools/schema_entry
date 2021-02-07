# 0.1.3

## bug修复

+ 修复了`boolean`型参数必须使用命令行设置为True否则一定被false覆盖的问题

# 0.1.2

## 新增特性

+ `EntryPoint`类可以直接在实例化时通过参数定义其`description`, `epilog`, `usage`, `name`等属性.这样我们就可以直接实例化`EntryPoint`构造节点而不用继承了.这一特性适合用在构造非叶子节点时.
+ 与其对应的,`.regist_sub`方法现在可以添加参数用于在实例化节点时放入参数

# 0.1.1

## bug修复

+ 解决自定义解析的配置文件不受``控制的问题
+ 解决打印出奇怪字符的问题

# 0.1.0

## 新特性

+ schema字段现在支持`title`和`$comment`字段了
+ schema中定义的`title`字段可以用于定义命令行的缩写

# 0.0.9

## 新特性

+ 可以使用`@regist_config_file_parser(config_file_name)`来注册如何解析特定命名的配置文件

# 0.0.8

## 新特性

+ 可以通过设置`load_all_config_file = True`来按设定顺序读取全部预设的配置文件位置

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
