def 谷歌填表_获取页面源代码(驱动器对象):
    """
    获取当前页面的源代码。

    参数:
        - 驱动器对象: WebDriver 对象。

    返回:
        - 当前页面的源代码，如果失败则返回 None。
    """
    try:
        return 驱动器对象.page_source
    except Exception:
        return None