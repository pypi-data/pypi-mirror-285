import psutil


def 进程_取父ID(pid):
    """
    根据进程ID获取父进程ID。

    参数:
        - pid (int): 要查询的进程ID。

    返回值:
        - int: 成功返回父进程ID，失败返回0。

    使用示例:
    父进程ID = 进程_取父ID(1234)
    """
    try:
        process = psutil.Process(pid)
        return process.ppid()
    except Exception:
        return 0