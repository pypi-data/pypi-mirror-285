def mysql_执行SQL语句(连接对象, SQL语句):
    """
    执行任意 SQL语句 并返回结果。

    参数：
        - 连接对象：与数据库的连接对象。
        - SQL语句：要执行的SQL查询字符串。

    返回值：
        - 结果：查询结果列表，如果查询失败则返回 None。
    """
    游标对象 = None
    try:
        # 创建游标对象，用于执行SQL查询
        游标对象 = 连接对象.cursor()
        # 执行SQL查询
        游标对象.execute(SQL语句)
        # 如果是查询语句，获取查询结果
        if SQL语句.strip().lower().startswith('select'):
            结果 = 游标对象.fetchall()
            return 结果
        else:
            # 对于插入、更新、删除操作，提交事务
            连接对象.commit()
            return 游标对象.rowcount  # 返回受影响的行数
    except Exception as e:
        print(f"执行SQL失败: {e}")
        return None
    finally:
        # 无论是否发生异常，关闭游标对象以释放资源
        if 游标对象:
            游标对象.close()