import os


def 目录_取桌面目录(加尾斜杠=False):
    """
    获取当前用户的桌面目录路径。

    参数:
        - 加尾斜杠 (bool): 如果为 True，则在目录路径末尾添加一个反斜杠。默认为 False。

    返回:
        - str: 当前用户的桌面目录路径。如果获取失败或异常则返回 None。

    示例:
        桌面目录 = 目录_取桌面目录()
        if 桌面目录 is not None:
            print("桌面目录路径:", 桌面目录)
        else:
            print("获取桌面目录失败")

        桌面目录_加斜杠 = 目录_取桌面目录(True)
        if 桌面目录_加斜杠 is not None:
            print("桌面目录路径(加斜杠):", 桌面目录_加斜杠)
        else:
            print("获取桌面目录失败")
    """
    try:
        if os.name == 'nt':  # Windows
            桌面目录 = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        else:  # macOS 和 Linux
            桌面目录 = os.path.join(os.path.expanduser('~'), 'Desktop')

        if os.path.exists(桌面目录):
            return 桌面目录 + '\\' if 加尾斜杠 else 桌面目录
        else:
            return None
    except Exception:
        return None