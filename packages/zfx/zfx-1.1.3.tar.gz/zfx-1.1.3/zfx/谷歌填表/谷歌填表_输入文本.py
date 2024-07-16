def 谷歌填表_输入文本(元素对象, 文本):
    """
    在指定的网页元素中输入文本。

    参数:
        - 元素对象: 要输入文本的元素对象。
        - 文本: 要输入的文本内容。

    返回:
        - bool: 输入文本成功返回 True，失败返回 False。
    """
    try:
        元素对象.send_keys(文本)
        return True
    except Exception:
        return False