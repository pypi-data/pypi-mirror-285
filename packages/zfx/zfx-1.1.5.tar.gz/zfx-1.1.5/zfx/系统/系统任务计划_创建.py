import xml.etree.ElementTree as ET
import subprocess, os
from datetime import datetime, timedelta


def 系统任务计划_创建(任务名称, 执行的文件):
    """
        # 示例用法,注意：参数不能包含中文
        创建系统任务计划("MyTask", "C:\\path\\to\\script.py")
    """
    # 计算启动时间（当前时间 + 5分钟）
    start_time = datetime.now() + timedelta(minutes=5)
    start_boundary = start_time.strftime("%Y-%m-%dT%H:%M:%S")

    # 创建 XML 元素
    root = ET.Element("Task", version="1.2", xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task")
    registration_info = ET.SubElement(root, "RegistrationInfo")
    ET.SubElement(registration_info, "Author").text = "Administrator"
    ET.SubElement(registration_info, "URI").text = "\\" + 任务名称
    triggers = ET.SubElement(root, "Triggers")
    time_trigger = ET.SubElement(triggers, "TimeTrigger")
    repetition = ET.SubElement(time_trigger, "Repetition")
    ET.SubElement(repetition, "Interval").text = "PT1H"
    ET.SubElement(repetition, "Duration").text = "P9999D"  # 设置为无限期
    ET.SubElement(repetition, "StopAtDurationEnd").text = "false"
    ET.SubElement(time_trigger, "StartBoundary").text = start_boundary  # 设置启动时间
    ET.SubElement(time_trigger, "Enabled").text = "true"
    principals = ET.SubElement(root, "Principals")
    principal = ET.SubElement(principals, "Principal", id="Author")
    ET.SubElement(principal, "UserId").text = "S-1-5-21-3825598007-1340154419-189627469-500"
    ET.SubElement(principal, "LogonType").text = "InteractiveToken"
    ET.SubElement(principal, "RunLevel").text = "LeastPrivilege"
    settings = ET.SubElement(root, "Settings")
    ET.SubElement(settings, "MultipleInstancesPolicy").text = "IgnoreNew"
    ET.SubElement(settings, "DisallowStartIfOnBatteries").text = "true"
    ET.SubElement(settings, "StopIfGoingOnBatteries").text = "true"
    ET.SubElement(settings, "AllowHardTerminate").text = "true"
    ET.SubElement(settings, "StartWhenAvailable").text = "false"
    ET.SubElement(settings, "RunOnlyIfNetworkAvailable").text = "false"
    idle_settings = ET.SubElement(settings, "IdleSettings")
    ET.SubElement(idle_settings, "StopOnIdleEnd").text = "true"
    ET.SubElement(idle_settings, "RestartOnIdle").text = "false"
    ET.SubElement(settings, "AllowStartOnDemand").text = "true"
    ET.SubElement(settings, "Enabled").text = "true"
    ET.SubElement(settings, "Hidden").text = "false"
    ET.SubElement(settings, "RunOnlyIfIdle").text = "false"
    ET.SubElement(settings, "WakeToRun").text = "false"
    ET.SubElement(settings, "ExecutionTimeLimit").text = "PT72H"
    ET.SubElement(settings, "Priority").text = "7"
    actions = ET.SubElement(root, "Actions", Context="Author")
    exec_elem = ET.SubElement(actions, "Exec")
    ET.SubElement(exec_elem, "Command").text = 执行的文件

    # 保存 XML 文件
    xml_file = f"{任务名称}.xml"
    with open(xml_file, "wb") as f:
        f.write(ET.tostring(root, encoding="utf-8"))

    # 使用 schtasks 命令添加任务计划
    subprocess.run(["schtasks", "/Create", "/TN", 任务名称, "/XML", xml_file, "/F"])

    # 删除临时文件
    os.remove(xml_file)