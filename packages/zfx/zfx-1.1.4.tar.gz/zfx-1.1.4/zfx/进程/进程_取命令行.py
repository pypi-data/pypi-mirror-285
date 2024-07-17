import psutil


def 进程_取命令行(pid):
    """
    根据进程ID获取进程的命令行参数。

    参数:
        - pid (int): 要查询的进程ID。

    返回值:
        - list: 成功返回包含命令行参数的列表，失败返回空列表。

    使用示例:
    命令行参数 = 进程_取命令行(1234)
    """
    try:
        process = psutil.Process(pid)
        return process.cmdline()
    except Exception:
        return []