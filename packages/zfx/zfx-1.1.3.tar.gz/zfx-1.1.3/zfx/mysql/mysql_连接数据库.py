import mysql.connector


def mysql_连接数据库(主机, 用户名, 密码, 数据库名):
    """
    连接到MySQL数据库并返回 连接对象, 游标对象。

    参数：
        - 主机：数据库主机名或IP地址。
        - 用户名：数据库用户名。
        - 密码：数据库密码。
        - 数据库名：要连接的数据库名。

    返回值：
        - 连接对象：表示与数据库的连接。如果连接失败，则返回 False。
        - 游标对象：用于执行查询和获取结果。如果连接失败，则返回 False。
    """
    try:
        # 连接到数据库
        连接对象 = mysql.connector.connect(
            host=主机,
            user=用户名,
            password=密码,
            database=数据库名
        )

        # 创建游标对象
        游标对象 = 连接对象.cursor()

        # 返回连接对象和游标对象
        return 连接对象, 游标对象
    except Exception:
        return False, False