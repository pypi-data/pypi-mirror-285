def 网页协议_获取_响应二进制内容(响应对象):
    """
    获取响应的二进制内容。

    参数:
        - 响应对象 (requests.Response): 服务器响应对象。

    返回:
        - bytes: 响应的二进制内容。如果响应为 None 或出现任何异常则返回空字节串。
    """
    try:
        if 响应对象 is not None:
            return 响应对象.content
        else:
            return b''
    except Exception:
        return b''