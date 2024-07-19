def mysql_查询_条件查找(连接对象, 表名, 条件):
    """
    根据条件查询指定表的记录。

    参数：
        - 连接对象：与数据库的连接对象。
        - 表名 (str)：要查询的表名。
        - 条件 (str)：用于查询记录的条件字符串（严格遵守 MySQL 原生格式条件）。

    返回值：
        - 记录列表 (list)：满足条件的记录列表，如果查询失败则返回 None。
    """
    游标对象 = None
    try:
        游标对象 = 连接对象.cursor()
        游标对象.execute(f"SELECT * FROM {表名} WHERE {条件}")
        记录列表 = 游标对象.fetchall()
        return 记录列表
    except Exception:
        return None
    finally:
        if 游标对象:
            游标对象.close()