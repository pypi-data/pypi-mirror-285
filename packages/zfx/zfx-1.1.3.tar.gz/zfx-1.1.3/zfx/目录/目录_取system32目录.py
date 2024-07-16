import os


def 目录_取system32目录(加尾斜杠=False):
    """
    获取系统中 System32 目录的路径。

    参数:
        - 添加反斜杠: bool, 是否在返回的路径末尾添加反斜杠，默认为 False。

    返回:
        str: System32 目录的路径，如果操作失败则返回 False。
    """
    try:
        # 使用 os.environ 获取环境变量中的 SystemRoot
        system_root = os.environ.get('SystemRoot', 'C:\\Windows')
        # 构造 System32 目录的完整路径
        system32_path = os.path.join(system_root, 'System32')

        # 检查路径是否存在，并且确保是一个目录
        if os.path.exists(system32_path) and os.path.isdir(system32_path):
            if 加尾斜杠:
                return system32_path + '\\'
            else:
                return system32_path
        else:
            return False
    except Exception:
        return False