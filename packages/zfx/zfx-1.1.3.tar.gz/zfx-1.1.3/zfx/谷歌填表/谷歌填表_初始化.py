from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def 谷歌填表_初始化(chrome驱动路径, 浏览器路径, 启动参数=[], 异常返回=False):
    """
    初始化谷歌填表驱动器。

    参数:
        - chrome驱动路径 (str): Chrome 驱动程序的路径。
        - 浏览器路径 (str): Chrome 浏览器的路径。
        - 启动参数 (list): 启动参数列表，每个元素是一个字符串，表示一个启动参数。
        - 异常返回 (bool, optional): 如果为 True，出现异常时返回异常信息；如果为 False，出现异常时返回 False。默认值为 False。

    返回:
        - WebDriver: Chrome 浏览器的 驱动器对象。成功返回 Chrome 浏览器的驱动器对象，失败返回 False 或异常信息。

    使用示例:
        - chrome驱动路径 = "C:\\Users\\Administrator\\Desktop\\chrome-win64\\chromedriver.exe"
        - 浏览器路径 = "C:\\Users\\Administrator\\Desktop\\chrome-win64\\chrome.exe"
        - 启动参数 = ["--incognito", "--disable-gpu"]  # 添加启动参数
        - 驱动器对象 = 谷歌填表_初始化(chrome驱动路径, 浏览器路径, 启动参数)
    """
    try:
        # 创建 ChromeDriver 服务对象
        chrome服务 = Service(chrome驱动路径)

        # 创建 Chrome 驱动器对象并指定服务
        选项 = webdriver.ChromeOptions()
        选项.binary_location = 浏览器路径

        # 添加启动参数
        for 参数 in 启动参数:
            选项.add_argument(参数)

        驱动器 = webdriver.Chrome(service=chrome服务, options=选项)
        return 驱动器
    except Exception as e:
        if 异常返回:
            return str(f"处理失败: {e}")
        return False
