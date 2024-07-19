def 谷歌填表_判断选中(元素对象):
    """
    判断给定元素是否选中。

    参数:
        - 元素对象: 要进行选中状态检查的元素对象。

    返回:
        - bool: 如果元素选中，则返回 True；否则返回 False。
    """
    try:
        return 元素对象.is_selected()
    except Exception:
        return False