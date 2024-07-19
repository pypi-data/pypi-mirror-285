import os


def 文件_枚举(目录路径):
    """
    枚举指定目录下的所有文件，并返回文件完整路径的列表。

    参数:
    目录路径 (str): 要枚举的目录路径。

    返回:
    list: 包含所有文件完整路径的列表。执行异常或失败则返回 False

    使用示例：
    - 文件列表 = 文件_枚举(r"C:\\Users\\example_directory")
    """
    文件列表 = []
    try:
        for 根目录, 目录名, 文件名 in os.walk(目录路径):
            for 文件 in 文件名:
                文件完整路径 = os.path.join(根目录, 文件)
                文件列表.append(文件完整路径)
        return 文件列表
    except Exception:
        return False