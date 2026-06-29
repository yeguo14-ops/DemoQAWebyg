import pytest
import time
import os
from selenium.webdriver.common.by import By
from pages.web_tables_page import WebTablesPage
from utils.excel_reader import ExcelReader
from utils.data_parser import parse_input_str

EXCEL_FILES = [
    "../test_data/模块二WebTables测试用例1_【已新增自动化编码列】.xlsx",
    "../test_data/模块二WebTables测试用例2_添加模块【已新增自动化编码列】.xlsx",
    "../test_data/模块二WebTables测试用例3_修改模块【已新增自动化编码列】.xlsx",
]

all_case_data = []
base_path = os.path.dirname(__file__)
for rel_path in EXCEL_FILES:
    full_path = os.path.join(base_path, rel_path)
    reader = ExcelReader(full_path, sheet_name="Sheet1")
    case_list = reader.get_test_data()
    all_case_data.extend(case_list)


def _resolve_action_type(test_module, test_purpose):
    if "搜索" in test_module:
        return "search"
    if "删除" in test_module:
        return "delete"
    if "排序" in test_module or "分页" in test_module:
        return "sort_page"
    if (
        "编辑弹窗" in test_module
        or "弹窗表单校验-编辑" in test_module
        or ("编辑" in test_module and "新增" not in test_module)
        or ("弹窗表单校验" in test_module and "编辑" in test_purpose)
    ):
        return "edit"
    if (
        "新增" in test_module
        or test_module.startswith("弹窗表单校验")
        or "弹窗表单校验-新增" in test_module
        or "弹窗表单校验-正向" in test_module
    ):
        return "add"
    return "unknown"


def _should_use_default_fields(test_module, input_data):
    """单字段校验/边界测试时，其余字段需先填合法值。"""
    if "所有字段" in input_data:
        return False
    if not test_module.startswith("弹窗表单校验"):
        return False
    provided = {k for k in input_data if k in WebTablesPage.FIELD_LOCATORS}
    return len(provided) < len(WebTablesPage.FIELD_LOCATORS)


