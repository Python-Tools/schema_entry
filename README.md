# entry-tree

入口树的构造工具.

这个基类的设计目的是为了配置化入口的定义.通过继承和覆盖基类中的特定字段和方法来实现入口的参数配置读取.

目前的实现可以依次从指定路径下的json文件,环境变量,命令行参数读取需要的数据.
然后校验是否符合设定的json schema规定的模式,在符合模式后执行注册进去的回调函数.

入口树中可以有中间节点,用于分解复杂命令行参数,中间节点不会执行.
他们将参数传递给下一级节点,直到尾部可以执行为止.


## Features

+ 从默认文件路径,环境变量,命令行参数中获取配置参数
+ 通过jsonschema的定义构造环境变量的获取行为
+ 配置参数通过jsonschema进行检验
+ 可以构造多级命令行命令

## Install

## Document

