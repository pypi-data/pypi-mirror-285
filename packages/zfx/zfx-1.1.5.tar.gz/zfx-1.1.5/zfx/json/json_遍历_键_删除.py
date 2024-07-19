import json


def json_遍历_键_删除(数据对象, 目标键):
    """
    删除 JSON 对象中所有指定的键。

    参数:
        - 数据对象 (dict 或 str): Python 字典对象或 JSON 字符串。
        - 目标键 (str): 要删除的键。

    返回:
        - dict: 删除后的 JSON 数据对象。
    """
    try:
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        def 遍历(obj):
            if isinstance(obj, dict):
                if 目标键 in obj:
                    del obj[目标键]
                for v in obj.values():
                    if isinstance(v, (dict, list)):
                        遍历(v)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        遍历(item)

        遍历(数据对象)
        return 数据对象
    except Exception as e:
        return {}