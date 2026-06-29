from utils.data_parser import parse_input_str

def resolve_case_expect(case: dict):
    """
    读取Excel单行用例，返回预期是否应该成功
    T → True（正向操作符合预期）
    F → False（非法提交应该被拦截）
    """
    auto_code = case.get("自动化预期编码", "").strip().upper()
    if auto_code == "T":
        return True
    elif auto_code == "F":
        return False
    # 空值默认当成拦截用例
    return False


def get_case_info(case: dict):
    """统一提取所有要用的字段，减少重复代码"""
    case_id = case.get("用例编号", "")
    test_purpose = case.get("测试点/目的", "")
    step_text = case.get("测试步骤", "")
    expect_text = case.get("预期结果", "")
    input_raw = case.get("输入数据", "")
    input_dict = parse_input_str(input_raw)
    expect_success = resolve_case_expect(case)
    return case_id, test_purpose, step_text, expect_text, input_dict, expect_success