def 文本文件_取指定行内容_取右边(文件路径, 行号, 分隔符):
    """
    获取指定文本文件中特定行的内容，并取分隔符右边的部分。

    注意：文本编码格式需要为UTF-8

    参数:
        - 文件路径 (str): 要读取的文本文件的路径。
        - 行号 (int): 要获取内容的行号（从1开始）。
        - 分隔符 (str): 用于分割行内容的分隔符。

    返回:
        - str: 分隔符右边的内容。失败返回 None。

    示例:
        行内容右边 = 文本文件_取指定行内容_取右边('示例.txt', 3, '----')
        if 行内容右边 is not None:
            print("行内容右边:", 行内容右边)
        else:
            print("获取行内容失败")
    """
    try:
        with open(文件路径, 'r', encoding='utf-8') as file:
            行内容 = file.readlines()

        if 行号 < 1 or 行号 > len(行内容):
            return None

        # 获取指定行并去除行尾的换行符
        指定行内容 = 行内容[行号 - 1].rstrip('\n')

        # 根据分隔符取分隔符右边的内容
        分隔符位置 = 指定行内容.find(分隔符)
        if 分隔符位置 == -1:
            return None

        右边内容 = 指定行内容[分隔符位置 + len(分隔符):]

        return 右边内容
    except Exception:
        return None