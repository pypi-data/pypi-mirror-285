import json
from jsonpath_ng import parse


def json_遍历_值_取出现次数(数据对象, 目标值):
    """
    统计 JSON 对象中指定值的出现次数。

    参数:
        - 数据对象 (dict 或 str): Python 字典对象或 JSON 字符串。
        - 目标值 (any): 要统计的值。

    返回:
        - int: 目标值在 JSON 对象中出现的次数。

    示例：
        出现次数 = json_遍历_值_取出现次数(json文本, 20.54)
        print(f"目标值出现的次数: {出现次数}")
    """
    try:
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        # 创建 JSONPath 表达式，用于查找所有值
        jsonpath_expr = parse('$..*')

        # 查找所有值并统计目标值的出现次数
        结果 = [match.value for match in jsonpath_expr.find(数据对象)]
        次数 = 结果.count(目标值)

        return 次数
    except Exception as e:
        return 0