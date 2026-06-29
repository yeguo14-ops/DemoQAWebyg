# 临时测试浏览器启动
# sandbox/test_driver.py
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def test_browser_launch():
    """测试浏览器是否能正常启动并访问百度"""
    print("\n🚀 单独测试：启动Chrome浏览器...")

    # 你的ChromeDriver路径
    chrome_driver_path = r"C:\Users\admin\AppData\Local\Python\pythoncore-3.14-64\chromedriver.exe"

    # 创建Service对象
    service = Service(executable_path=chrome_driver_path)

    # 启动浏览器
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.implicitly_wait(10)

    # 访问百度
    driver.get("https://www.baidu.com/")
    print(f"✅ 浏览器启动成功！标题为：{driver.title}")

    # 断言
    assert "百度" in driver.title, f"标题中未找到'百度'，实际标题为：{driver.title}"

    print("✅ 测试通过！浏览器将在3秒后关闭...")
    import time
    time.sleep(3)

    driver.quit()
    print("🔚 浏览器已关闭")