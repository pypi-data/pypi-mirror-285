import os


def 目录_取运行目录(加尾斜杠=False):
    """
    获取当前运行目录的函数。

    参数:
        - 加尾斜杠 (bool): 如果为 True，则在目录路径末尾添加一个反斜杠。默认为 False。

    返回:
        - str: 当前运行目录的路径，如果获取失败则返回 None。

    使用示例:
        运行目录 = 目录_取运行目录()
        print(运行目录)

        运行目录_加斜杠 = 目录_取运行目录(True)
        print(运行目录_加斜杠)
    """
    try:
        运行目录 = os.getcwd()  # 尝试获取当前运行目录
        return 运行目录 + '\\' if 加尾斜杠 else 运行目录
    except Exception:
        return None
