import os


def 目录_取子目录数(父文件夹路径):
    """
    获取指定父文件夹路径下的子目录数量。

    参数:
        - str： 父文件夹路径: 文本型，父文件夹的路径

    返回:
        - int: 子目录的数量，如果操作失败则返回 -1
    """
    try:
        # 使用 os.listdir() 获取父文件夹下的所有文件和目录列表
        文件和目录列表 = os.listdir(父文件夹路径)
        # 过滤出子目录
        子目录列表 = [名称 for 名称 in 文件和目录列表 if os.path.isdir(os.path.join(父文件夹路径, 名称))]
        # 返回子目录的数量
        return len(子目录列表)
    except Exception:
        return -1