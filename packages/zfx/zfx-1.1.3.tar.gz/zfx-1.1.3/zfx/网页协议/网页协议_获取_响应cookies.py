def 网页协议_获取_响应cookies(响应对象):
    """
    获取响应的 cookies。

    参数:
        - 响应对象 (requests.Response): 服务器响应对象。

    返回:
        - 响应的 cookies 对象。如果响应为 None 或出现任何异常则返回空的 字典。
    """
    try:
        if 响应对象 is not None:
            return 响应对象.cookies
        else:
            return {}
    except Exception:
        return {}