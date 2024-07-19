def 文本文件_删除指定行(文件路径, 行号):
    """
    删除指定行的内容。

    参数:
        - 文件路径 (str): 要操作的文件路径。
        - 行号 (int): 要删除的行号。

    返回:
        - bool: 如果删除成功，返回 True；否则返回 False。
    """
    try:
        with open(文件路径, 'r+', encoding='utf-8') as file:
            行列表 = file.readlines()
            if 0 < 行号 <= len(行列表):
                行列表.pop(行号 - 1)
                file.seek(0)
                file.writelines(行列表)
                file.truncate()
                return True
            return False
    except Exception:
        return False