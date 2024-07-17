import time
from selenium.webdriver.common.by import By


def 谷歌填表_查找元素(驱动器对象, 定位方法, 定位值):
    """
    在网页上查找元素。

    参数:
        - 驱动器对象: WebDriver 对象，即浏览器驱动器，用于在网页上执行操作。
        - 定位方法: 可以是 "ID"、"XPATH"、"CLASS_NAME"、"NAME"、"TAG_NAME"、"LINK_TEXT"、"PARTIAL_LINK_TEXT"、"CSS_SELECTOR" 等。
        - 定位值: 定位值，根据定位方法指定的方式，传入相应的定位值。

    返回:
        - 如果找到元素，则返回查找到的第一个元素对象，否则返回 None。
    """
    try:
        定位方法常量 = getattr(By, 定位方法.upper())
        元素对象 = 驱动器对象.find_element(定位方法常量, value=定位值)
        time.sleep(1)
        return 元素对象
    except Exception:
        return None