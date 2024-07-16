def 邮件IMAP_选择邮箱文件夹(连接对象, 文件夹名称="inbox"):
    """
    选择IMAP邮箱中的文件夹。

    参数:
        邮箱 (IMAP4_SSL): IMAP4_SSL连接对象。
        文件夹名称 (str): 文件夹名称，默认为收件箱 "inbox"。

    返回:
        bool: 选择成功返回True，否则返回False。

    小提示：
        常用的IMAP邮箱文件夹名称包括：
        收件箱： "INBOX"
        草稿箱： "Drafts"
        已发送： "Sent"
        垃圾邮件： "Junk"
        垃圾箱： "Trash"
        存档： "Archive"
        不同的邮件服务提供商可能使用不同的文件夹名称，但这些是较为常见的标准文件夹。您也可以根据需要检查服务器上实际存在的文件夹名称
    """
    try:
        连接对象.select(文件夹名称)
        return True
    except Exception:
        return False