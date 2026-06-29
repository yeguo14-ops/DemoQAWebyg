'''
解析 Excel「输入数据」字段，支持中英文分号、(空)转空字符串、键值对拆分
'''


def parse_input_str(input_str):
    """解析Excel输入数据字段，返回键值对字典"""
    parsed_data = {}
    if not input_str or input_str.strip() == "无":
        return parsed_data

    # 处理换行、回车
    cleaned_str = input_str.replace('\n', '').replace('\r', '').strip()
    # 按中英文分号拆分
    parts = cleaned_str.split('；') if '；' in cleaned_str else cleaned_str.split(';')

    for part in parts:
        part = part.strip()
        if not part:
            continue
        # 按中英文冒号拆分键值
        if '：' in part:
            key, value = part.split('：', 1)
        elif ':' in part:
            key, value = part.split(':', 1)
        else:
            continue

        key = key.strip()
        value = value.strip()
        # 处理(空)值
        if value == '(空)':
            value = ''
        parsed_data[key] = value

    return parsed_data