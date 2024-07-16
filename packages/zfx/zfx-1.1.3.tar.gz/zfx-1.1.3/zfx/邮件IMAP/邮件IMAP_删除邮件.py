def 邮件IMAP_删除邮件(连接对象, 邮件ID):
    """
    删除IMAP邮箱中的邮件。

    参数:
        邮箱 (IMAP4_SSL): IMAP4_SSL连接对象。
        邮件ID (str): 邮件序列号或 UID，字符串格式。

    返回:
        bool: 删除成功返回True，否则返回False。
    """
    try:
        连接对象.store(邮件ID, "+FLAGS", "\\Deleted")
        连接对象.expunge()
        return True
    except Exception:
        return False