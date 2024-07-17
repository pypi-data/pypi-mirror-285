import subprocess


def 系统任务计划_删除(任务名称):
    """
    # 示例用法
    删除系统任务计划("MyTask")
    """
    # 使用 schtasks 命令删除任务计划
    subprocess.run(["schtasks", "/Delete", "/TN", 任务名称, "/F"])
