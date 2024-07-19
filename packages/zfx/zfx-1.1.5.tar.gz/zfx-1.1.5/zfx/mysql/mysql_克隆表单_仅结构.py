def mysql_克隆表单_仅结构(连接对象, 源表名, 目标表名, 自动递增是否重置=False):
    """
    仅复制源表的表结构到目标表。

    参数：
        - 连接对象：MySQL 数据库连接对象。
        - 源表名：要复制结构的源表名称。
        - 目标表名：目标表的名称。
        - 自动递增是否归重置：为真则重置为1，为假则保持原样，默认为假。

    返回值：
        - 克隆成功返回 True，失败返回 False。
    """
    try:
        cursor = 连接对象.cursor()

        # 查询源表的结构信息
        查询语句 = f"SHOW CREATE TABLE {源表名}"
        cursor.execute(查询语句)
        结果 = cursor.fetchone()

        # 提取创建表的语句
        创建语句 = 结果[1]

        # 替换表名为目标表名
        创建语句 = 创建语句.replace(源表名, 目标表名)

        # 执行创建表操作
        cursor.execute(创建语句)

        # 如果需要重置自动递增的值
        if 自动递增是否重置:
            重置语句 = f"ALTER TABLE {目标表名} AUTO_INCREMENT = 1"
            cursor.execute(重置语句)

        连接对象.commit()
        return True

    except Exception as e:
        return False