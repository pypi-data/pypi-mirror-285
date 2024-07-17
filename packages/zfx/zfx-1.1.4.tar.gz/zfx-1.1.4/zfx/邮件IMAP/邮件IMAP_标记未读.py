def 邮件IMAP_标记未读(连接对象, 邮件ID):
    """
    标记邮件为未读。

    参数:
        连接对象 (IMAP4_SSL): IMAP4_SSL连接对象。
        邮件ID (bytes): 要标记为未读的邮件ID。

    返回:
        str: 操作状态。

    示例:
        状态 = 邮件IMAP_标记未读(邮箱, b'1')
        if 状态 == "OK":
            print("邮件已标记为未读")
        else:
            print("标记邮件为未读失败")
    """
    try:
        状态, _ = 连接对象.store(邮件ID, '-FLAGS', '\\Seen')
        return 状态
    except Exception:
        return "FAIL"
