def 谷歌填表_取当前页面网址(驱动器对象):
    """
    获取当前页面的URL。

    参数:
        驱动器对象: 已经初始化的Selenium Chrome驱动对象。

    返回:
        str: 当前页面的URL，获取失败则返回None。
    """
    try:
        return 驱动器对象.current_url
    except Exception:
        return None