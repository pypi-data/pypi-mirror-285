def 邮件IMAP_登出邮箱(连接对象):
    """
    登出IMAP邮箱。

    参数:
        邮箱 (IMAP4_SSL): IMAP4_SSL连接对象。

    返回:
        bool: 登出成功返回True，否则返回False。
    """
    try:
        连接对象.logout()
        return True
    except Exception:
        return False