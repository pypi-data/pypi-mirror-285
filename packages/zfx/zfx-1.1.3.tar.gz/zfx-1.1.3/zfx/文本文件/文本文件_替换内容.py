def 文本文件_替换内容(文件名, 目标内容, 替换内容):
    """
    替换文本文件中的指定内容为新内容，并保存修改后的文件。

    参数:
        - 文件名 (str): 要修改的文本文件名。
        - 目标内容 (str): 要被替换的内容。
        - 替换内容 (str): 替换后的新内容。

    返回:
        - 成功时返回 True，失败时返回 False。
    """
    try:
        with open(文件名, 'r', encoding='utf-8') as 文件:
            文本 = 文件.read()

        替换后文本 = 文本.replace(目标内容, 替换内容)

        with open(文件名, 'w', encoding='utf-8') as 文件:
            文件.write(替换后文本)

        return True
    except Exception:
        return False