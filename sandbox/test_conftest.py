# sandbox/test_conftest.py
import pytest

def test_conftest_driver(driver):
    """测试conftest.py里的driver fixture是否能正常工作"""
    driver.get("https://www.baidu.com/")
    print(f"\n✅ conftest.py驱动正常！标题为：{driver.title}")
    assert "百度" in driver.title, "访问百度失败"
    print("✅ 测试通过！")