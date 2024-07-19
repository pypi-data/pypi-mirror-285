def 谷歌填表_后退(驱动器对象):
    """
    使用提供的驱动程序执行后退操作。

    参数:
        - 驱动器对象: WebDriver 对象，用于控制浏览器的行为。

    返回:
        - bool: 后退操作成功返回 True，失败返回 False。
    """
    try:
        驱动器对象.back()
        return True
    except Exception:
        return False