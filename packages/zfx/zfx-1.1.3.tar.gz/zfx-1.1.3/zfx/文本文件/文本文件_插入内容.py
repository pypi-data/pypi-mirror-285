def 文本文件_插入内容(文件路径, 行号, 内容):
    """
    在指定行前插入内容。

    参数:
        - 文件路径 (str): 要操作的文件路径。
        - 行号 (int): 插入内容的位置（行号）。
        - 内容 (str): 要插入的内容。

    返回:
        - bool: 如果插入成功，返回 True；否则返回 False。
    """
    try:
        with open(文件路径, 'r+', encoding='utf-8') as file:
            行列表 = file.readlines()
            行列表.insert(行号 - 1, 内容 + '\n')
            file.seek(0)
            file.writelines(行列表)
        return True
    except Exception:
        return False
