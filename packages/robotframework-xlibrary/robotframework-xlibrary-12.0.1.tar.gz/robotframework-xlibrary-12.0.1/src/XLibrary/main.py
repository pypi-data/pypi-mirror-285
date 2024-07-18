#XpiumLibraryFlutter/main.py
# -*- coding: utf-8 -*-
from robot.api.deco import keyword

class MainClass:
    @keyword("Print Welcome Message")
    def print_welcome_message(self):
        """ พิมพ์ข้อความ 'Hello again!' ลงในคอนโซล """
        print("Welcome to XpiumLibraryFlutter")