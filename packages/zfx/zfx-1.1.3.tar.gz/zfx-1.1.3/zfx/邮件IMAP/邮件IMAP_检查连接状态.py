def 邮件IMAP_检查连接状态(连接对象):
    """
    检查与IMAP服务器的连接状态。

    参数:
        连接对象 (IMAP4_SSL): IMAP4_SSL连接对象。

    返回:
        bool: 连接状态，True为连接正常，False为断开。

    示例:
        if 邮件IMAP_检查连接状态(邮箱):
            print("连接正常")
        else:
            print("连接已断开")
    """
    try:
        状态, _ = 连接对象.noop()
        return 状态 == 'OK'
    except Exception:
        return False
