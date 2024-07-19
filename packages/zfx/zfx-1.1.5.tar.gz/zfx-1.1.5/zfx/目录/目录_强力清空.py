import os
import shutil


def 目录_强力清空(目录路径):
    """
    强力清空指定目录下的所有文件和文件夹。

    参数:
        - 目录路径 (str): 要清空的目录路径。

    返回:
        - bool: 如果清空成功则返回 True，否则返回 False。

    示例:
        成功 = 目录_强力清空('/path/to/directory')
        if 成功:
            print("目录清空成功")
        else:
            print("目录清空失败")
    """
    try:
        if not os.path.isdir(目录路径):
            return False

        # 删除目录下的所有文件和文件夹
        for 文件名 in os.listdir(目录路径):
            文件路径 = os.path.join(目录路径, 文件名)
            if os.path.isfile(文件路径) or os.path.islink(文件路径):
                os.unlink(文件路径)
            elif os.path.isdir(文件路径):
                shutil.rmtree(文件路径)
        return True
    except Exception:
        return False