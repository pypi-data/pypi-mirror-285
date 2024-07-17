def 文本文件_修改指定行内容(文件路径, 行号, 新内容):
    """
    修改指定文本文件中特定行的内容。
    注意：文本编码格式需要为UTF-8

    参数:
        文件路径 (str): 要修改的文本文件的路径。
        行号 (int): 要修改的行号（从1开始）。
        新内容 (str): 要写入的新内容。

    返回:
        bool: 修改成功返回 True，修改失败返回 False。

    示例:
        成功 = 文本文件_修改指定行内容('示例.txt', 3, '这是新的内容')
        if 成功:
            print("行内容修改成功")
        else:
            print("行内容修改失败")
    """
    try:
        with open(文件路径, 'r', encoding='utf-8') as file:
            行内容 = file.readlines()

        if 行号 < 1 or 行号 > len(行内容):
            return False

        行内容[行号 - 1] = 新内容 + '\n'

        with open(文件路径, 'w', encoding='utf-8') as file:
            file.writelines(行内容)

        return True
    except Exception:
        return False