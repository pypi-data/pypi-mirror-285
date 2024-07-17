from selenium.webdriver.common.action_chains import ActionChains


def 谷歌填表_偏移点击(参_driver, 元素, x偏移量=0, y偏移量=0):
    """
    在元素上应用偏移量并点击。

    参数：
        - 参_driver: WebDriver 对象
        - 元素: 要点击的元素
        - x偏移量: X 轴偏移量，默认为 0
        - y偏移量: Y 轴偏移量，默认为 0

    返回:
        - bool: 成功返回 True，失败返回 False
    """
    try:
        # 创建 ActionChains 对象
        动作 = ActionChains(参_driver)

        # 将鼠标移动到元素位置，并添加偏移量
        动作.move_to_element_with_offset(元素, x偏移量, y偏移量)

        # 执行点击操作
        动作.click().perform()
        return True
    except Exception:
        return False