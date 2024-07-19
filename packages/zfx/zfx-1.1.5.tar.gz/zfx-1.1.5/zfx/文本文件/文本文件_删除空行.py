def 文本文件_删除空行(文件路径):
    """
    删除指定文本文件中的空行(只支持UTF-8)。

    参数:
        文件路径 (str): 要处理的文本文件的路径。

    返回:
        bool: 删除成功返回 True，删除失败返回 False。
    """
    try:
        # 打开文件读取内容
        with open(文件路径, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 过滤掉空行
        non_empty_lines = [line for line in lines if line.strip()]

        # 将非空行写回文件
        with open(文件路径, 'w', encoding='utf-8') as file:
            file.writelines(non_empty_lines)

        return True
    except Exception:
        return False