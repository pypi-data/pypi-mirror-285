def 文本文件_写入文件内容(文件路径, 内容):
    """
    将指定内容写入指定文件路径的文本文件中，替换原本的内容。
    注意：文本编码格式需要为UTF-8

    参数:
        文件路径 (str): 要写入的文本文件的路径。
        内容 (str): 要写入文件的内容。

    返回:
        bool: 写入成功返回 True，写入失败返回 False。
    """
    try:
        with open(文件路径, 'w', encoding='utf-8') as file:
            file.write(str(内容))
        return True
    except Exception:
        return False