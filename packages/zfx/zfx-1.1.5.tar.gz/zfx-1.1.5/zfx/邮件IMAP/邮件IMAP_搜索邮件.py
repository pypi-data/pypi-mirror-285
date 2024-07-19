def 邮件IMAP_搜索邮件(连接对象, 搜索条件="ALL"):
    """
    在 IMAP 邮箱中根据指定条件搜索邮件。

    参数:
        连接对象 (IMAP4_SSL): IMAP4_SSL 连接对象。
        搜索条件 (str): 要用于搜索的条件。默认为 "ALL"，表示搜索所有邮件。

    返回:
        list: 包含符合搜索条件的邮件的邮件ID列表。

    示例:
        # 使用默认搜索条件搜索所有邮件
        邮件ID列表 = 搜索邮件(邮箱)

        # 搜索发件人为 "example@example.com" 的邮件
        邮件ID列表 = 搜索邮件(邮箱, 'FROM "example@example.com"')

        # 搜索主题包含 "important" 的未读邮件
        邮件ID列表 = 搜索邮件(邮箱, '(UNSEEN) (SUBJECT "important")')

        # 搜索特定日期以后的邮件 (例如，2024年5月4日以后的邮件)
        邮件ID列表 = 搜索邮件(邮箱, 'SINCE 4-May-2024')

        # 搜索特定日期以后(5月4日，并包含5月4日)，并且主题包含指定文本的邮件（多个条件）
        搜索条件 = ' '.join(['(SINCE "4-May-2024")', '(SUBJECT "[Important] Activation Code for your Amazon Order")'])
        邮件ID列表 = 搜索邮件(邮箱, 搜索条件)

        # 以下是各种搜索条件
        "FROM"：按发件人进行搜索。
        "TO"：按收件人进行搜索。
        "SUBJECT"：按主题进行搜索。
        "BEFORE"：搜索在指定日期之前发送的邮件。
        "SINCE"：搜索在指定日期之后发送的邮件。
        "UNSEEN"：搜索未读的邮件。
        "FLAGGED"：搜索已标记的重要邮件等。
    """
    try:
        状态, 邮件数据 = 连接对象.search(None, 搜索条件)
        if 状态 != "OK":
            return []
        邮件ID列表 = 邮件数据[0].split()
        return 邮件ID列表
    except Exception:
        return []