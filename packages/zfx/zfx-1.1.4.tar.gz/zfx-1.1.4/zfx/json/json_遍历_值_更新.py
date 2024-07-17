import json


def json_遍历_值_更新(数据对象, 目标值, 新值):
    """
    更新 JSON 对象中所有指定的值。

    参数:
        - 数据对象 (dict 或 str): Python 字典对象或 JSON 字符串。
        - 目标值 (any): 要更新的目标值。
        - 新值 (any): 用于替换目标值的新值。

    返回:
        - dict: 更新后的 JSON 数据对象。
    """
    try:
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        def 遍历(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if v == 目标值:
                        obj[k] = 新值  # 更新值
                    elif isinstance(v, (dict, list)):
                        遍历(v)
            elif isinstance(obj, list):
                for index, item in enumerate(obj):
                    if item == 目标值:
                        obj[index] = 新值  # 更新值
                    elif isinstance(item, (dict, list)):
                        遍历(item)

        遍历(数据对象)
        return 数据对象
    except Exception as e:
        return {}
