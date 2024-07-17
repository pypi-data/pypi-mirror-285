def 文本文件_读入全部内容(文件路径):
    """
    读取指定文件路径的文本文件内容。
    注意：文本编码格式需要为UTF-8

    参数:
        文件路径 (str): 要读取的文本文件的路径。

    返回:
        str: 文本文件的内容，失败将返回 None。

    示例:
        文件内容 = 文本文件_读入全部内容('示例.txt')
        if 文件内容 is not None:
            print("文件内容:", 文件内容)
        else:
            print("读取文件失败")
    """
    try:
        with open(文件路径, 'r', encoding='utf-8') as file:
            文件内容 = file.read()
        return 文件内容
    except Exception:
        return None
