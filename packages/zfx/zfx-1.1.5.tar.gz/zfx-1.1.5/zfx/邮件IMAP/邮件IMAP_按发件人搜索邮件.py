def 邮件IMAP_按发件人搜索邮件(连接对象, 发件人邮箱):
    """
    按发件人搜索邮件。

    参数:
        连接对象 (IMAP4_SSL): IMAP4_SSL 连接对象。
        发件人 (str): 发件人邮箱地址。

    返回:
        list: 包含符合搜索条件的邮件的邮件ID列表。

    示例:
        邮件ID列表 = 邮件IMAP_按发件人搜索邮件(连接对象, 'example@example.com')
    """
    try:
        搜索条件 = f'FROM "{发件人邮箱}"'
        状态, 邮件数据 = 连接对象.search(None, 搜索条件)
        if 状态 != "OK":
            return []
        邮件ID列表 = 邮件数据[0].split()
        return 邮件ID列表
    except Exception:
        return []