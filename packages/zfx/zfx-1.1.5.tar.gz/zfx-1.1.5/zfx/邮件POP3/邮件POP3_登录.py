import poplib


def 邮件POP3_登录(服务器地址, 用户名, 密码):
    """
    尝试连接到指定的POP3服务器并登录邮箱账户(只支持 110 端口的协议)。

    参数:
        - 服务器地址 (str): POP3服务器的地址。
        - 用户名 (str): 登录邮箱的用户名。
        - 密码 (str): 登录邮箱的密码。

    返回值:
        - 如果登录成功，返回连接成功的POP3服务器对象；如果登录失败或出现异常，返回假(False)。
    """
    try:
        # 连接到POP3服务器
        邮件服务器 = poplib.POP3(服务器地址, 110)

        # 尝试登录邮箱
        响应用户 = 邮件服务器.user(用户名)
        响应密码 = 邮件服务器.pass_(密码)

        # 判断登录是否成功
        if 响应用户.startswith(b'+OK') and 响应密码.startswith(b'+OK'):
            return 邮件服务器  # 返回连接成功的POP3服务器对象
    except Exception:
        return False  # 如果连接失败或登录失败，直接返回 False