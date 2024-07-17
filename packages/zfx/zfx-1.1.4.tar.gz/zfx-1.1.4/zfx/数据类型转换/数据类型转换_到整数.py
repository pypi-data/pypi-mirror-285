def 数据类型转换_到整数(输入值):
    """
    将输入值转换为整数。

    参数:
    输入值: 任何类型
        需要转换为整数的值。

    返回:
    int
        输入值转换后的整数。如果转换失败，则返回错误信息。
    """
    try:
        return int(输入值)
    except Exception as e:
        return e