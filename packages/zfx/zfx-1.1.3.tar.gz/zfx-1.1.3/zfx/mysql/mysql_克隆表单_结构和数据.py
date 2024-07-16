def mysql_克隆表单_结构和数据(连接对象, 源表名, 目标表名):
    """
    复制源表的结构和数据到目标表。

    参数：
        - 连接对象：MySQL 数据库连接对象。
        - 源表名：要复制结构和数据的源表名称。
        - 目标表名：目标表的名称。

    返回值：
        - 克隆成功返回 True，失败返回 False。
    """
    try:
        cursor = 连接对象.cursor()

        # 检查目标表是否存在
        查询目标表语句 = f"SHOW TABLES LIKE '{目标表名}'"
        cursor.execute(查询目标表语句)
        if cursor.fetchone():
            print(f"目标表 '{目标表名}' 已存在，无需创建。")
        else:
            # 查询源表的结构信息
            查询结构语句 = f"SHOW CREATE TABLE {源表名}"
            cursor.execute(查询结构语句)
            结构结果 = cursor.fetchone()
            创建语句 = 结构结果[1].replace(源表名, 目标表名)

            # 创建目标表
            cursor.execute(创建语句)

        # 复制数据
        复制数据语句 = f"INSERT INTO {目标表名} SELECT * FROM {源表名}"
        cursor.execute(复制数据语句)

        连接对象.commit()
        return True

    except Exception:
        return False