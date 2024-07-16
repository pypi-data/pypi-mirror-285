# -*- coding: utf-8 -*-
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from AppiumFlutterLibrary.finder import ElementFinder
import json
import requests
import logging


class XAppiumFlutter:
    def __init__(self):
        super().__init__()
        self._bi = BuiltIn()
        self.finder = ElementFinder()

    @keyword('XQuit Application')
    def quit_application(self):
        """
        ***|    Description     |***
        |   *`XQuit Application`*   |   ปิดแอปพลิเคชันปัจจุบันและปิดเซสชัน |

        
        ***|    Example     |***
        | *`XQuit Application`* |

        
        ***|    Parameters     |***
        - ไม่มีพารามิเตอร์

        *`Create By Tassana Khrueawan`*
        """
        # ดึงอินสแตนซ์ของแอปพลิเคชันปัจจุบัน
        driver = self._current_application()
        # ปิด driver ซึ่งจะทำให้แอปพลิเคชันปิดลงและสิ้นสุดเซสชัน
        driver.quit()

    @keyword('XSwitch Context Mode')
    def switch_context_mode(self, mode):
        """
        ***|    Description     |***
        |   *`Switch Context Mode`*   |   สลับโหมดคอนเทคซ์ไปยัง NATIVE_APP หรือ FLUTTER |

        
        ***|    Example     |***
        | *`XSwitch Context Mode`* | *`NATIVE`* |
        | *`XSwitch Context Mode`* | *`FLUTTER`* |

        
        ***|    Parameters     |***
        - **`mode`**: โหมดคอนเทคซ์ที่ต้องการสลับไป, สามารถเป็น 'NATIVE' หรือ 'FLUTTER'.

        *`Create By Tassana Khrueawan`*
        """
        # ดึงอินสแตนซ์ของแอปพลิเคชันปัจจุบัน
        driver = self._current_application()
        # สลับโหมดคอนเทคซ์ตามพารามิเตอร์ที่ได้รับ
        if mode == 'NATIVE':
            driver.switch_to.context('NATIVE_APP')
            print("Context switched to NATIVE_APP (โหมด NATIVE_APP).")
        elif mode == 'FLUTTER':
            driver.switch_to.context('FLUTTER')
            print("Context switched to FLUTTER (โหมด FLUTTER).")
        else:
            print(f"Invalid mode: {mode}. Please use 'NATIVE' or 'FLUTTER'. (โหมดไม่ถูกต้อง: {mode}. กรุณาใช้ 'NATIVE' หรือ 'FLUTTER').")

    def _current_application(self):
        """
        ***|    Description     |***
        |   *`_current_application`*   |   คืนค่าอินสแตนซ์ของแอปพลิเคชันปัจจุบัน |


        ***|    Parameters     |***
        - ไม่มีพารามิเตอร์

        *`Create By Tassana Khrueawan`*
        """
        # ดึงและคืนค่าอินสแตนซ์ของแอปพลิเคชันปัจจุบันจาก AppiumFlutterLibrary
        return self._bi.get_library_instance('AppiumFlutterLibrary')._current_application()
    
    @keyword("XGet Session ID")
    def xget_session_id(self):
        """
        ***|    Description     |***
        |   *`get_appium_session_id`*   |   คืนค่า session_id ของแอปพลิเคชันปัจจุบัน |

        ***|    Parameters     |***
        - ไม่มีพารามิเตอร์

        *`Create By Tassana Khrueawan`*
        """
        driver = self._current_application()
        session_id = driver.session_id
        return session_id

    @keyword("XSwipe")
    def swipe_on_screen(self, start_x, start_y, end_x, end_y, duration=800):
        """
        ***|    Description     |***
        |   *`Swipe on Screen`*   |   ทำการเลื่อนหน้าจอจากจุดหนึ่งไปยังจุดหนึ่งในเวลาที่กำหนด และสลับคอนเทคซ์จาก NATIVE_APP กลับไปยัง FLUTTER  |

        
        ***|    Example     |***
        | *`Swipe on Screen`* | *`start_x`* | *`start_y`* | *`end_x`* | *`end_y`* | *`duration`* |

        
        ***|    Parameters     |***
        - **`start_x`**  ค่าพิกัด X ที่จุดเริ่มต้น.
        - **`start_y`**  ค่าพิกัด Y ที่จุดเริ่มต้น.
        - **`end_x`**    ค่าพิกัด X ที่จุดสิ้นสุด.
        - **`end_y`**    ค่าพิกัด Y ที่จุดสิ้นสุด.
        - **`duration`** ระยะเวลาของการเลื่อนหน้าจอในหน่วยมิลลิวินาที.

        *`Create By Tassana Khrueawan`*
        """
        # ดึงอินสแตนซ์ของแอปพลิเคชันปัจจุบัน
        driver = self._current_application()
        # เก็บคอนเทคซ์เดิม
        original_context = driver.current_context
        try:
            # สลับไปยังคอนเทคซ์ NATIVE_APP
            driver.switch_to.context('NATIVE_APP')
            # ทำการเลื่อนหน้าจอจากจุดเริ่มต้นไปยังจุดสิ้นสุดในเวลาที่กำหนด
            driver.swipe(start_x, start_y, end_x, end_y, duration)
        finally:
            # สลับกลับไปยังคอนเทคซ์ FLUTTER
            driver.switch_to.context('FLUTTER')

    @keyword("XGet Window Height")
    def get_window_height(self):
        """
        ***|    Description     |***
        |   *`Get Window Height`*   |   คืนค่าความสูงของหน้าต่างแอปพลิเคชันในคอนเทคซ์ native และสลับกลับไปยัง Flutter |

        
        ***|    Example     |***
        | *`${height}`* | *`Get Window Height`* |
        | *`Log`* | *`Window height: ${height}`* |

        
        ***|    Parameters     |***
        - ไม่มีพารามิเตอร์

        *`Create By Tassana Khrueawan`*
        """
        # ดึงอินสแตนซ์ของแอปพลิเคชันปัจจุบัน
        driver = self._current_application()
        # เก็บคอนเทคซ์เดิม
        original_context = driver.current_context
        try:
            # สลับไปยังคอนเทคซ์ NATIVE_APP
            driver.switch_to.context('NATIVE_APP')
            # ดึงค่าความสูงของหน้าต่างแอปพลิเคชัน
            height = driver.get_window_size()['height']
            return height
        finally:
            # สลับกลับไปยังคอนเทคซ์ FLUTTER
            driver.switch_to.context('FLUTTER')

    @keyword("XGet Window Width")
    def get_window_width(self):
        """
        ***|    Description     |***
        |   *`Get Window Width`*   |   คืนค่าความกว้างของหน้าต่างแอปพลิเคชันในคอนเทคซ์ native และสลับกลับไปยัง Flutter |

        
        ***|    Example     |***
        | *`${width}`* | *`Get Window Width`* |
        | *`Log`* | *`Window width: ${width}`* |

        
        ***|    Parameters     |***
        - ไม่มีพารามิเตอร์

        *`Create By Tassana Khrueawan`*
        """
        # ดึงอินสแตนซ์ของแอปพลิเคชันปัจจุบัน
        driver = self._current_application()
        # เก็บคอนเทคซ์เดิม
        original_context = driver.current_context
        try:
            # สลับไปยังคอนเทคซ์ NATIVE_APP
            driver.switch_to.context('NATIVE_APP')
            # ดึงค่าความกว้างของหน้าต่างแอปพลิเคชัน
            width = driver.get_window_size()['width']
            return width
        finally:
            # สลับกลับไปยังคอนเทคซ์ FLUTTER
            driver.switch_to.context('FLUTTER')

    @keyword("XSend Status To BrowserStack")
    def send_status_to_browserstack(self):
        """
        ***|    Description     |***
        |   *`XSend Status To BrowserStack`*   |   ส่งสถานะและข้อความไปยัง BrowserStack ตาม session_id, status, และ message ที่กำหนด |

        ***|    Example     |***
        | *`XSend Status To BrowserStack`* |

        ***|    Parameters     |***
        - ไม่มีพารามิเตอร์

        *`Create By Tassana Khrueawan`*
        """
        # ประกาศค่า variables ที่ใช้ในการเชื่อมต่อกับ BrowserStack
        BROWSERSTACK_USERNAME = 'juralakp_p2Vx0U'
        BROWSERSTACK_ACCESS_KEY = 'PPed2Tj3ZNZqaGw6kLyw'
        BROWSERSTACK_URL = f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"

        # ดึงค่า session_id จากตัวแปรของ Robot Framework
        session_id = BuiltIn().get_variable_value("${SESSION_ID}")

        # ดึงค่า TEST STATUS และ TEST MESSAGE จาก Robot Framework
        test_status = BuiltIn().get_variable_value("${TEST STATUS}")
        test_message = BuiltIn().get_variable_value("${TEST MESSAGE}")

        # ถ้า TEST STATUS หรือ TEST MESSAGE เป็น None ให้ดึงข้อมูลจาก get_variables
        if not test_status or not test_message:
            variables = BuiltIn().get_variables()
            test_status = variables.get("${TEST STATUS}", "FAIL")
            test_message = variables.get("${TEST MESSAGE}", "")

        # ตรวจสอบค่า test_status และ test_message
        logging.info(f"Test Status: {test_status}")
        logging.info(f"Test Message: {test_message}")

        # กำหนดสถานะการทดสอบเป็น "passed" ถ้าผลลัพธ์คือ "PASS" มิฉะนั้นจะเป็น "failed"
        status = "passed" if test_status == "PASS" else "failed"

        # กำหนดข้อความเป็น "PASS" ถ้าสถานะคือ "passed" มิฉะนั้นจะใช้ข้อความจาก test_message
        message = "PASS" if status == "passed" else test_message

        # Log the status and message for debugging
        logging.info(f"Sending to BrowserStack: status={status}, message={message}")

        # สร้าง URL สำหรับการส่งคำขอไปยัง BrowserStack
        url = f"{BROWSERSTACK_URL}/session/{session_id}/execute"

        # สร้าง payload ในรูปแบบ JSON ที่จะส่งไปยัง BrowserStack
        payload = json.dumps({
            "script": f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status": "{status}", "reason": "{message}"}}}}',
            "args": []
        })

        # ตั้งค่า headers สำหรับคำขอ HTTP POST
        headers = {
            'Content-Type': 'application/json'
        }

        # ส่งคำขอ HTTP POST ไปยัง BrowserStack
        response = requests.post(url, headers=headers, data=payload)

        # ตรวจสอบสถานะการตอบกลับและบันทึกข้อมูล
        if response.status_code == 200:
            logging.info(f"Successfully sent status to BrowserStack: {status}, {message}")
        else:
            logging.error(f"Failed to send status to BrowserStack: {response.status_code}, {response.content}")