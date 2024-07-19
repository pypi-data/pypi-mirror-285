def 数据类型转换_到字符串(输入值):
    """
    将任何输入值转换为字符串。

    参数:
    输入值: 任何类型
        需要转换为字符串的值。

    返回:
    str
        输入值转换后的字符串。如果转换失败，则返回错误信息。
    """
    try:
        return str(输入值)
    except Exception as e:
        return e