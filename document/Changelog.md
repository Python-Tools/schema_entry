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
