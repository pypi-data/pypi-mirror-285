import winreg


def 系统任务计划_遍历名称():
    """
    # 示例用法
    打印所有任务计划名称()
    """
    # 打开注册表键
    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            print("任务计划库中的任务名称：")
            # 枚举注册表子项
            for i in range(winreg.QueryInfoKey(key)[0]):
                task_name = winreg.EnumKey(key, i)
                print(task_name)
    except FileNotFoundError:
        print("找不到任务计划库的注册表项。")