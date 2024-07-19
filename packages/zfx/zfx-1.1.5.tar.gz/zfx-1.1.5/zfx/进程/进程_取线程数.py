import psutil


def 进程_取线程数(pid):
    """
    根据进程ID获取进程的线程数。

    参数:
        - pid (int): 要查询的进程ID。

    返回值:
        - int: 成功返回线程数，失败返回0。

    使用示例:
    线程数 = 进程_取线程数(1234)
    """
    try:
        process = psutil.Process(pid)
        return process.num_threads()
    except Exception:
        return 0