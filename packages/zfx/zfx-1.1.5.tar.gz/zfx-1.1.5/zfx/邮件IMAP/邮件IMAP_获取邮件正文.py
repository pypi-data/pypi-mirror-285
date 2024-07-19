def 邮件IMAP_获取邮件正文(连接对象, 邮件ID):
    """
    从IMAP邮箱中获取指定邮件的正文。

    参数:
        连接对象 (IMAP4_SSL): IMAP4_SSL连接对象。
        邮件ID (bytes): 要获取的邮件的 ID。

    返回:
        tuple: 包含状态和正文信息的元组。如果获取失败，返回 (None, None)。

    示例:
        # 从邮箱中获取指定邮件的正文
        邮件ID = b'1'  # 假设邮件的 ID 是 '1'
        状态, 正文信息 = 邮件IMAP_获取邮件正文(邮箱, 邮件ID)

        if 状态 == "OK":
            print("邮件正文信息:", 正文信息)
        else:
            print("获取邮件正文信息失败")
    """
    try:
        # 获取邮件正文信息
        状态, 邮件数据 = 连接对象.fetch(邮件ID, "(BODY[TEXT])")
        if 状态 != "OK":
            print("获取邮件正文信息失败")
            return None, None

        for 响应部分 in 邮件数据:
            if isinstance(响应部分, tuple):
                正文信息 = 响应部分[1]
                return 状态, 正文信息

        return None, None
    except Exception:
        return None, None