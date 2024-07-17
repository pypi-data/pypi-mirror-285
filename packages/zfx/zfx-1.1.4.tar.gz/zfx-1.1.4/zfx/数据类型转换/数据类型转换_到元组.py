def 数据类型转换_到元组(输入值):
    """
    将输入值转换为元组。

    参数:
    输入值: 任何类型
        需要转换为元组的值。

    返回:
    tuple
        输入值转换后的元组。如果转换失败，则返回错误信息。
    """
    try:
        return tuple(输入值)
    except TypeError:
        # 如果输入值无法直接转换为元组，尝试将其包装在一个元组中
        return (输入值,)
    except Exception as e:
        return e