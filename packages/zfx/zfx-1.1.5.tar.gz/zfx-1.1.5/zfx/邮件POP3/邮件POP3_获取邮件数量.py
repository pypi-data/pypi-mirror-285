def 邮件POP3_获取邮件数量(服务器对象):
    """
    获取邮箱中的邮件数量。

    参数:
        - 邮件服务器 (poplib.POP3): 已经连接的POP3服务器对象。

    返回值:
        - int: 邮件数量。如果出现异常，返回假(False)。
    """
    try:
        # 获取邮箱中的邮件数量
        num_messages, _ = 服务器对象.stat()
        return num_messages
    except Exception:
        return False