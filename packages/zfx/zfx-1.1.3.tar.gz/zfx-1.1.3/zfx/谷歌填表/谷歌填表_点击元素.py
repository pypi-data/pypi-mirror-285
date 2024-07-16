def 谷歌填表_点击元素(元素对象):
    """
    点击指定的网页元素。

    参数:
        - 元素对象: 要点击的 WebElement 对象。

    返回:
        - bool: 如果点击成功，则返回 True，否则返回 False。
    """
    try:
        元素对象.click()
        return True
    except Exception:
        return False