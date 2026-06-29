'''基础页父类，封装通用 Selenium 操作：
打开页面、显式等待、点击、输入、获取文本、判断元素状态'''

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)  # 全局显式等待10秒

    # 通用打开页面方法
    def open(self, url):
        self.driver.get(url)
        self.driver.maximize_window()

    # 通用等待元素可点击
    def wait_for_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    # 通用等待元素可见
    def wait_for_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    # 通用点击方法
    def click(self, locator):
        self.wait_for_clickable(locator).click()

    # 通用输入方法
    def send_keys(self, locator, text):
        element = self.wait_for_visible(locator)
        element.clear()
        element.send_keys(text)

    # 通用获取元素文本
    def get_text(self, locator):
        return self.wait_for_visible(locator).text

    # 通用判断元素是否显示
    def is_displayed(self, locator):
        try:
            return self.wait_for_visible(locator).is_displayed()
        except TimeoutException:
            return False

    # 通用判断元素是否有错误样式（标红）
    def is_field_invalid(self, locator):
        element = self.wait_for_visible(locator)
        # 适配demoqa网站的错误样式class，可根据实际调整
        return "invalid" in element.get_attribute("class")