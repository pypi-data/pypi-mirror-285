def 谷歌填表_判断可见(元素对象):
    """
    判断给定元素是否可见。

    参数:
        - 元素对象: 要进行可见性检查的元素对象。

    返回:
        - bool: 如果元素可见，则返回 True；否则返回 False。
    """
    try:
        return 元素对象.is_displayed()
    except Exception:
        return False