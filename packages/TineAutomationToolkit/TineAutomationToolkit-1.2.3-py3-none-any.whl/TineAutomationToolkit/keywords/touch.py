# -*- coding: utf-8 -*-
from .connectionmanagement import ConnectionManagement

cache_app = ConnectionManagement()

class Touch():

    def __init__(self):
        #เนื่องจากปัญหาเรื่องโครงสร้าง structure เลยยังไม่สามารถใช้ได้
        pass


    def native_tap_with_positions(self, duration=500, *locations):
        """Taps on a particular place with up to five fingers, holding for a
        certain time

        Args:
        - locations - an array of tuples representing the x/y coordinates of
                the fingers to tap. Length can be up to five.
        - duration - length of time to tap, in ms. Default: 500ms

        Example:
        |  @{firstFinger}   |  create list  |  ${100}  |  ${500}  |
        |  @{secondFinger}  |  create list  |${700}    |  ${500}  |
        |  @{fingerPositions}  |  create list  |  ${firstFinger}  |  ${secondFinger}  |
        |  Sleep  |  1  |
        |  Tap with Positions  |  ${1000}  |  @{fingerPositions}  |

        ============================================================

        แตะบนจุดที่ระบุด้วยนิ้วมือสูงสุดถึงห้านิ้ว โดยกดค้างไว้เป็นระยะเวลาหนึ่ง

        อาร์กิวเมนต์:
        - locations - อาร์เรย์ของทูเพิลแสดงพิกัด x/y ของนิ้วที่จะแตะ ความยาวสามารถเป็นได้ถึงห้า
        - duration - ระยะเวลาในการแตะ, เป็นมิลลิวินาที ค่าเริ่มต้น: 500 มิลลิวินาที

        ตัวอย่าง:
        |  @{firstFinger}   |  สร้างรายการ  |  ${100}  |  ${500}  |
        |  @{secondFinger}  |  สร้างรายการ  |${700}    |  ${500}  |
        |  @{fingerPositions}  |  สร้างรายการ  |  ${firstFinger}  |  ${secondFinger}  |
        |  หลับ  |  1  |
        |  แตะด้วยตำแหน่ง  |  ${1000}  |  @{fingerPositions}  |
        """
        driver = cache_app._current_application()
        driver.tap(positions=list(locations), duration=duration)