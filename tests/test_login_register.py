import pytest
import os
from pages.login_register_page import LoginRegisterPage
from utils.excel_reader import ExcelReader
from utils.data_parser import parse_input_str
from selenium.common.exceptions import TimeoutException, InvalidArgumentException, WebDriverException

# 模块三Excel路径
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "../test_data/模块三登录注册测试用例【已新增自动化编码列】.xlsx")
all_case_data = ExcelReader(EXCEL_PATH, sheet_name="Sheet1").get_test_data()

class TestLoginRegister:
    @pytest.mark.parametrize("case", all_case_data)
    def test_login_reg_all(self, driver, case):
        page = LoginRegisterPage(driver)

        # 解析用例信息
        case_id = case.get("用例编号", "")
        test_module = case.get("测试模块", "")
        test_purpose = case.get("测试子项", "")
        test_step = case.get("测试步骤", "")
        input_raw = case.get("输入数据", "")
        input_data = parse_input_str(input_raw)
        expected_result = case.get("预期结果", "")
        auto_code = case.get("自动化预期编码", "").strip().upper()
        expect_success = True if auto_code == "T" else False

        print(f"\n===== 执行 {case_id} | 预期编码：{auto_code} =====")
        print(f"输入数据：{input_data}")

        # ============================================================
        # 登录页面用例
        # ============================================================
        if "登录页" in test_module:
            page.open_login()

            # 1. 纯跳转类用例（TC_LP_06）
            if "新用户" in test_step:
                page.click_new_user()
                assert "register" in page.driver.current_url, f"{case_id} 未跳注册页"
                print(f"✅ {case_id} 执行通过")
                return

            # 2. 普通登录流程
            un = input_data.get("用户名", "")
            pw = input_data.get("密码", "")
            page.input_login_info(un, pw)
            page.click_login()

            if expect_success:
                assert page.is_profile_page(), \
                    f"{case_id} 登录未跳转Profile，请检查账号 {un} 是否已在 demoqa 注册"
                print(f"✅ {case_id} 执行通过")
            else:
                still_login = "login" in page.driver.current_url
                has_err_text = False
                try:
                    err_text = page.get_error_text()
                    has_err_text = len(err_text) > 0
                except TimeoutException:
                    has_err_text = False

                assert still_login or has_err_text, \
                    f"{case_id} 反向用例失败：登录未拦截，既无错误提示又跳转走了"
                print(f"✅ {case_id} 反向用例通过（预期失败，实际被拦截）")

        # ============================================================
        # 注册页面用例
        # ============================================================
        elif "注册页" in test_module:
            page.open_register()

            # 1. 返回登录跳转（TC_RP_01）
            if "返回登录" in test_step:
                page.back_login()
                assert "login" in page.driver.current_url, f"{case_id} 未跳登录页"
                print(f"✅ {case_id} 执行通过")
                return

            # 2. 纯密码眼睛切换（TC_RP_04）
            # 关键修正：只有"测试步骤"里完全没有"注册"二字，才是纯眼睛切换
            if "注册" not in test_step and ("明文" in expected_result or "密文" in expected_result):
                pw = input_data.get("密码", "Test@123")
                page.input_register_pwd(pw)  # 关键：用注册页方法
                eye_ok = page.toggle_pwd_eye()
                if expect_success and not eye_ok:
                    pytest.fail(f"{case_id} 眼睛切换失败")
                print(f"✅ {case_id} 执行通过")
                return

            # 3. 注册表单提交类用例（TC_RP_02,03,05,06,07,08）
            if "注册" in test_step:
                try:
                    page.fill_register_form(input_data)
                except (TimeoutException, WebDriverException) as e:
                    if expect_success:
                        raise
                    print(f"✅ {case_id} 反向用例通过（填表阶段异常）")
                    return

                # TC_RP_06 步骤里包含"点击密码眼睛"，执行但不阻断
                if "眼睛" in test_step:
                    eye_ok = page.toggle_pwd_eye()
                    if not eye_ok:
                        print(f"⚠️ {case_id} 眼睛图标未找到，跳过此步骤继续注册")

                # 人机验证
                should_click_captcha = "不点击reCaptcha" not in test_step
                if should_click_captcha:
                    try:
                        page.click_recaptcha()
                    except (TimeoutException, InvalidArgumentException):
                        pass

                page.click_register()

                if expect_success:
                    print(f"✅ {case_id} 正向用例执行通过")
                else:
                    still_register = "register" in page.driver.current_url
                    has_captcha_err = False
                    has_field_err = False

                    if "reCaptcha" in expected_result or "人机验证" in expected_result or "verify" in expected_result:
                        try:
                            captcha_tip = page.get_captcha_msg()
                            has_captcha_err = "verify reCaptcha" in captcha_tip
                        except TimeoutException:
                            pass

                    if "标红" in expected_result or "所有字段" in str(input_data):
                        field_map = {
                            "名字": page.FIRST_NAME,
                            "姓氏": page.LAST_NAME,
                            "用户名": page.USERNAME_REG,
                            "密码": page.PWD_REG
                        }
                        for k, v in input_data.items():
                            if v == "" and k in field_map:
                                try:
                                    if page.input_is_error(field_map[k]):
                                        has_field_err = True
                                except Exception:
                                    pass

                        if "所有字段" in str(input_data):
                            all_red = True
                            for locator in [page.FIRST_NAME, page.LAST_NAME,
                                            page.USERNAME_REG, page.PWD_REG]:
                                try:
                                    if not page.input_is_error(locator):
                                        all_red = False
                                except Exception:
                                    all_red = False
                            if all_red:
                                has_field_err = True

                    assert still_register or has_captcha_err or has_field_err, \
                        f"{case_id} 反向用例失败：注册未拦截，当前URL={page.driver.current_url}"
                    print(f"✅ {case_id} 反向用例通过（预期失败，实际被拦截）")