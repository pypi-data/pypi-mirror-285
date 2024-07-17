import configparser


def 配置文件_读配置项(config文件路径, 节名称, 配置项名称):
    """
    读取指定配置文件中的配置项值。

    参数:
        config文件路径 (str): 配置文件的路径。
        节名称 (str): 节的名称。
        配置项名称 (str): 配置项的名称。

    返回:
        str: 配置项的值，如果读取失败则返回 None。

    使用示例:
        value = 读取配置('config.ini', 'database', 'host')
    """
    try:
        # 创建 ConfigParser 对象
        config = configparser.ConfigParser()

        # 读取配置文件
        config.read(config文件路径)

        # 获取配置项值
        值 = config[节名称][配置项名称]
        return 值
    except Exception:
        return None  # 读取失败时返回 None