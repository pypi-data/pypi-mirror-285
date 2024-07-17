def 邮件IMAP_登录邮箱(连接对象, 用户名, 密码):
    """
    登录到IMAP邮箱账户。

    参数:
        邮箱 (IMAP4_SSL): IMAP4_SSL连接对象。
        用户名 (str): 邮箱用户名。
        密码 (str): 邮箱密码。

    返回:
        bool: 登录成功返回True，否则返回False。
    """
    try:
        连接对象.login(用户名, 密码)
        return True
    except Exception:
        return False