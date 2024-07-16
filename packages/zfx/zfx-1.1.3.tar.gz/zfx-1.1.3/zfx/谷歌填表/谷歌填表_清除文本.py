def 谷歌填表_清除文本(元素对象):
    """
    清除元素对象中的文本。

    参数:
        - 元素对象: 要清除文本的 WebElement 对象。

    返回:
        - bool: 清除文本成功返回 True，失败返回 False。
    """
    try:
        元素对象.clear()
        return True
    except Exception:
        return False