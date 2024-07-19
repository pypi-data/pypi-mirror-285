def 文本文件_取指定行内容_取出现次数(文件路径, 行号, 子字符串):
    """
    获取指定文本文件中特定行的内容，并返回子字符串在该行内容中出现的次数。

    注意：文本编码格式需要为UTF-8

    参数:
        - 文件路径 (str): 要读取的文本文件的路径。
        - 行号 (int): 要获取内容的行号（从1开始）。
        - 子字符串 (str): 要统计出现次数的子字符串。

    返回:
        - int: 子字符串在指定行内容中出现的次数。失败返回 None。

    示例:
        出现次数 = 文本文件_取指定行内容_取出现次数('示例.txt', 3, 'aaa')
        if 出现次数 is not None:
            print("出现次数:", 出现次数)
        else:
            print("获取出现次数失败")
    """
    try:
        with open(文件路径, 'r', encoding='utf-8') as file:
            行内容 = file.readlines()

        if 行号 < 1 or 行号 > len(行内容):
            return None

        # 获取指定行并去除行尾的换行符
        指定行内容 = 行内容[行号 - 1].rstrip('\n')

        # 获取子字符串出现的次数
        出现次数 = 指定行内容.count(子字符串)

        return 出现次数
    except Exception:
        return None