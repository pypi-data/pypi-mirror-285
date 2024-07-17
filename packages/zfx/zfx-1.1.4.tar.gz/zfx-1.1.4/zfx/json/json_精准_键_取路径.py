import json
from jsonpath_ng import parse


def json_精准_键_取路径(数据对象, 父路径, 目标键):
    """
    在指定的父路径下查找 JSON 对象中指定键的路径。

    参数:
        - 数据对象 (dict 或 str): Python 字典对象或 JSON 字符串。
        - 父路径 (str): 要查找的父路径(部分或全部，不确定部分也可以用 * 代替)，例如 '*.address.[0].details'。
        - 目标键 (str): 要查找的键。

    返回:
        - list: 包含所有匹配键的路径的列表，如果没有匹配或异常则返回空列表。
    """
    try:
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        jsonpath_expr = parse(f'$.{父路径}..{目标键}')
        结果 = [match.full_path for match in jsonpath_expr.find(数据对象)]

        return [str(path) for path in 结果]
    except Exception as e:
        return []