import requests
import os
import shutil


def 网页协议_图片下载(图片链接, 保存目录, 图片名称):
    """
    下载图片并保存到指定目录和文件名。

    参数：
        - 图片链接 (str): 图片的URL链接。
        - 保存目录 (str): 保存图片的本地目录路径。
        - 图片名称 (str): 保存的图片文件名。

    返回值：
        - bool: 下载成功返回 True，下载失败返回 False。

    示例使用：
        图片链接 = "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"
        保存目录 = r"C:\tmp"
        图片名称 = 'downloaded_image.png'
        结果 = 网页协议_图片下载(图片链接, 保存目录, 图片名称)
        print(结果)
    """
    try:
        # 确保保存目录存在，如果不存在则创建
        if not os.path.exists(保存目录):
            os.makedirs(保存目录)

        # 构造完整的文件路径
        文件路径 = os.path.join(保存目录, 图片名称)

        # 发送GET请求获取图片
        response = requests.get(图片链接, stream=True)

        # 检查请求是否成功（状态码200表示成功）
        if response.status_code == 200:
            # 打开本地文件，准备写入
            with open(文件路径, 'wb') as file:
                # 使用shutil.copyfileobj将响应内容保存到文件
                shutil.copyfileobj(response.raw, file)
            return True
        else:
            return False
    except Exception:
        return False