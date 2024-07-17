import jsonpath
import json


def json_遍历所有层级指定键(数据对象, 键名):
    """
    使用说明：
    1、遍历所有层级下指定键的值，逐层进行寻找。

    参数:
    数据对象 (dict 或 str): Python 字典对象或 json 字符串。
    键名 (str): 要查找的键名。

    返回:
    list: 包含所有匹配键值的列表，如果没有匹配或异常则返回空列表。
    """
    try:
        # 如果传入的是 json 字符串，则解析为 Python 字典
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        # 构建 JSONPath 表达式
        expr = f'$..{键名}'

        # 执行 JSONPath 查询
        匹配的值 = jsonpath.jsonpath(数据对象, expr)

        return 匹配的值 if 匹配的值 else []
    except Exception:
        return []