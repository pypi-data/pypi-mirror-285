import json
from jsonpath_ng import parse


def json_遍历_键_取值(数据对象, 目标键):
    """
    查找 JSON 对象中所有指定键的值。

    参数:
        数据对象 (dict 或 str): Python 字典对象或 JSON 字符串。
        目标键 (str): 要查找的键。

    返回:
        list: 包含所有匹配键的值的列表，如果没有匹配或异常则返回空列表。
    """
    try:
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        # 使用 JSONPath 表达式查找所有目标键
        jsonpath_expr = parse(f'$..{目标键}')
        结果 = [match.value for match in jsonpath_expr.find(数据对象)]

        return 结果
    except Exception as e:
        return []