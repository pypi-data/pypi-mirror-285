def 网页协议_获取_响应头(响应对象):
    """
    获取响应头的字典形式。

    参数:
        - 响应对象 (requests.Response): 服务器响应对象。

    返回:
        - dict: 响应头的字典形式。如果响应为 None 或出现任何异常则返回空字典。
    """
    try:
        if 响应对象 is not None:
            return 响应对象.headers
        else:
            return {}
    except Exception:
        return {}