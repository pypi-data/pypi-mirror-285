def 文本文件_取指定行内容(文件路径, 行号):
    """
    获取指定文本文件中特定行的内容。
    注意：文本编码格式需要为UTF-8

    参数:
        - 文件路径 (str): 要读取的文本文件的路径。
        - 行号 (int): 要获取内容的行号（从1开始）。

    返回:
        - str: 指定行的内容。失败返回 None。

    示例:
        行内容 = 文本文件_取指定行内容('示例.txt', 3)
        if 行内容 is not None:
            print("行内容:", 行内容)
        else:
            print("获取行内容失败")
    """
    try:
        with open(文件路径, 'r', encoding='utf-8') as file:
            行内容 = file.readlines()

        if 行号 < 1 or 行号 > len(行内容):
            return None

        return 行内容[行号 - 1].rstrip('\n')
    except Exception:
        return None