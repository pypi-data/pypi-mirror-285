# submodule2/module4.py
# -*- coding: utf-8 -*-
import pandas as pd
from robot.api.deco import keyword

class XExcal:
    
    @keyword("XLog Excel Data")
    def log_excel_data(self, file_path, sheet_name, range_name=None):
        """
        Log ข้อมูลจากไฟล์ Excel

        ***|    Parameters     |***
            - **`file_path`**  พาธของไฟล์ Excel ที่ต้องการอ่าน
            - **`sheet_name`**  ชื่อของแผ่นงานที่ต้องการอ่านข้อมูล
            - **`range_name`**  ช่วงข้อมูลที่ต้องการอ่าน (เช่น 'A1:D5').
        """
        data = self._read_excel_data(file_path, sheet_name, range_name)
        self.log_tree_data(data)
        
    def _read_excel_data(self, file_path, sheet_name, range_name=None):
        """
        อ่านข้อมูลจากไฟล์ Excel

        ***|    Parameters     |***
            - **`file_path`**  พาธของไฟล์ Excel ที่ต้องการอ่าน
            - **`sheet_name`**  ชื่อของแผ่นงานที่ต้องการอ่านข้อมูล
            - **`range_name`**  ช่วงข้อมูลที่ต้องการอ่าน (เช่น 'A1:D5').

        ***|    Returns     |***
            - **`data`**  ข้อมูลทั้งหมดในรูปแบบ List ของ Dictionary.
        """
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        if range_name:
            df = self._filter_range(df, range_name)
        
        return df.to_dict(orient='records')

    def _filter_range(self, df, range_name):
        """
        ฟังก์ชันสำหรับกรองข้อมูลตามช่วงที่กำหนดใน Excel
        
        ***|    Parameters     |***
            - **`df`**  DataFrame ที่ต้องการกรองข้อมูล
            - **`range_name`**  ช่วงข้อมูลที่ต้องการอ่าน (เช่น 'A1:D5').

        ***|    Returns     |***
            - **`df`**  DataFrame ที่กรองข้อมูลแล้ว.
        """
        # Split the range_name to get the start and end cells
        start_cell, end_cell = range_name.split(':')
        start_row, start_col = self._cell_to_rowcol(start_cell)
        end_row, end_col = self._cell_to_rowcol(end_cell)
        
        # Convert columns to numbers and filter DataFrame
        filtered_df = df.iloc[start_row-1:end_row, start_col-1:end_col]
        return filtered_df

    def _cell_to_rowcol(self, cell):
        """
        ฟังก์ชันสำหรับแปลงชื่อเซลล์ Excel เป็นเลขแถวและเลขคอลัมน์
        
        ***|    Parameters     |***
            - **`cell`**  ชื่อเซลล์ (เช่น 'A1').

        ***|    Returns     |***
            - **`row`**  เลขแถว
            - **`col`**  เลขคอลัมน์
        """
        col_str = ''.join(filter(str.isalpha, cell))
        row_str = ''.join(filter(str.isdigit, cell))
        row = int(row_str)
        col = self._col_to_num(col_str)
        return row, col

    def _col_to_num(self, col_str):
        """
        ฟังก์ชันสำหรับแปลงชื่อคอลัมน์ Excel เป็นเลขคอลัมน์
        
        ***|    Parameters     |***
            - **`col_str`**  ชื่อคอลัมน์ (เช่น 'A').

        ***|    Returns     |***
            - **`num`**  เลขคอลัมน์
        """
        num = 0
        for c in col_str:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
        return num