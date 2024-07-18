# submodule2/module3.py
# -*- coding: utf-8 -*-
from robot.api.deco import keyword
import requests

class XGoogleSheet:
    @keyword("XLog Data Google Sheet")
    def log_data_google_sheet(self, api_key, spreadsheet_id, data_row_number):
        """
        Log ข้อมูลจาก Google Sheets โดยใช้ TileRow A1:V1 เป็น Title และแสดงข้อมูลแถวที่ระบุ

        ***|    Parameters     |***
            - **`api_key`**  API Key สำหรับเข้าถึง Google Sheets API.
            - **`spreadsheet_id`**  ID ของ Google Spreadsheet.
            - **`data_row_number`**  หมายเลขแถวข้อมูลที่ต้องการแสดง (เช่น 10).

        ***|    Returns     |***
            - **`data_dict`**  ข้อมูลในรูปแบบ dictionary ที่จับคู่ headers กับ data row.
        """
        title_range = "Sheet1!A1:V1"
        data_range = f"Sheet1!A{data_row_number}:V{data_row_number}"

        # Read the title row
        titles = self._read_google_sheet_data(api_key, spreadsheet_id, title_range)
        # Read the data row
        data = self._read_google_sheet_data(api_key, spreadsheet_id, data_range)

        if not titles or not data:
            print("No data found.")
            return None

        headers = titles[0]
        row = data[0]

        # Create a dictionary to match headers with row data
        data_dict = dict(zip(headers, row))
        
        self._log_row_data(headers, row)
        
        return data_dict

    def _read_google_sheet_data(self, api_key, spreadsheet_id, range_name):
        """
        อ่านข้อมูลจาก Google Sheets

        ***|    Parameters     |***
            - **`api_key`**  API Key สำหรับเข้าถึง Google Sheets API.
            - **`spreadsheet_id`**  ID ของ Google Spreadsheet.
            - **`range_name`**  ช่วงข้อมูลที่ต้องการอ่าน (เช่น 'Sheet1!A1:D5').

        ***|    Returns     |***
            - **`data`**  ข้อมูลทั้งหมดในรูปแบบ List ของ Dictionary.
        """
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}"
        params = {"key": api_key}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('values', [])

    def _log_row_data(self, headers, row):
        """
        ฟังก์ชันสำหรับแสดงข้อมูลในรูปแบบ Tree Structure โดยจับคู่ Title กับข้อมูล

        ***|    Parameters     |***
            - **`headers`**  ชื่อคอลัมน์ (Title).
            - **`row`**  ข้อมูลแถวที่ต้องการแสดง.
        """
        for j, cell in enumerate(row):
            print(f"├── [{j}]")
            print(f"│   ├── {headers[j]} : {cell}")
