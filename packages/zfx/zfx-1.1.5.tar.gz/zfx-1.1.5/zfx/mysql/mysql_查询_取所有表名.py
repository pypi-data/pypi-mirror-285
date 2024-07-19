def mysql_查询_取所有表名(连接对象):
    """
    获取数据库中所有表名。

    参数：
        - 连接对象：与数据库的连接对象。

    返回值：
        - 表名列表：包含所有表名的列表，如果查询失败则返回 None。
    """
    游标对象 = None
    try:
        # 创建游标对象，用于执行SQL查询
        游标对象 = 连接对象.cursor()
        # 执行SQL查询，获取所有表名
        游标对象.execute("SHOW TABLES")
        # 将查询结果转换为列表
        表名列表 = [row[0] for row in 游标对象.fetchall()]
        return 表名列表
    except Exception:
        return None
    finally:
        # 无论是否发生异常，关闭游标对象以释放资源
        if 游标对象:
            游标对象.close()