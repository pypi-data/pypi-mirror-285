def 网页协议_获取_响应URL(响应对象):
    """
    获取响应的 URL。

    参数:
        - 响应对象 (requests.Response): 服务器响应对象。

    返回:
        - str: 响应的 URL。如果响应为 None 或出现任何异常则返回空字符串。
    """
    try:
        if 响应对象 is not None:
            return 响应对象.url
        else:
            return ''
    except Exception:
        return ''