import json


def json_遍历所有层级获取路径(数据对象, 键名):
    """
    使用说明：
        1、遍历所有层级下指定键的值，逐层进行寻找，并返回键的值及其层级路径。

    参数:
        数据对象 (dict 或 str): Python 字典对象或 json 字符串。
        键名 (str): 要查找的键名。

    返回:
        list: 包含所有匹配键值及其 JSON 路径的列表，如果没有匹配或异常则返回空列表。

    使用示例：
        匹配结果 = json_遍历所有层级获取路径(响应文本, 键名)
        for 路径, 值 in 匹配结果:
            print(f"路径: {路径}, 值: {值}")
    """
    try:
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        结果 = []

        def 遍历(obj, 当前路径):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    新路径 = 当前路径 + f'["{k}"]'
                    if k == 键名:
                        结果.append((当前路径, v))
                    if isinstance(v, (dict, list)):
                        遍历(v, 新路径)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    新路径 = 当前路径 + f'[{idx}]'
                    遍历(item, 新路径)

        遍历(数据对象, '数据对象')
        return 结果
    except Exception as e:
        return []