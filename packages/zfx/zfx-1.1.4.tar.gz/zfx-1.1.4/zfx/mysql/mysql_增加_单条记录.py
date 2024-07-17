def mysql_增加_单条记录(连接对象, 表名, 数据字典):
    """
    添加一条记录到指定的表中。

    参数：
        - 连接对象: 数据库连接对象。
        - 表名: 需要添加记录的表的名称。
        - 数据字典: 包含字段和值的字典，例如 {"字段1": "值1", "字段2": "值2"}。

    返回值：
        - 添加成功返回 True，失败返回 False。
    """
    游标 = None
    try:
        # 构造字段和对应值的列表
        字段列表 = ", ".join(数据字典.keys())
        值列表 = ", ".join([f"'{值}'" for 值 in 数据字典.values()])

        # 构造完整的插入 SQL 语句
        sql = f"INSERT INTO {表名} ({字段列表}) VALUES ({值列表});"

        # 获取游标对象，用于执行 SQL 语句
        游标 = 连接对象.cursor()
        # 执行 SQL 语句
        游标.execute(sql)
        # 提交事务，确保更改生效
        连接对象.commit()
        return True
    except Exception:
        return False
    finally:
        # 如果游标对象存在，关闭游标，释放资源
        if 游标:
            游标.close()