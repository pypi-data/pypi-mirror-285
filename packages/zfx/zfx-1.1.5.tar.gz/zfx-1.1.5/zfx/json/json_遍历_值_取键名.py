import json


def json_遍历_值_取键名(数据对象, 目标值):
    """
    查找 JSON 对象中指定值的所有键。

    参数:
        数据对象 (dict 或 str): Python 字典对象或 JSON 字符串。
        目标值 (any): 要查找的值。

    返回:
        list: 包含所有匹配值的键的列表，如果没有匹配或异常则返回空列表。

    使用示例：
        匹配结果 = zfx.json_值_取键名(JSON文本, 目标值)
        zfx.打印_依次打印列表(匹配结果)
    """
    try:
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        结果 = []

        def 遍历(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if v == 目标值:
                        结果.append(k)  # 记录匹配值的键
                    if isinstance(v, (dict, list)):
                        遍历(v)
            elif isinstance(obj, list):
                for item in obj:  # 修正此处
                    if isinstance(item, (dict, list)):
                        遍历(item)

        遍历(数据对象)
        return 结果
    except Exception as e:
        return []