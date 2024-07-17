def 邮件POP3_获取邮箱占用空间(服务器对象):
    """
    获取邮箱的占用空间。

    参数:
        - 服务器对象 (poplib.POP3): 已经连接的POP3服务器对象。

    返回值:
        - int: 邮箱占用空间（以字节为单位）。如果出现异常，返回假(False)。
    """
    try:
        # 获取邮箱的占用空间
        _, total_size = 服务器对象.stat()
        return total_size
    except Exception:
        return False