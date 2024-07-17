def 邮件IMAP_获取完整邮件(连接对象, 邮件ID):
    """
    从 IMAP 邮箱中获取指定邮件。

    参数:
        连接对象 (IMAP4_SSL): IMAP4_SSL 连接对象。
        邮件ID (bytes): 要获取的邮件的 ID。

    返回:
        tuple: 包含状态和邮件数据的元组。

    示例:
        # 从邮箱中获取指定邮件
        邮件ID = b'1'  # 假设邮件的 ID 是 '1'
        状态, 邮件数据 = 邮件IMAP_获取完整邮件(邮箱, 邮件ID)

        if 状态 == "OK":
            print("邮件数据:", 邮件数据)
        else:
            print("获取邮件失败")
    """
    try:
        # 获取邮件数据
        状态, 邮件数据 = 连接对象.fetch(邮件ID, "(RFC822)")
        return 状态, 邮件数据
    except Exception:
        return None, None
