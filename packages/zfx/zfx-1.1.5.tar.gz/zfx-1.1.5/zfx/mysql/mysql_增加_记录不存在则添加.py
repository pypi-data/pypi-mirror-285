def mysql_增加_记录不存在则添加(连接对象, 表名, 数据字典, 唯一字段, 唯一值):
    """
    如果记录不存在，则添加记录。

    参数：
        - 连接对象: 数据库连接对象。
        - 表名: 需要添加记录的表的名称。
        - 数据字典: 包含字段和值的字典，例如 {"字段1": "值1", "字段2": "值2"}。
        - 唯一字段: 用于检查记录是否存在的唯一字段。
        - 唯一值: 用于检查记录是否存在的唯一值。

    返回值：
        - 添加成功返回 True，失败返回 False。
    """
    游标 = None
    try:
        # 检查记录是否存在
        检查sql = f"SELECT COUNT(*) FROM {表名} WHERE {唯一字段} = '{唯一值}';"
        游标 = 连接对象.cursor()
        游标.execute(检查sql)
        记录数 = 游标.fetchone()[0]

        if 记录数 > 0:
            return False

        # 构造字段和对应值的列表
        字段列表 = ", ".join(数据字典.keys())
        值列表 = ", ".join([f"'{值}'" for 值 in 数据字典.values()])

        # 构造完整的插入 SQL 语句
        插入sql = f"INSERT INTO {表名} ({字段列表}) VALUES ({值列表});"

        # 执行插入 SQL 语句
        游标.execute(插入sql)
        # 提交事务，确保更改生效
        连接对象.commit()
        return True
    except Exception as e:
        return False
    finally:
        # 如果游标对象存在，关闭游标，释放资源
        if 游标:
            游标.close()