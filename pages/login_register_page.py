from utils.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, InvalidArgumentException
import time

class LoginRegisterPage(BasePage):
    # 页面地址
    LOGIN_URL = "https://demoqa.com/login"
    REGISTER_URL = "https://demoqa.com/register"

    # 登录页元素
    USERNAME_INPUT = (By.ID, "userName")
    PWD_INPUT = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login")
    NEW_USER_BTN = (By.ID, "newUser")
    ERROR_TIP = (By.ID, "name")
    PROFILE_HEADER = (By.CLASS_NAME, "main-header")

    # 注册页元素
    FIRST_NAME = (By.ID, "firstName")
    LAST_NAME = (By.ID, "lastName")
    USERNAME_REG = (By.ID, "userName")
    PWD_REG = (By.ID, "password")
    # 关键修正：基于密码框找兄弟元素，更精确
    EYE_ICON = (By.XPATH, "//input[@id='password']/following-sibling::span[contains(@class,'input-group-text')]")
    REGISTER_BTN = (By.ID, "register")
    BACK_TO_LOGIN = (By.ID, "gotologin")
    RECAPTCHA_FRAME = (By.XPATH, "//iframe[contains(@src,'recaptcha')]")
    RECAPTCHA_CHECK = (By.XPATH, "//div[@class='recaptcha-checkbox-border']")
    CAPTCHA_TIP = (By.ID, "captcha")

    # 打开登录页面
    def open_login(self):
        self.driver.get(self.LOGIN_URL)
        time.sleep(0.3)

    # 打开注册页面
    def open_register(self):
        self.driver.get(self.REGISTER_URL)
        time.sleep(0.3)

    # 登录输入账号密码
    def input_login_info(self, username, pwd):
        self.send_keys(self.USERNAME_INPUT, username)
        self.send_keys(self.PWD_INPUT, pwd)

    # 注册页输入密码（专门给注册页用）
    def input_register_pwd(self, pwd):
        self.send_keys(self.PWD_REG, pwd)

    # 点击登录
    def click_login(self):
        self.click(self.LOGIN_BTN)
        time.sleep(0.5)

    # 点击新用户跳转注册
    def click_new_user(self):
        self.click(self.NEW_USER_BTN)

    # 获取错误提示文本
    def get_error_text(self):
        try:
            return self.get_text(self.ERROR_TIP)
        except TimeoutException:
            return ""

    # 判断是否跳转到个人主页
    def is_profile_page(self):
        return "profile" in self.driver.current_url

    # 注册填写全部字段
    def fill_register_form(self, data):
        field_map = {
            "名字": self.FIRST_NAME,
            "姓氏": self.LAST_NAME,
            "用户名": self.USERNAME_REG,
            "密码": self.PWD_REG
        }
        for k, v in data.items():
            if k in field_map:
                try:
                    self.send_keys(field_map[k], v)
                except TimeoutException:
                    pass

    # 密码明文密文切换（加JS备用方案）
    def toggle_pwd_eye(self):
        try:
            self.click(self.EYE_ICON)
            time.sleep(0.2)
            return True
        except TimeoutException:
            # 备用：通过JS直接修改type属性
            try:
                pwd_input = self.driver.find_element(*self.PWD_REG)
                current_type = pwd_input.get_attribute("type")
                new_type = "text" if current_type == "password" else "password"
                self.driver.execute_script(
                    f"arguments[0].setAttribute('type', '{new_type}');", pwd_input
                )
                time.sleep(0.2)
                return True
            except Exception:
                return False

    # 点击注册按钮
    def click_register(self):
        self.click(self.REGISTER_BTN)
        time.sleep(0.5)

    # 返回登录页
    def back_login(self):
        self.click(self.BACK_TO_LOGIN)

    # 人机验证点击
    def click_recaptcha(self):
        try:
            self.driver.switch_to.frame(self.RECAPTCHA_FRAME)
            self.click(self.RECAPTCHA_CHECK)
            self.driver.switch_to.default_content()
            time.sleep(1)
            return True
        except (TimeoutException, InvalidArgumentException):
            self.driver.switch_to.default_content()
            return False

    # 获取人机验证提示
    def get_captcha_msg(self):
        try:
            return self.get_text(self.CAPTCHA_TIP)
        except TimeoutException:
            return ""

    # 判断输入框标红
    def input_is_error(self, locator):
        try:
            elem = self.wait_for_visible(locator)
            cls = elem.get_attribute("class") or ""
            return any(k in cls for k in ["field-error", "is-invalid", "invalid", "error"])
        except TimeoutException:
            return False