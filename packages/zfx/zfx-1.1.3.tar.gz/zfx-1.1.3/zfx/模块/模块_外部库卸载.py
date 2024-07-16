import subprocess


def 模块_外部库卸载(模块名称):
    """
    卸载指定名称的 Python 模块。

    参数:
        - 模块名称 (str): 要卸载的模块名称。

    返回:
        - bool: 如果卸载成功，则返回 True，否则返回 False。

    示例:
        卸载成功 = zfx.模块_外部库卸载("requests")
        if 卸载成功:
            print("requests包已成功卸载")
        else:
            print("requests包卸载失败")
    """
    try:
        # 使用subprocess模块执行卸载命令
        subprocess.run(["pip", "uninstall", "-y", 模块名称], check=True)
        return True
    except Exception:
        return False  # 捕获其他所有异常并返回 False