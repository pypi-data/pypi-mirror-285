import requests


def 网页协议_发送_GET请求(网址, 参数=None, 异常返回=False):
    """
    发送 GET 请求并返回服务器响应对象或异常信息。

    参数:
        - 网址 (str): 请求的 URL。
        - 参数 (dict, optional): 要发送的参数，字典形式，默认为 None。
        - 异常返回 (bool, optional): 如果为 True，出现异常时返回异常信息；如果为 False，出现异常时返回 None。默认值为 False。

    返回:
        - 响应对象或 str: 服务器响应对象。如果请求失败且异常返回为 True，则返回异常信息；否则返回 None。
    """
    try:
        响应 = requests.get(网址, params=参数)
        响应.raise_for_status()  # 检查响应状态，如果不是 200 则引发 HTTPError
        return 响应
    except Exception as e:
        if 异常返回:
            return str(f"处理失败: {e}")
        return None
