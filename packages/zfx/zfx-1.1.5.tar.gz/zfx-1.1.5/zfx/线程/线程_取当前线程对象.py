import threading


def 线程_取当前线程对象():
    """
    获取当前线程对象

    返回值:
    - 线程对象: threading.Thread 对象，表示当前线程，如果获取失败则返回 False
    """
    try:
        return threading.current_thread()
    except Exception:
        return False