def mysql_查询_最后一条记录(连接对象, 表名):
    """
    查询指定表的最后一条记录。

    参数：
        - 连接对象：与数据库的连接对象。
        - 表名：要查询最后一条记录的表名。

    返回值：
        - 最后一条记录：表中的最后一条记录，如果查询失败则返回 None。
    """
    游标对象 = None
    try:
        游标对象 = 连接对象.cursor()
        游标对象.execute(f"SELECT * FROM {表名} ORDER BY id DESC LIMIT 1")
        最后一条记录 = 游标对象.fetchone()
        return 最后一条记录
    except Exception:
        return None
    finally:
        if 游标对象:
            游标对象.close()