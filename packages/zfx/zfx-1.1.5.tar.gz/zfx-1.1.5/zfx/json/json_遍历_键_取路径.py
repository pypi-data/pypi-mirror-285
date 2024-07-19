import json


def json_遍历_键_取路径(数据对象, 目标键):
    """
    查找 JSON 对象中所有指定键的路径。

    参数:
        - 数据对象 (dict 或 str): Python 字典对象或 JSON 字符串。
        - 目标键 (str): 要查找的键。

    返回:
        - list: 包含所有匹配键的路径的列表，如果没有匹配或异常则返回空列表。
    """
    try:
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        结果 = []

        def 遍历(obj, 当前路径):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    新路径 = 当前路径 + f'["{k}"]'
                    if k == 目标键:
                        结果.append(新路径)
                    if isinstance(v, (dict, list)):
                        遍历(v, 新路径)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    新路径 = 当前路径 + f'[{idx}]'
                    if isinstance(item, (dict, list)):
                        遍历(item, 新路径)

        遍历(数据对象, '数据对象')
        return 结果
    except Exception as e:
        return []