import subprocess


def 模块_外部库安装(模块名称):
    """
    安装指定名称的 Python 模块。

    参数:
        - 模块名称 (str): 要安装的模块名称。

    返回:
        - bool: 如果安装成功，则返回 True，否则返回 False。

    示例:
        安装成功 = zfx.模块_外部库安装("requests")
        if 安装成功:
            print("requests包已成功安装")
        else:
            print("requests包安装失败")
    """
    try:
        # 使用subprocess模块执行安装命令
        subprocess.run(["pip", "install", 模块名称], check=True)
        return True
    except Exception:
        return False  # 捕获其他所有异常并返回 False