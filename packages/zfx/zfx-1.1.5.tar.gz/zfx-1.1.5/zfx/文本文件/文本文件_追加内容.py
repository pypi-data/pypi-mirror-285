def 文本文件_追加内容(文件名, 内容):
    """
    向文本文件末尾追加内容。

    参数:
        - 文件名 (str): 要追加内容的文本文件名。
        - 内容 (str): 要追加的内容。

    返回:
        - 成功时返回 True，失败时返回 False。

    示例:
        追加成功 = 文本文件_追加内容('example.txt', '追加的内容\n')
        if 追加成功:
            print("内容追加成功")
        else:
            print("内容追加失败")
    """
    try:
        with open(文件名, 'a', encoding='utf-8') as 文件:
            文件.write(内容)
        return True
    except Exception:
        return False
