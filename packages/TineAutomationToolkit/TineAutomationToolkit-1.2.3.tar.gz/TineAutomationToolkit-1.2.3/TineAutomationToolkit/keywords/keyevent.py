# -*- coding: utf-8 -*-
from .connectionmanagement import ConnectionManagement

cache_app = ConnectionManagement()

class KeyEvent():

    def __init__(self):
        #เนื่องจากปัญหาเรื่องโครงสร้าง structure เลยยังไม่สามารถใช้ได้
        pass

    def native_press_keycode(self, keycode, metastate=None):
        """Sends a press of keycode to the device.

        Android only.

        Possible keycodes & meta states can be found in
        http://developer.android.com/reference/android/view/KeyEvent.html

        Meta state describe the pressed state of key modifiers such as
        Shift, Ctrl & Alt keys. The Meta State is an integer in which each
        bit set to 1 represents a pressed meta key.

        For example
        - META_SHIFT_ON = 1
        - META_ALT_ON = 2

        | metastate=1 --> Shift is pressed
        | metastate=2 --> Alt is pressed
        | metastate=3 --> Shift+Alt is pressed

         - _keycode- - the keycode to be sent to the device
         - _metastate- - status of the meta keys

        ============================================================

        ฟังก์ชันที่ใช้สำหรับการส่งการกดปุ่มคีย์โค้ดไปยังอุปกรณ์ Android ในการทดสอบอัตโนมัติด้วยเฟรมเวิร์ก Appium 
        ซึ่งเป็นเฟรมเวิร์กยอดนิยมสำหรับการทดสอบแอปพลิเคชันบนมือถือ

        - keycode: รหัสของปุ่มที่ต้องการกด รหัสเหล่านี้สามารถหาได้จากเอกสารของ Android ที่
          http://developer.android.com/reference/android/view/KeyEvent.html

        - metastate: สถานะของปุ่มตัวช่วยเช่น Shift, Ctrl, หรือ Alt 
        ซึ่งถูกแสดงด้วยตัวเลขที่แต่ละบิตที่ถูกตั้งค่าเป็น 1 แทนสถานะที่กดของปุ่มตัวช่วยนั้น ๆ
        """
        driver = cache_app._current_application()
        driver.press_keycode(keycode, metastate)