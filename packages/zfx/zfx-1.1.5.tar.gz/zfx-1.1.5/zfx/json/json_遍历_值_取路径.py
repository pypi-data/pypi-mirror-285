import json
from jsonpath_ng import parse


def json_遍历_值_取路径(数据对象, 目标值):
    """
    查找 JSON 对象中指定值的所有路径。

    参数:
        - 数据对象 (dict 或 str): Python 字典对象或 JSON 字符串。
        - 目标值 (any): 要查找的值。（是数字就直接写数字，是字符串就提交字符串）

    返回:
        - list: 包含所有匹配值及其 JSON 路径的列表，如果没有匹配或异常则返回空列表。

    使用示例：
        匹配结果 = json_遍历_值_取路径(JSON文本, 目标值)
        打印_依次打印列表(匹配结果)
    """
    try:
        # 如果数据对象是 JSON 字符串，则将其解析为字典
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        # 创建 JSONPath 表达式，用于查找所有值
        jsonpath_expr = parse('$..*')

        # 查找所有值并记录匹配目标值的路径
        结果 = []
        for match in jsonpath_expr.find(数据对象):
            if match.value == 目标值:
                结果.append(str(match.full_path))

        return 结果
    except Exception as e:
        # 发生异常时返回空列表
        return []