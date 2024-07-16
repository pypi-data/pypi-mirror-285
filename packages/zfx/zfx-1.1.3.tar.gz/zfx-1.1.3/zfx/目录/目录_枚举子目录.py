import os


def 目录_枚举子目录(目录路径):
    """
    枚举指定目录下的所有子目录，并将它们存储在一个列表中返回。

    参数:
        - 目录路径 (str): 要枚举子目录的目录路径。

    返回:
        - list: 包含所有子目录的列表。如果获取失败或异常则返回 None。

    示例:
        子目录列表 = 目录_枚举子目录('/path/to/directory')
        if 子目录列表 is not None:
            print("子目录列表:", 子目录列表)
        else:
            print("获取子目录失败")
    """
    try:
        # 检查目录路径是否存在且是一个目录
        if not os.path.isdir(目录路径):
            return None

        # 枚举子目录
        子目录列表 = [os.path.join(目录路径, 名称) for 名称 in os.listdir(目录路径)
                      if os.path.isdir(os.path.join(目录路径, 名称))]
        return 子目录列表
    except Exception:
        return None
