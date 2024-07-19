import requests


def 网页协议_发送_POST请求(网址, 数据, 异常返回=False):
    """
    发送 POST 请求并返回服务器响应文本或异常信息。

    参数:
        - 网址 (str): 请求的 URL。
        - 数据 (dict): 要发送的数据，字典形式。
        - 异常返回 (bool, optional): 如果为 True，出现异常时返回异常信息；如果为 False，出现异常时返回 None。默认值为 False。

    返回:
        - str: 服务器响应文本。如果请求失败且异常返回为 True，则返回异常信息；否则返回 None。
    """
    try:
        响应 = requests.post(网址, data=数据)
        响应.raise_for_status()  # 检查请求是否成功
        return 响应.text
    except Exception as e:
        if 异常返回:
            return str(f"处理失败: {e}")
        return None