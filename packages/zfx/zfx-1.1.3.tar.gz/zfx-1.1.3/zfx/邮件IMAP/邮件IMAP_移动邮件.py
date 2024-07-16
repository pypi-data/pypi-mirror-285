def 邮件IMAP_移动邮件(连接对象, 邮件ID, 目标文件夹):
    """
    移动邮件到指定文件夹。

    参数:
        连接对象 (IMAP4_SSL): IMAP4_SSL连接对象。
        邮件ID (bytes): 要移动的邮件ID。
        目标文件夹 (str): 目标文件夹名称。

    返回:
        str: 操作状态。

    示例:
        状态 = 邮件IMAP_移动邮件(邮箱, b'1', '目标文件夹')
        if 状态 == "OK":
            print("邮件已移动")
        else:
            print("移动邮件失败")
    """
    try:
        连接对象.copy(邮件ID, 目标文件夹)
        连接对象.store(邮件ID, '+FLAGS', '\\Deleted')
        连接对象.expunge()
        return "OK"
    except Exception:
        return "FAIL"
