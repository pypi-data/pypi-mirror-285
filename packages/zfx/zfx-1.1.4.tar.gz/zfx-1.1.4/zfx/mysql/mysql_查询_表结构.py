def mysql_查询_表结构(连接对象, 表名):
    """
    导出指定表的结构信息：字段名、数据类型、长度、是否允许为 NULL、是否为主键、是否自增等，获得的 表结构信息 可直接用于mysql_创建新表。

    参数：
        - 连接对象：MySQL 数据库连接对象。
        - 表名：要导出结构的表名。

    返回值：
        - 表结构信息：返回一个列表，每个元素为一个字典，包含每个字段的详细信息，如字段名、数据类型、长度、是否允许为空、是否为主键、是否自增等。
          如果获取结构失败，返回空列表。
    """
    表结构信息列表 = []

    try:
        # 查询表结构信息
        查询字段信息 = f"SELECT COLUMN_NAME, COLUMN_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_KEY, EXTRA " \
                     f"FROM information_schema.COLUMNS " \
                     f"WHERE TABLE_SCHEMA = '{连接对象.database}' AND TABLE_NAME = '{表名}'"

        cursor = 连接对象.cursor()

        # 获取字段信息
        cursor.execute(查询字段信息)
        字段结果 = cursor.fetchall()

        # 遍历每个字段的信息
        for row in 字段结果:
            字段名 = row[0]
            列类型 = row[1]
            if '(' in 列类型 and 列类型.endswith(')'):
                数据类型, 长度 = 列类型.split('(')
                长度 = 长度[:-1]
            else:
                数据类型, 长度 = 列类型, None
            是否允许为空 = row[3]
            是否主键 = (row[4] == 'PRI')
            是否自增 = ('auto_increment' in row[5])

            # 将字段信息添加到列表中
            表结构信息列表.append({
                "字段名": 字段名,
                "数据类型": 数据类型,
                "长度": 长度,
                "是否允许为空": 是否允许为空,
                "是否主键": 是否主键,
                "是否自增": 是否自增
            })

        return 表结构信息列表

    except Exception:
        return []