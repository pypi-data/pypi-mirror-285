def 文本文件_取指定行内容_取长度(文件路径, 行号):
    """
    获取指定文本文件中特定行的内容，并返回该行内容的长度。

    注意：文本编码格式需要为UTF-8

    参数:
        - 文件路径 (str): 要读取的文本文件的路径。
        - 行号 (int): 要获取内容的行号（从1开始）。

    返回:
        - int: 指定行内容的长度。失败返回 None。

    示例:
        行内容长度 = 文本文件_取指定行内容_取长度('示例.txt', 3)
        if 行内容长度 is not None:
            print("行内容长度:", 行内容长度)
        else:
            print("获取行内容长度失败")
    """
    try:
        with open(文件路径, 'r', encoding='utf-8') as file:
            行内容 = file.readlines()

        if 行号 < 1 or 行号 > len(行内容):
            return None

        # 获取指定行并去除行尾的换行符
        指定行内容 = 行内容[行号 - 1].rstrip('\n')

        # 获取行内容的长度
        行内容长度 = len(指定行内容)

        return 行内容长度
    except Exception:
        return None