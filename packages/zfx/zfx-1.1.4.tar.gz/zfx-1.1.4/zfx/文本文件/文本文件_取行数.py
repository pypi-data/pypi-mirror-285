def 文本文件_取行数(文件路径):
    """
    计算指定文本文件的行数。

    参数:
        文件路径 (str): 要计算行数的文本文件路径。

    返回:
        int: 文本文件内的行数。失败返回 -1。

    示例:
        行数 = 文本文件_取行数('示例.txt')
        if 行数 != -1:
            print(f"文件行数: {行数}")
        else:
            print("获取文件行数失败")
    """
    try:
        with open(文件路径, 'r', encoding='utf-8') as file:
            行数 = sum(1 for _ in file)
        return 行数
    except Exception:
        return -1