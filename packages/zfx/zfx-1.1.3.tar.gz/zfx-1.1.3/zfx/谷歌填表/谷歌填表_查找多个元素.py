import time
from selenium.webdriver.common.by import By


def 谷歌填表_查找多个元素(驱动器对象, 定位方法, 定位值):
    """
    在网页上查找多个元素。

    参数:
        - 驱动器对象: WebDriver 对象，即浏览器驱动器，用于在网页上执行操作。
        - 定位方法: 可以是 "ID"、"XPATH"、"CLASS_NAME"、"NAME"、"TAG_NAME"、"LINK_TEXT"、"PARTIAL_LINK_TEXT"、"CSS_SELECTOR" 等。
        - 定位值: 定位值，根据定位方法指定的方式，传入相应的定位值。

    返回:
        - list: 查找到的所有元素列表。如果找不到任何元素，则返回 None。
    """
    try:
        定位方法常量 = getattr(By, 定位方法.upper())
        元素对象列表 = 驱动器对象.find_elements(定位方法常量, value=定位值)
        time.sleep(1)
        return 元素对象列表
    except Exception:
        return None