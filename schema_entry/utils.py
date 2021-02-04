"""utils.

模块需要的工具.
"""
import warnings
import argparse
from typing import List, Dict, Any, Optional
from .entrypoint_base import EntryPointABC


def _get_parent_tree(c: EntryPointABC, result: List[str]) -> None:
    if c.parent:
        result.append(c.parent.name)
        _get_parent_tree(c.parent, result)
    else:
        return


def get_parent_tree(c: EntryPointABC) -> List[str]:
    """获取父节点树.

    Args:
        c (EntryPoint): 节点类

    Returns:
        List[str]: 父节点树

    """
    result_list: List[str] = []
    _get_parent_tree(c, result_list)
    return list(reversed(result_list))


def parse_value_string_by_schema(schema: Dict[str, Any], value_str: str) -> Any:
    """根据schema的定义解析字符串的值.

    Args:
        schema (Dict[str, Any]): 描述字符串值的json schema字典.
        value_str (str): 待解析的字符串.

    Returns:
        Any: 字段的值

    """
    t = schema.get("type")
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
        item_info = schema.get("items")
        if not item_info:
            return value_str.split(",")
        else:
            return [parse_value_string_by_schema(item_info, i) for i in value_str.split(",")]
    else:
        warnings.warn(f"不支持的数据类型{t}")
        return value_str


def _argparse_base_handdler(_type: Any, key: str, schema: Dict[str, Any], parser: argparse.ArgumentParser, *,
                            required: bool = False, noflag: bool = False) -> argparse.ArgumentParser:
    kwargs: Dict[str, Any] = {}
    kwargs.update({
        "type": _type
    })
    _enum = schema.get("enum")
    if _enum:
        kwargs.update({
            "choices": _enum
        })
    _description = schema.get("description")
    if _description:
        kwargs.update({
            "help": _description
        })
    if required:
        kwargs.update({
            "required": required
        })
    if noflag:
        parser.add_argument(f"{key}", **kwargs)
    else:
        if schema.get("title"):
            short = schema["title"][0]
            parser.add_argument(f"-{short}", f"--{key}", **kwargs)
        else:
            parser.add_argument(f"--{key}", **kwargs)
    return parser


def _argparse_number_handdler(key: str, schema: Dict[str, Any], parser: argparse.ArgumentParser, *,
                              required: bool = False, noflag: bool = False) -> argparse.ArgumentParser:
    return _argparse_base_handdler(float, key, schema, parser, required=required, noflag=noflag)


def _argparse_string_handdler(key: str, schema: Dict[str, Any], parser: argparse.ArgumentParser, *,
                              required: bool = False, noflag: bool = False) -> argparse.ArgumentParser:
    return _argparse_base_handdler(str, key, schema, parser, required=required, noflag=noflag)


def _argparse_integer_handdler(key: str, schema: Dict[str, Any], parser: argparse.ArgumentParser, *,
                               required: bool = False, noflag: bool = False) -> argparse.ArgumentParser:
    return _argparse_base_handdler(int, key, schema, parser, required=required, noflag=noflag)


def _argparse_boolean_handdler(key: str, schema: Dict[str, Any], parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    kwargs: Dict[str, Any] = {}
    kwargs.update({
        "action": "store_true"
    })
    _description = schema.get("description")
    if _description:
        kwargs.update({
            "help": _description
        })
    if schema.get("title"):
        short = schema["title"][0]
        parser.add_argument(f"-{short}", f"--{key}", **kwargs)
    else:
        parser.add_argument(f"--{key}", **kwargs)
    return parser


def _argparse_array_handdler(key: str, schema: Dict[str, Any], parser: argparse.ArgumentParser, *,
                             noflag: bool = False) -> argparse.ArgumentParser:
    sub_schema: Optional[Dict[str, Any]] = schema.get("items")
    if sub_schema is None:
        print("array params must have sub schema items")
        return parser
    sub_type = sub_schema.get("type")
    if sub_type not in ("number", "string", "integer"):
        print("array params item type must in number,string,integer")
        return parser
    kwargs: Dict[str, Any] = {}
    if sub_type == "number":
        kwargs.update({
            "type": float
        })
    elif sub_type == "string":
        kwargs.update({
            "type": str
        })
    elif sub_type == "integer":
        kwargs.update({
            "type": int
        })
    _default = schema.get("default")
    if _default:
        kwargs.update({
            "default": _default
        })
    _description = schema.get("description")
    if _description:
        kwargs.update({
            "help": _description
        })
    _enum = sub_schema.get("enum")
    if _enum:
        kwargs.update({
            "choices": _enum
        })

    if noflag:
        kwargs.update({
            "nargs": "+"
        })
        parser.add_argument(f"{key}", **kwargs)
    else:
        kwargs.update({
            "action": "append"
        })
        if schema.get("title"):
            short = schema["title"][0]
            parser.add_argument(f"-{short}", f"--{key}", **kwargs)
        else:
            parser.add_argument(f"--{key}", **kwargs)
    return parser


def parse_schema_as_cmd(key: str, schema: Dict[str, Any], parser: argparse.ArgumentParser, *,
                        required: bool = False, noflag: bool = False) -> argparse.ArgumentParser:
    """根据字段的模式解析命令行行为

    Args:
        key (str): 字段名
        schema (Dict[str, Any]): 字段的模式
        parser (argparse.ArgumentParser): 添加命令行解析的解析器

    Returns:
        argparse.ArgumentParser: 命令行的解析器
    """
    _type = schema.get("type")
    if not _type:
        return parser
    if not noflag:
        key = key.replace("_", "-")
    if _type == "number":
        return _argparse_number_handdler(key, schema, parser, required=required, noflag=noflag)
    elif _type == "string":
        return _argparse_string_handdler(key, schema, parser, required=required, noflag=noflag)
    elif _type == "integer":
        return _argparse_integer_handdler(key, schema, parser, required=required, noflag=noflag)
    elif _type == "boolean":
        return _argparse_boolean_handdler(key, schema, parser)
    elif _type == "array":
        return _argparse_array_handdler(key, schema, parser, noflag=noflag)
    else:
        print(f"未支持的类型{_type}")
        return parser
