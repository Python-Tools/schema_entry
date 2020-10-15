"""utils.

模块需要的工具.
"""
import warnings
from typing import List, Dict, Any


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


def parse_value_string_by_schema(schema: Dict[str, Any], value_str: str) -> Any:
    """根据schema的定义解析字符串的值.

    Args:
        schema (Dict[str, Any]): 描述字符串值的json schema字典.
        value_str (str): 待解析的字符串.

    Returns:
        List[str]: 父节点树

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
