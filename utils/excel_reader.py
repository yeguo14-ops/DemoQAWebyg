# utils/excel_reader.py
import openpyxl
import re


class ExcelReader:
    """读取Excel测试数据的工具类"""

    def __init__(self, file_path, sheet_name):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.workbook = openpyxl.load_workbook(file_path, data_only=True)
        self.sheet = self.workbook[sheet_name]

    def get_test_data(self):
        """
        获取所有测试数据，返回字典列表
        第一行作为表头，从第二行开始作为数据
        """
        rows = list(self.sheet.iter_rows(values_only=True))
        if not rows:
            return []

        # 第一行作为表头
        headers = rows[0]
        # 从第二行开始是数据
        data_rows = rows[1:]

        test_data_list = []
        for row in data_rows:
            # 跳过完全为空的行
            if not row or not any(cell is not None and str(cell).strip() != '' for cell in row):
                continue

            # 如果第一个单元格（用例编号）为空，也跳过
            if not row[0] or str(row[0]).strip() == '':
                continue

            row_dict = {}
            for i, header in enumerate(headers):
                if header is None:
                    continue
                # 取当前行的对应列值
                value = row[i] if i < len(row) else ''
                # 清理数据：去除换行符、多余空格
                if isinstance(value, str):
                    # 将换行符替换为正常分隔符，合并为一行
                    value = value.replace('\n', '').replace('\r', '').strip()
                row_dict[str(header).strip()] = value

            test_data_list.append(row_dict)

        return test_data_list