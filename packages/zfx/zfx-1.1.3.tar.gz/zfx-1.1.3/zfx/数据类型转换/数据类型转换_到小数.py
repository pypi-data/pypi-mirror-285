def 数据类型转换_到小数(输入值):
    """
    将输入值转换为小数（浮点数）。

    参数:
    输入值: 任何类型
        需要转换为小数的值。

    返回:
    float
        输入值转换后的小数。如果转换失败，则返回错误信息。
    """
    try:
        return float(输入值)
    except Exception as e:
        return e