def mysql_更新_清空数据表(连接对象, 表名):
    """
    清空整个表的所有数据。

    参数：
        - 连接对象: 数据库连接对象。
        - 表名: 需要清空数据的表的名称。

    返回值：
        - 清空成功返回 True，失败返回 False。
    """
    游标 = None
    try:
        # 构造 TRUNCATE TABLE 语句以清空表的数据
        sql = f"TRUNCATE TABLE {表名};"

        # 获取游标对象，用于执行 SQL 语句
        游标 = 连接对象.cursor()
        # 执行 SQL 语句
        游标.execute(sql)
        # 提交事务，确保更改生效
        连接对象.commit()
        return True
    except Exception as e:
        return False
    finally:
        # 如果游标对象存在，关闭游标，释放资源
        if 游标:
            游标.close()