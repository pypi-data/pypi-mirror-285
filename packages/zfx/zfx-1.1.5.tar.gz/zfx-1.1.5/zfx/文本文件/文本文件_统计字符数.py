def 文本文件_统计字符数(文件路径):
    """
    统计文件中的字符数。

    参数:
        - 文件路径 (str): 要统计的文件路径。

    返回:
        - 字符数 (int)。失败则返回 None
    """
    try:
        with open(文件路径, 'r', encoding='utf-8') as file:
            内容 = file.read()
            return len(内容)
    except Exception:
        return None