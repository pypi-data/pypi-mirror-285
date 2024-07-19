import threading


def 线程_取当前线程名称():
    """
    获取当前线程的名称

    返回值:
    - 当前线程的名称 (str)，如果获取失败则返回 False
    """
    try:
        当前线程 = threading.current_thread()
        return 当前线程.name
    except Exception:
        return False