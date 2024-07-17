def 文本_到小写(要转换的文本):
    """
    将文本转换为小写。

    参数:
        要转换的文本 (str): 要转换为小写的文本。

    返回:
        str: 转换为小写的文本。如果转换失败或出现任何异常，则返回 False。

    示例:
        文本 = "Hello World"
        结果 = 文本_到小写(文本)
        print(结果)  # 输出：hello world
    """
    try:
        小写文本 = 要转换的文本.lower()
        return 小写文本
    except Exception:  # 捕获所有异常
        return False