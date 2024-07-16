def 网页协议_响应对象_取行数(响应对象):
    """
    获取响应的文本内容，并统计文本的行数。

    参数:
        - 响应对象: 服务器响应对象。

    返回:
        - int: 文本的行数。如果响应为 None 或出现任何异常，则返回 0。
    """
    try:
        if 响应对象 is not None:
            文本内容 = 响应对象.text
            行数 = len(文本内容.splitlines())
            return 行数
        else:
            return 0
    except Exception:
        return 0