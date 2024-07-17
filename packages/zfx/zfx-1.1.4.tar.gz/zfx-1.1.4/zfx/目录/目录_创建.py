import os


def 目录_创建(目录路径):
    """
    创建目录的函数。

    参数:
        目录路径 (str): 要创建的目录路径。

    返回:
        bool: 创建成功返回 True，创建失败返回 False。

    使用示例:
        result = 目录_创建("C:/哈哈/哈哈哈")
        print(result)
    """
    try:
        os.makedirs(目录路径, exist_ok=True)
        return True
    except Exception:
        return False