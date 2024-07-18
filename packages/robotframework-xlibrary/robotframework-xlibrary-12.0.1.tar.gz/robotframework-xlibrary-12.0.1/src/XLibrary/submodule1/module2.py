#submodule1/module2.py
# -*- coding: utf-8 -*-
from robot.api.deco import keyword
import ast
import pymongo
import logging
import bson
import json



class XMongoDB:

    def __init__(self):
        self._dbconnection = None

    @keyword("XConnect Mongodb With URL")
    def connect_to_mongodb_with_uri(self, dbURI, timeout=10):
        """
        ***|    Description     |***
        | *`Connect Mongodb With URL`* | เป็น Keyword ไว้เชื่อมต่อกับ MongoDB โดยใช้ URI โดยเฉพาะ |

            
        ***|    Example     |***
        | *`Connect Mongodb With URL`* | *`mongodb+srv://username:password@host`* | *`timeout=10`* |
            

        ***|    Parameters     |***
        - **`dbURI`**: URL สำหรับการเชื่อมต่อไปยัง MongoDB.
        - **`timeout`**: ตั้งเวลา TimeOut ในการเชื่อมต่อไปยัง MongoDB.

            
        *`Create By Tassana Khrueawan`*
        """
        try:
            # สร้างการเชื่อมต่อกับ MongoDB โดยใช้ URI และตั้งเวลา timeout
            self._dbconnection = pymongo.MongoClient(dbURI, serverSelectionTimeoutMS=timeout*1000)
            # ตรวจสอบการเชื่อมต่อ
            self._dbconnection.server_info()
            logging.debug("| Succeed: เชื่อมต่อกับ MongoDB โดยใช้ URI | %s |" % dbURI)
        except pymongo.errors.ServerSelectionTimeoutError as e:
            logging.error("| Fail: การเชื่อมต่อ MongoDB ล้มเหลว เนื่องจาก TimeOut | %s |" % str(e))
            raise Exception("การเชื่อมต่อ MongoDB ล้มเหลว เนื่องจาก TimeOut")
        except Exception as e:
            logging.error("| Fail: การเชื่อมต่อ MongoDB ล้มเหลว | %s |" % str(e))
            raise Exception("การเชื่อมต่อ MongoDB ล้มเหลว: " + str(e))

    @keyword("XQuery MongoDB")
    def query_mongodb(self, database_name, collection_name, query, limit=None, sort=None):
        """
        ***|    Description     |***
        |   *`Query MongoDB`*   |   เป็น Keyword สำหรับ Query ข้อมูลใน Collection พร้อมกับการกำหนดจำนวนข้อมูลสูงสุดและการเรียงลำดับข้อมูล. สำหรับการเรียงลำดับข้อมูล, คุณต้องสร้าง list ของ string และแปลงเป็น tuple ในฟังก์ชัน Python ของคุณ.|
        
        ***|    Example     |***
        | *`${result}`* | *`Query MongoDB`* | *`database_name`* | *`collection_name`* | *`Command Query`* | *`limit=5`* | *`sort=_id,-1`* |
        | *`Log`* | *`${result}`* |
        
        ***|    Parameters     |***
        - **`database_name`**: ชื่อของฐานข้อมูล.
        - **`collection_name`**: ชื่อของ collection.
        - **`query`**: คำสั่ง Query.
        - **`limit`**: (Optional) จำนวนข้อมูลสูงสุดที่ต้องการส่งกลับ.
        - **`sort`**: (Optional) ลำดับข้อมูล ตัวอย่างเช่น _id,-1 (แทนที่ "_id" คือ field ที่ต้องการเรียงลำดับ และ "-1" คือ การเรียงลำดับจากมากไปน้อย, "1" คือ การเรียงลำดับจากน้อยไปมาก).
        
        *`Create By Tassana Khrueawan`*
        """
        # ดึง collection ที่ต้องการจากฐานข้อมูล
        collection = self._dbconnection[database_name][collection_name]
        # แปลงคำสั่ง Query จาก string เป็น dictionary
        query_dict = ast.literal_eval(query)
        # เริ่มการ Query ข้อมูล
        cursor = collection.find(query_dict)
        
        # ถ้ามีการกำหนดลำดับข้อมูล
        if sort:
            sort_field, sort_order = sort.split(',')
            sort = [(sort_field, int(sort_order))]
            cursor = cursor.sort(sort)
        
        # ถ้ามีการกำหนดจำนวนข้อมูลสูงสุด
        if limit:
            cursor = cursor.limit(int(limit))
        
        # ส่งคืนผลลัพธ์ในรูปแบบ list
        results = list(cursor)
        return results

    @keyword("XQuery Dynamic Value")
    def query_dynamic_value(self, result, field='None', value='None', expect=None):
        """
        ***|    Description     |***
        |   *`XQuery Dynamic Value`*   |   เป็น Keyword สำหรับ Query ข้อมูลใน Collection แบบเจาะลงไป |
 
       
        ***|    Example     |***
        | *`${arpu_value}`* | *`XQuery Dynamic Value`* | *`result`* | *`productCharacteristic`* | *`name`* | *`arpu`* |
        | *`Log`* | *`${arpu_value}`* |
 
       
        ***|    Parameters     |***
        - **`result`**  ผลลัพธ์ของการ Query ที่เป็นรายการข้อมูลจาก MongoDB.
        - **`field`**   ชื่อฟิลด์ในข้อมูลที่ต้องการเจาะลงไป.
        - **`value`**   ชื่อคีย์ภายในฟิลด์ที่ต้องการเข้าถึง.
        - **`expect`**  ค่าที่ต้องการเทียบเพื่อหาข้อมูลที่ตรงกับเงื่อนไข.
 
 
        *`Create By Tassana Khrueawan`*
        """
        for item in result:
            if field in item and isinstance(item[field], list):
                if expect:
                    for char in item[field]:
                        if char.get(value) == expect:
                            return char.get('value')
                else:
                    return item[field]
        return None
 
    @keyword("XQuery Specific Value")
    def query_specific_value(self, result, field_name=None):
        """
        ***|    Description     |***
        |   XQuery Specific Value   |   Keyword สำหรับ Query ข้อมูลใน Collection แบบไม่เจาะลงไป |
 
       
        ***|    Example     |***
        | *`${name}`* | *`XQuery Specific Value`* | *`result`* | *`name`* |
        | *`Log`* | *`${name}`* |
 
 
        ***|    Parameters     |***
        - **`result`**  ผลลัพธ์ของการ Query ที่เป็นรายการข้อมูลจาก MongoDB.
        - **`field_name`**   ชื่อฟิลด์ที่ต้องการเข้าถึงเพื่อค้นหาค่าภายใน.
 
 
        *`Create By Tassana Khrueawan`*
        """
        if not field_name:
            return result
 
        results = []
        if isinstance(result, list):
            for doc in result:
                if isinstance(doc, dict) and field_name in doc:
                    results.append(doc[field_name])
        else:
            results = result.get(field_name, None)
 
        return results  

    @keyword("XConvert BSON Document to JSON Object")
    def bson_to_json_object(self, bson_data):
        """
        ***|    Description     |***
        |   *`Convert BSON Document to JSON Object`*   |   แปลงข้อมูล BSON เป็นอ็อบเจกต์ Python (dictionary หรือ list) โดยไม่ต้องแปลงเป็นสตริง JSON |

        
        ***|    Example     |***
        | *`${json_object}`* | *`Convert BSON Document to JSON Object`* | *`${bson_data}`* |
        

        ***|    Parameters     |***
        - **`bson_data`**: ข้อมูล BSON ในรูปแบบไบต์สตริงหรือดิกชันนารี.

        
        ***|    Returns     |***
        - อ็อบเจกต์ Python ซึ่งอาจเป็นดิกชันนารีหรือลิสต์ของดิกชันนารีที่แสดงถึงข้อมูล BSON.

        
        *`Create By Tassana Khrueawan`*
        """
        try:
            # ตรวจสอบว่าข้อมูล BSON เป็นไบต์สตริง
            if isinstance(bson_data, bytes):
                bson_data = bson.loads(bson_data)
            # แปลงข้อมูล BSON เป็นอ็อบเจกต์ Python โดยตรง
            return bson_data  # คืนค่าเป็น Python dictionary หรือ list ของ dictionary
        except Exception as e:
            return f"Failed to convert BSON to JSON object: {str(e)}"
        
    @keyword("XCreate JSON String")
    def create_json_string(self, status, reason):
        """
        ***|    Description     |***
        |   *`XCreate JSON String`*   |   สร้าง JSON สตริงสำหรับการตั้งสถานะของเซสชั่นใน BrowserStack โดยการรับสถานะและเหตุผล |

        
        ***|    Example     |***
        | *`${json_string}`* | *`XCreate JSON String`* | *`passed`* | *`Test completed successfully`* |
        

        ***|    Parameters     |***
        - **`status`**: สถานะของเซสชั่น เช่น "passed" หรือ "failed".
        - **`reason`**: เหตุผลที่ตั้งสถานะนี้ เช่น "Test completed successfully".

        
        ***|    Returns     |***
        - JSON สตริงที่มีข้อมูลเกี่ยวกับการตั้งสถานะของเซสชั่นใน BrowserStack.

        
        *`Create By Tassana Khrueawan`*
        """
        try:
            data = {
                "script": f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status": "{status}", "reason": "{reason}"}}}}',
                "args": []
            }
            return json.dumps(data)
        except Exception as e:
            return f"Failed to create JSON string: {str(e)}"
