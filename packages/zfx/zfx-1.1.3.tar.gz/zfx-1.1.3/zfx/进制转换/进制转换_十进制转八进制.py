def 进制转换_十进制转八进制(十进制数):
    """
    将给定的十进制数转换为八进制表示形式。

    参数:
    十进制数 (int): 要转换的十进制数

    返回:
    str: 十进制数的八进制表示形式，不包括前缀 '0o'；如果转换失败或输入不符合要求，则返回 None
    """
    try:
        return oct(十进制数).replace("0o", "")
    except Exception:
        return None