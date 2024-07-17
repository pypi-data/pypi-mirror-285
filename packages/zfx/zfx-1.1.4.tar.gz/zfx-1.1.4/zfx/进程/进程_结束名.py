import subprocess


def 进程_结束名(进程名):
    """
    尝试终止指定名称的所有进程。

    参数:
        - 进程名 (str): 要终止的进程名称，包括后缀（例如：chrome.exe）。

    返回值:
        - bool: 成功终止所有进程返回True，如果任何一个进程无法终止则返回False。

    说明:
    该函数会尝试终止指定名称的所有进程。如果发生异常，会返回False。
    """
    try:
        # 使用 tasklist 命令查找指定名称的进程
        result = subprocess.run(['tasklist', '/fi', f'imagename eq {进程名}'], capture_output=True, text=True)

        if 进程名.lower() not in result.stdout.lower():
            return False

        # 使用 taskkill 命令终止指定名称的进程
        kill_result = subprocess.run(['taskkill', '/f', '/im', 进程名], capture_output=True, text=True)

        if kill_result.returncode == 0:
            return True
        else:
            return False

    except Exception:
        return False
