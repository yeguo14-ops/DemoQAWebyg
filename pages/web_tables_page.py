import time
from utils.base_page import BasePage
from selenium.webdriver.common.by import By


class WebTablesPage(BasePage):
    PAGE_URL = "https://demoqa.com/webtables"

    ADD_BUTTON = (By.ID, "addNewRecordButton")
    POPUP_CLOSE_BUTTON = (By.XPATH, "//button[@aria-label='Close']")

    TABLE_ROWS = (By.XPATH, "//table/tbody/tr")
    TABLE_BODY = (By.XPATH, "//table/tbody")
    SEARCH_INPUT = (By.ID, "searchBox")

    FIELD_LOCATORS = {
        "名": (By.ID, "firstName"),
        "姓": (By.ID, "lastName"),
        "邮箱": (By.ID, "userEmail"),
        "年龄": (By.ID, "age"),
        "薪资": (By.ID, "salary"),
        "部门": (By.ID, "department"),
    }

    FIELD_ORDER = ["名", "姓", "年龄", "邮箱", "薪资", "部门"]

    DEFAULT_VALID_DATA = {
        "名": "Auto",
        "姓": "Test",
        "邮箱": "auto@test.com",
        "年龄": "25",
        "薪资": "50000",
        "部门": "IT",
    }

    def open(self):
        super().open(self.PAGE_URL)
        self.dismiss_ads()
        time.sleep(0.6)

    def dismiss_ads(self):
        try:
            self.driver.execute_script(
                """
                const ad = document.getElementById('fixedban');
                if (ad) ad.remove();
                const footer = document.getElementById('adplus-anchor');
                if (footer) footer.remove();
                """
            )
        except Exception:
            pass

    def wait_table_loaded(self):
        try:
            self.wait_for_visible(self.TABLE_BODY)
            time.sleep(0.3)
        except Exception:
            time.sleep(1)

    def get_all_rows(self):
        return self.driver.find_elements(*self.TABLE_ROWS)

    def open_add_popup(self):
        self.wait_table_loaded()
        self.dismiss_ads()
        self.click(self.ADD_BUTTON)
        time.sleep(0.4)
        return self.is_popup_open()

    def open_edit_popup(self, row_num=1):
        self.wait_table_loaded()
        self.dismiss_ads()
        edit_button = (By.ID, f"edit-record-{row_num}")
        self.click(edit_button)
        time.sleep(0.5)
        return self.is_popup_open()

    def get_popup_field_value(self, field_name):
        locator = self.FIELD_LOCATORS[field_name]
        element = self.wait_for_visible(locator)
        return (element.get_attribute("value") or "").strip()

    def fill_popup_form(self, data, use_defaults=False):
        if "所有字段" in data:
            for locator in self.FIELD_LOCATORS.values():
                element = self.wait_for_visible(locator)
                element.clear()
            return

        fill_data = data
        if use_defaults:
            fill_data = {**self.DEFAULT_VALID_DATA, **data}

        for field_name, value in fill_data.items():
            if field_name in self.FIELD_LOCATORS:
                locator = self.FIELD_LOCATORS[field_name]
                element = self.wait_for_visible(locator)
                element.clear()
                if value:
                    element.send_keys(value)

    def submit_popup(self):
        submit_btn = (By.XPATH, "//div[contains(@class,'modal-content')]//button[@id='submit']")
        self.click(submit_btn)
        time.sleep(1.0)

    def close_popup(self):
        self.click(self.POPUP_CLOSE_BUTTON)
        time.sleep(0.4)

    def delete_row(self, row_num=1):
        self.wait_table_loaded()
        self.dismiss_ads()
        delete_button = (By.ID, f"delete-record-{row_num}")
        self.click(delete_button)
        time.sleep(0.8)

    def delete_rows_until_count(self, target_count):
        while len(self.get_all_rows()) > target_count:
            self.delete_row(1)
            time.sleep(0.3)

    def get_row_data(self, row_num=1):
        row_cells = (By.XPATH, f"//table/tbody/tr[{row_num}]/td")
        elements = self.driver.find_elements(*row_cells)
        row_data = {}
        for i, field in enumerate(self.FIELD_ORDER):
            if i < len(elements):
                row_data[field] = elements[i].text.strip()
        return row_data

    def is_row_exists(self, data):
        all_rows = self.get_all_rows()
        for idx in range(1, len(all_rows) + 1):
            row_data = self.get_row_data(idx)
            match = True
            for key, value in data.items():
                if value and row_data.get(key) != value:
                    match = False
                    break
            if match:
                return True, idx
        return False, 0

    def search(self, keyword):
        search_input = self.wait_for_visible(self.SEARCH_INPUT)
        search_input.clear()
        search_input.send_keys(keyword)
        time.sleep(0.6)

    def is_popup_open(self):
        try:
            title = self.driver.find_element(
                By.XPATH,
                "//div[contains(@class,'modal-content')]//div[contains(text(),'Registration Form')]",
            )
            if title.is_displayed():
                return True
        except Exception:
            pass
        try:
            submit_btn = self.driver.find_element(
                By.XPATH,
                "//div[contains(@class,'modal-content')]//button[@id='submit']",
            )
            if submit_btn.is_displayed():
                return True
        except Exception:
            pass
        return False

    def is_field_error(self, field_name):
        if field_name in self.FIELD_LOCATORS:
            locator = self.FIELD_LOCATORS[field_name]
            element = self.driver.find_element(*locator)
            class_attr = element.get_attribute("class") or ""
            aria_invalid = element.get_attribute("aria-invalid")
            return "is-invalid" in class_attr or aria_invalid == "true"
        return False

    def is_empty_state(self):
        if len(self.get_all_rows()) == 0:
            return True
        try:
            empty_msg = self.driver.find_element(By.XPATH, "//div[contains(text(),'No rows found')]")
            return empty_msg.is_displayed()
        except Exception:
            return False

    def get_page_info_text(self):
        try:
            page_info = self.driver.find_element(By.XPATH, "//div[contains(@class,'-pageInfo')]")
            return page_info.text
        except Exception:
            return ""

    def get_table_all_data(self):
        all_rows = self.get_all_rows()
        result = []
        for i in range(1, len(all_rows) + 1):
            result.append(self.get_row_data(i))
        return result
