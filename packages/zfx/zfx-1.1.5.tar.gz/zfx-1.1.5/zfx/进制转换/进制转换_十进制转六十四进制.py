def 进制转换_十进制转六十四进制(十进制数):
    """
    将十进制数转换为六十四进制字符串。

    参数:
        十进制数 (int): 要转换的十进制整数。

    返回:
        str: 转换后的六十四进制字符串，如果输入不是有效的十进制数则返回 None。

    示例使用:
        六十四进制字符串 = 进制转换_十进制转六十四进制(12345)
        print("转换后的六十四进制字符串:", 六十四进制字符串)
    """
    try:
        # 检查输入是否为非负整数
        if 十进制数 < 0 or not isinstance(十进制数, int):
            return None

        # 定义64进制的字符集
        字符集 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/'
        if 十进制数 == 0:
            return '0'
        六十四进制字符串 = ''
        while 十进制数 > 0:
            十进制数, 余数 = divmod(十进制数, 64)
            六十四进制字符串 = 字符集[余数] + 六十四进制字符串
        return 六十四进制字符串
    except Exception:
        return None