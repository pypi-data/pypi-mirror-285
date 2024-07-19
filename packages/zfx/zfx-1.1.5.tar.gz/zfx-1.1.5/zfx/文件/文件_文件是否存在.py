import os


def 文件_文件是否存在(文件完整路径):
    """
    检查文件是否存在，并捕获可能的异常。

    参数:
    file_path (str): 要检查的文件路径。

    返回:
    bool: 如果文件存在返回True，否则返回False。
    """
    try:
        return os.path.exists(文件完整路径)
    except Exception:
        return False