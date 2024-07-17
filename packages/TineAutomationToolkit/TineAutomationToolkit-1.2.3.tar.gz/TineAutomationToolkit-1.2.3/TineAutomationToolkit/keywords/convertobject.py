# -*- coding: utf-8 -*-
import bson
import logging
import pytz
import re
import base64
import json

from datetime import datetime

class ConvertObject:

    def __init__(self):
        #เนื่องจากปัญหาเรื่องโครงสร้าง structure เลยยังไม่สามารถใช้ได้
        # self._bi = BuiltIn()
        pass

    #KeyWord

    def convert_bson_to_json(self, bson_data):
        """ Owner : tassana.k@epic-consulting.net
        Convert BSON data to a Python object (dictionary or list) 
        without converting it to a JSON string.

        ==========================================================

        แปลงข้อมูล BSON เป็นอ็อบเจกต์ Python (dictionary หรือ list) 
        โดยไม่ต้องแปลงเป็นสตริง JSON
        """
        try:
            if isinstance(bson_data, bytes):
                bson_data = bson.loads(bson_data)
            # Convert BSON directly to a Python object without converting to a JSON string
            return bson_data  # This returns a Python dictionary or list of dictionaries
        except Exception as e:
            return f"Failed to convert BSON to JSON object: {str(e)}"

    def log_tree_structure_data(self, data):
        """ Owner : tassana.k@epic-consulting.net
        ***|    Description     |***
        |   *`Log Tree Data`*   |   เป็น Keyword สำหรับ Log Data ให้ออกมาเป็น Tree Data |

        ***|    Example     |***
        | *`Log Tree Data`* | *`${value}`* |
        
        ***|    Parameters     |***
            - **`data`**  ข้อมูล Json.
        """
        self._tree_structure(data)

    def convert_time_to_local_timezone(self,date,timezone='Asia/Bangkok'):
        """ Owner : suthasinee.k@arcadiaapm.com
        ***|    Description     |***
        |   มีไว้สำหรับรับเวลาที่ได้มาแล้วแปลงเป็นเวลาของ TimeZone 
        |   โดย Default คือ Asia/Bangkok
        """
        # กำหนด timezone เป็น UTC
        utc_timezone = pytz.timezone('UTC')
        # แปลง timezone จาก UTC เป็น local timezone
        local_timezone = pytz.timezone(timezone)  
        # ตรวจสอบว่าข้อมูลนำเข้าเป็น datetime object หรือไม่
        if isinstance(date, datetime):
            date_time = date
            local_date_time = utc_timezone.localize(date).astimezone(local_timezone)
        else:
            # ตรวจสอบว่าข้อมูลนำเข้าเป็นรูปแบบที่ถูกต้องหรือไม่
            if not self._is_valid_iso_format(date):
                raise ValueError("Invalid date format. Please provide the date in the format 'YYYY-MM-DDTHH:MM:SS.sss+HH:MM'")
        
            # แปลง string เป็น datetime object
            date_time = datetime.fromisoformat(date)
            local_date_time = date_time.astimezone(local_timezone)
        
        return local_date_time
    
    #(ยังใช้ไม่ได้อยู่ในช่วงทดสอบ)
    def convert_get_render_tree_to_json(self,tree):
        """ Owner : pornpawit.s@chareontut.co.th
        ***|    Description     |***
        |   มีไว้สำหรับนำข้อมูล get render tree แปลง
        |   เป็น json (ยังใช้ไม่ได้อยู่ในช่วงทดสอบ)
        """
        # แปลงข้อมูล Render Tree เป็น JSON
        render_tree_json = json.dumps(tree, indent=4)
        with open('render_tree.json', 'w') as json_file:
            json_file.write(render_tree_json)
        
        with open('render_tree.json', 'r') as json_file:
            data = json.load(json_file)
            print(data)
        


    #Private Function

    def _tree_structure(self, data, level=0, prefix=''):
        indent = "│   " * level
        branch = "├── " if level > 0 else ""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    logging.info(f"{indent}{branch}{key}")
                    self._tree_structure(value, level + 1)
                else:
                    logging.info(f"{indent}{branch}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                logging.info(f"{indent}├── [{i}]")
                self._tree_structure(item, level + 1)
        else:
            logging.info(f"{indent}{branch}{prefix}{data}")

    def _is_valid_iso_format(self,date_str):
        """ Owner : suthasinee.k@arcadiaapm.com
        ***|    Description     |***
        | 
        """
        pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{2}:\d{2}$')
        return bool(pattern.match(date_str))