class TestWebTablesAll:
    @pytest.mark.parametrize("case", all_case_data)
    def test_web_tables_full_flow(self, driver, case):
        page = WebTablesPage(driver)
        page.open()
        time.sleep(0.6)

        case_id = case.get("用例编号", "")
        test_module = case.get("测试模块", "")
        test_purpose = case.get("测试子项", "")
        test_step = case.get("测试步骤", "")
        input_raw = case.get("输入数据", "")
        input_data = parse_input_str(input_raw)
        expected_result = case.get("预期结果", "")
        auto_code = case.get("自动化预期编码", "").strip().upper()
        expect_success = auto_code == "T"

        print(f"\n===== 【{case_id}】预期{'T' if expect_success else 'F'} =====")
        print(f"测试目的：{test_purpose}")
        print(f"输入数据：{input_data}")

        check_table_data = False
        data_match = False
        popup_should_close = False
        action_type = _resolve_action_type(test_module, test_purpose)

        if action_type == "add":
            page.open_add_popup()
            use_defaults = _should_use_default_fields(test_module, input_data)
            page.fill_popup_form(input_data, use_defaults=use_defaults)

            if "提交" in test_step:
                page.submit_popup()
                popup_should_close = True
                check_table_data = True
                time.sleep(0.5)
                verify_data = {**page.DEFAULT_VALID_DATA, **input_data} if use_defaults else input_data
                data_match, row_idx = page.is_row_exists(verify_data)
                print(f"  新增后查找：match={data_match}, row={row_idx}")
                if not data_match:
                    print(f"  表格当前数据：{page.get_table_all_data()}")
            elif "×" in test_step or "关闭" in test_step:
                page.close_popup()
                popup_should_close = True
                check_table_data = True
                data_match, _ = page.is_row_exists(input_data)

        elif action_type == "edit":
            page.open_edit_popup(row_num=1)

            if "回填" in expected_result or "数据回填" in test_purpose:
                origin_data = page.get_row_data(1)
                print(f"  回填校验：{origin_data}")
                for k, v in origin_data.items():
                    if v and k in page.FIELD_LOCATORS:
                        actual = page.get_popup_field_value(k)
                        assert actual == v, f"{case_id} 回填不一致：{k}期望[{v}]实际[{actual}]"

            page.fill_popup_form(input_data)

            if "提交" in test_step:
                page.submit_popup()
                popup_should_close = True
                check_table_data = True
                time.sleep(0.5)
                new_row = page.get_row_data(1)
                print(f"  编辑后数据：{new_row}")
                data_match = True
                for k, v in input_data.items():
                    if v and new_row.get(k) != v:
                        data_match = False
                        print(f"  不匹配：{k} 期望[{v}] 实际[{new_row.get(k)}]")
            elif "×" in test_step or "关闭" in test_step:
                page.close_popup()
                popup_should_close = True
                check_table_data = True
                origin_data = page.get_row_data(1)
                data_changed = any(
                    v and origin_data.get(k) == v for k, v in input_data.items()
                )
                # 取消类：T 表示验证通过(未改动)，F 表示 data_match=True 代表发生了错误改动
                data_match = not data_changed if expect_success else data_changed

        elif action_type == "delete":
            if "空状态" in test_purpose:
                page.delete_rows_until_count(1)
            origin_data = page.get_row_data(1)
            print(f"  删除前数据：{origin_data}")
            page.delete_row(1)
            check_table_data = True
            still_exists, _ = page.is_row_exists(origin_data)
            data_match = not still_exists
            print(f"  删除后查找：match={still_exists}")
            if "空状态" in test_purpose or "No rows" in expected_result:
                is_empty = page.is_empty_state()
                print(f"  空状态：{is_empty}")
                assert is_empty, f"{case_id} 删除后应显示空状态提示"

        elif action_type == "search":
            keyword = input_data.get("关键词", "")
            page.search(keyword)
            check_table_data = True
            if "无结果" in test_purpose or "No rows" in expected_result:
                data_match = page.is_empty_state()
            else:
                rows = page.get_all_rows()
                data_match = False
                for i in range(1, len(rows) + 1):
                    row_data = page.get_row_data(i)
                    row_text = " ".join(row_data.values()).lower()
                    if keyword.lower() in row_text:
                        data_match = True
                        break

        elif action_type == "sort_page":
            if "排序" in test_module:
                age_header = (By.XPATH, "//th[contains(text(),'Age')]")
                try:
                    page.click(age_header)
                    time.sleep(0.3)
                    page.click(age_header)
                    time.sleep(0.3)
                except Exception:
                    pass

            if "分页" in test_module:
                page_info = page.get_page_info_text()
                print(f"  分页信息：{page_info}")

        popup_open = page.is_popup_open()
        print(f"  弹窗状态：popup_open={popup_open}, should_close={popup_should_close}")

        is_cancel_case = "×" in test_step or "关闭" in test_step or "取消" in test_module
        is_submit_case = "提交" in test_step

        if expect_success:
            if popup_should_close:
                assert not popup_open, f"{case_id} 正向操作弹窗应关闭"
            if check_table_data:
                assert data_match, f"【业务缺陷】{case_id} 合法操作无数据"
        else:
            if is_cancel_case:
                assert not popup_open, f"{case_id} 取消操作弹窗应关闭"
                if check_table_data:
                    assert not data_match, f"{case_id} 取消操作不应有数据变更"
                print(f"✅ {case_id} 取消类反向用例通过")
            elif is_submit_case:
                assert popup_open, f"{case_id} 非法提交弹窗应被拦截"
                print(f"✅ {case_id} 非法提交被拦截（弹窗未关闭）")

        print(f"✅ {case_id} 执行通过")
