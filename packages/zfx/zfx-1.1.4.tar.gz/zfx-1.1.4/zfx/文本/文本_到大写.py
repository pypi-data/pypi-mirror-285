def 文本_到大写(要转换的文本):
    """
    将文本转换为大写。

    参数:
        要转换的文本 (str): 要转换为大写的文本。

    返回:
        str: 转换为大写的文本。如果转换失败或出现任何异常，则返回 False。

    示例:
        文本 = "Hello world"
        结果 = 文本_到大写(文本)
        print(结果)  # 输出：HELLO WORLD
    """
    try:
        大写文本 = 要转换的文本.upper()
        return 大写文本
    except Exception:  # 捕获所有异常
        return False