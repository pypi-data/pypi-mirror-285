# submodule2/module1.py
# -*- coding: utf-8 -*-
import logging
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger

class XLog:
    def __init__(self):
        # กำหนดค่าเริ่มต้นของการบันทึก Log
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.builtin = BuiltIn()

    def _log_tree_structure(self, data, level=0, prefix=''):
        """
        ฟังก์ชันช่วยสำหรับการแสดงโครงสร้างข้อมูลในรูปแบบต้นไม้ (Tree Structure)
        
        พารามิเตอร์:
        - data: ข้อมูลที่ต้องการแสดง
        - level: ระดับของการแสดงผล (ใช้สำหรับการจัดเรียง)
        - prefix: คำนำหน้าข้อมูล (ถ้ามี)
        """
        indent = "│   " * level
        branch = "├── " if level > 0 else ""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    logging.info(f"{indent}{branch}{key}")
                    self._log_tree_structure(value, level + 1)
                else:
                    logging.info(f"{indent}{branch}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                logging.info(f"{indent}├── [{i}]")
                self._log_tree_structure(item, level + 1)
        else:
            logging.info(f"{indent}{branch}{prefix}{data}")

    @keyword("XLog Tree Data")
    def log_tree_data(self, data):
        """ 
        ***|    Description     |***
        |   *`XLog Tree Data`*   |   เป็น Keyword สำหรับ Log Data ให้ออกมาเป็น Tree Data |


        ***|    Example     |***
        | *`XLog Tree Data`* | *`${value}`* |
        

        ***|    Parameters     |***
        - **`data`**: ข้อมูล JSON.

        
        *`Create By Tassana Khrueawan`*
        """
        # เรียกใช้ฟังก์ชัน _log_tree_structure เพื่อแสดงโครงสร้างข้อมูลในรูปแบบต้นไม้
        self._log_tree_structure(data)

