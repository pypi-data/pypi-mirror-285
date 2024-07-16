import jsonpath
import json


def json_遍历指定层级指定键(数据对象, 层级路径, 键名):
    """
    使用说明：
    1、遍历指定层级指定键，按照指定的目录下开始进行寻找

    2、层级名称不固定可用*号代替。

    3、层级路径一定要写完整，最终一定要定位到自己想要的键去。类似于：数据[第一层][第二层][第三层]

    使用示例：zfx.json_遍历指定层级指定键(result, "data.wickedProductNoCache.*.edges", "*.shortId")


    参数:
    数据对象 (dict 或 str): Python 字典对象或 json 字符串。
    层级路径 (str): 路径部分。
    键名 (str): 要查找的键名。

    返回:
    list: 包含所有匹配键值的列表，如果没有匹配或异常则返回空列表。

    使用示例：
    结果 = json_遍历指定层级指定键(数据对象, 'data.第一层.第二层', '价格')
    """
    try:
        # 如果传入的是 json 字符串，则解析为 Python 字典
        if isinstance(数据对象, str):
            数据对象 = json.loads(数据对象)

        # 构建 JSONPath 表达式
        表达式 = f'$.{层级路径}[*].{键名}'

        # 执行 JSONPath 查询
        匹配的值 = jsonpath.jsonpath(数据对象, 表达式)

        return 匹配的值 if 匹配的值 else []
    except Exception:
        return []