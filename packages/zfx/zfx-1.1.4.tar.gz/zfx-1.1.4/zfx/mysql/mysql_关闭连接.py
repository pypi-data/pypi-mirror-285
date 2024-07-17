def mysql_关闭连接(连接对象, 游标对象=None):
    """
    关闭数据库连接和游标对象。

    参数：
        - 连接: 数据库连接对象。
        - 游标对象：可选，数据库游标对象。如果提供了游标对象，则同时关闭游标对象；如果未提供，则仅关闭连接对象。

    返回值：
        - 成功返回 True，失败返回 False
    """
    try:
        # 关闭游标对象（如果提供）
        if 游标对象:
            游标对象.close()

        # 关闭连接对象
        连接对象.close()
        return True
    except Exception:
        return False