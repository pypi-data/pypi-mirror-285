def 邮件IMAP_获取文件夹列表(连接对象):
    """
    获取邮箱中的所有文件夹列表。

    参数:
        连接对象 (IMAP4_SSL): IMAP4_SSL连接对象。

    返回:
        list: 文件夹名称列表。如果获取失败，返回空列表。

    示例:
        文件夹列表 = 邮件IMAP_获取文件夹列表(邮箱)
        if 文件夹列表:
            print("邮箱文件夹列表:", 文件夹列表)
        else:
            print("获取文件夹列表失败")
    """
    try:
        状态, 文件夹 = 连接对象.list()
        if 状态 != 'OK':
            return []
        return [文件夹.decode().split(' "/" ')[1] for 文件夹 in 文件夹]
    except Exception:
        return []
