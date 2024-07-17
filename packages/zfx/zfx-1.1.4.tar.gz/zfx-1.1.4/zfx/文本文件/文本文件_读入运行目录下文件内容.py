def 文本文件_读入运行目录下文件内容(文件名称):
    """
    读取运行目录下的指定文本文件内容，文本文件需要和运行的Py文件在同一目录，只需要传递文本文件的名称就行了，不需要传递完整路径。

    参数:
        - 文件名称 (str): 要读取的文本文件名称。

    返回:
        - 文件内容 (str): 成功时返回文件内容，失败时返回 None。

    示例:
        文件内容 = 文本文件_读入运行目录下文件('example.txt')
        if 文件内容 is not None:
            print("文件内容读取成功:")
            print(文件内容)
        else:
            print("文件内容读取失败")
    """
    try:
        with open(文件名称, 'r', encoding='utf-8') as 文件:
            内容 = 文件.read()
        return 内容
    except Exception:
        return None