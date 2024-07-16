def 谷歌填表_判断可用(元素对象):
    """
    判断给定元素是否可用。

    参数:
        - 元素对象: 要进行可用性检查的元素对象。

    返回:
        - bool: 如果元素可用，则返回 True；否则返回 False。
    """
    try:
        return 元素对象.is_enabled()
    except Exception:
        return False