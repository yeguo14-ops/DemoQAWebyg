# conftest.py
import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


@pytest.fixture(scope="function")
def driver():
    """每个测试用例启动一个Chrome浏览器（使用本地ChromeDriver）"""
    print("\n🚀 启动Chrome浏览器...")

    # 你的ChromeDriver路径（和sandbox里测试通过的一致）
    chrome_driver_path = r"C:\Users\admin\AppData\Local\Python\pythoncore-3.14-64\chromedriver.exe"

    # 创建Service对象
    service = Service(executable_path=chrome_driver_path)

    # 启动浏览器
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.implicitly_wait(10)  # 隐式等待10秒

    yield driver

    print("\n🔚 关闭浏览器...")
    time.sleep(1)
    driver.quit()

