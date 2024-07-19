import json


def json_遍历_键_重命名(数据对象, 旧键, 新键):
    """
    重命名 JSON 对象中所有指定的键。

    参数:
        - 数据对象 (dict 或 str): Python 字典对象或 JSON 字符串。
        - 旧键 (str): 要重命名的旧键。
        - 新键 (str): 新的键名。

    返回:
        - dict: 重命名后的 JSON 数据对象。
    """
    try:
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        def 遍历(obj):
            if isinstance(obj, dict):
                if 旧键 in obj:
                    obj[新键] = obj.pop(旧键)
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