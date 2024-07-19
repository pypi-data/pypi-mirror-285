import pyotp
import time


def totp_生成验证码(密钥):
    """
    生成当前时间的 TOTP 验证码，并估算剩余有效时间。

    参数:
    - 密钥: str, 用于生成 TOTP 验证码的密钥

    返回值:
    - 如果成功生成 TOTP 验证码和估算剩余有效时间，则返回元组 (验证码, 剩余有效时间)；
      如果生成失败，则返回 (None, None)
    """
    try:
        # 移除空格并确保是大写
        密钥 = 密钥.replace(' ', '').upper()

        # 创建一个TOTP对象
        totp = pyotp.TOTP(密钥)

        # 生成当前的TOTP验证码和剩余有效时间
        验证码 = totp.now()
        剩余有效时间 = totp.interval - (int(time.time()) % totp.interval)
        return 验证码, 剩余有效时间
    except Exception:
        return None, None