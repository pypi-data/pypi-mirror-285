def 邮件POP3_删除邮件(服务器对象, 邮件索引):
    """
    删除指定索引的邮件。

    参数:
        - 服务器对象 (poplib.POP3): 已连接的POP3服务器对象。
        - 邮件索引 (int): 要删除的邮件的索引。

    返回值:
        - bool: 如果成功删除邮件，则返回True；否则返回False。

    注意:
        - 删除邮件后，需要调用断开连接函数 `zfx.邮件pop3_断开连接(服务器对象)` 才会生效。
    """
    try:
        服务器对象.dele(邮件索引)
        return True
    except Exception:
        return False