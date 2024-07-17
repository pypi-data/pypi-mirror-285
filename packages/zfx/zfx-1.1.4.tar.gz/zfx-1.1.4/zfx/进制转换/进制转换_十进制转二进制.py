def 进制转换_十进制转二进制(十进制数):
    """
    将给定的十进制数转换为二进制表示形式。

    参数:
    十进制数 (int): 要转换的十进制数

    返回:
    str: 十进制数的二进制表示形式，不包括前缀 '0b'；如果转换失败或输入不符合要求，则返回 None
    """
    try:
        return bin(十进制数).replace("0b", "")
    except Exception:
        return None