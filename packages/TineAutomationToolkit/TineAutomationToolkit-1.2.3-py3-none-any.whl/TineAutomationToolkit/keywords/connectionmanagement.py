# -*- coding: utf-8 -*-

import robot
import inspect
import logging
import json
import requests

from appium import webdriver
from robot.libraries.BuiltIn import BuiltIn
from TineAutomationToolkit.utils.applicationcache import ApplicationCache
from AppiumLibrary.keywords._logging import _LoggingKeywords

cache_app = BuiltIn()
method_cache_app = ApplicationCache()
log = _LoggingKeywords()

class ConnectionManagement:

    def __init__(self):
        #เนื่องจากปัญหาเรื่องโครงสร้าง structure เลยยังไม่สามารถใช้ได้
        # self._bi = BuiltIn()
        pass
    #KeyWord
    
    def native_close_application_session(self,alias=None):
        """Close Application And Quit Seesion

        =========================================================
        
        ปิดแอพปัจจุบันและปิดเซสชัน"""
        driver = self._current_application()
        log._debug('Closing application with session id %s' % self._current_application().session_id)
        method_cache_app.register(driver,alias)
        method_cache_app.close_all()

    def native_background_application(self, seconds=5):
        """
        Puts the application in the background on the device for a certain
        duration.

        =========================================================

        วางแอปพลิเคชันไว้ในพื้นหลังของอุปกรณ์เป็นระยะเวลาหนึ่ง.
        """
        self._current_application().background_app(seconds)
        
    def native_activate_application(self, app_id):
        """
        Activates the application if it is not running or is running in the background.
        Args:
         - app_id - BundleId for iOS. Package name for Android.

        New in AppiumLibrary v2

        =========================================================

        
        เปิดใช้งานแอปพลิเคชันหากมันไม่ได้รันอยู่หรือรันอยู่ในพื้นหลัง
        อาร์กิวเมนต์:
        - app_id - BundleId สำหรับ iOS, ชื่อแพ็คเกจสำหรับ Android.
        """
        self._current_application().activate_app(app_id)

    def native_terminate_application(self, app_id):
        """
        Terminate the given app on the device

        Args:
         - app_id - BundleId for iOS. Package name for Android.

        New in AppiumLibrary v2

        =========================================================
        
        ยุติแอปพลิเคชันที่กำหนดไว้บนอุปกรณ์แต่ยัง active อยู่ในระบบ
        สามารถเปิดต่อได้

        อาร์กิวเมนต์:  

        app_id - BundleId สำหรับ iOS, ชื่อแพ็คเกจสำหรับ Android.
        ใหม่ใน AppiumLibrary เวอร์ชัน 2
        """
        return self._current_application().terminate_app(app_id)
    
    def native_get_window_height(self):
        """Get current device height.

        Example:
        | ${width}       | Get Window Width |
        | ${height}      | Get Window Height |
        | Click A Point  | ${width}         | ${height} |

        New in AppiumLibrary 1.4.5
        """
        return self._current_application().get_window_size()['height']
    
    def native_get_window_width(self):
        """Get current device width.

        Example:
        | ${width}       | Get Window Width |
        | ${height}      | Get Window Height |
        | Click A Point  | ${width}          | ${height} |

        New in AppiumLibrary 1.4.5
        """
        return self._current_application().get_window_size()['width']
    
    def commond_install_app(self, app_path, app_package):
        """ *******Not available wait for update flutter*******
        Install App via Appium
        
        Android .

        - app_path - path to app (.apk)
        - app_package - package of install app to verify

        Ios .

        - app_path - path to app (.app | .ipa)
        - bundleId - package of install app to verify
        """
        driver = self._current_application()
        driver.install_app(app_path)
        return driver.is_app_installed(app_package)
    
    
    
    #PRIVATE_FUNCTION
        
    def _current_application(self):
        """Return the instance of the current application
        From AppiumFlutterLibrary

        =========================================================

        คืนค่าอินสแตนซ์ของแอปพลิเคชันปัจจุบัน
        จาก AppiumFlutterLibrary
        """
        return cache_app.get_library_instance('AppiumFlutterLibrary')._current_application()
        # return self._bi.get_library_instance('AppiumFlutterLibrary')._current_application()

    def get_source(self):
        """Returns the entire source of the current page.
        
        =========================================================

        ฟังก์ชันนี้จะส่งคืนสตริงที่มีซอร์สโค้ด HTML ของหน้าเว็บที่กำลังแสดงอยู่ในเบราว์เซอร์ในขณะนั้น 
        ซึ่งสามารถนำไปใช้ในการตรวจสอบหรือวิเคราะห์โครงสร้างหรือเนื้อหาของหน้าเว็บได้
        """
        return self._current_application().page_source
    
    def log_source(self, loglevel='INFO'):
        """Logs and returns the entire html source of the current page or frame.

        The `loglevel` argument defines the used log level. Valid log levels are
        `WARN`, `INFO` (default), `DEBUG`, `TRACE` and `NONE` (no logging).
        """
        ll = loglevel.upper()
        if ll == 'NONE':
            return ''
        else:
            if  "run_keyword_and_ignore_error" not in [check_error_ignored[3] for check_error_ignored in inspect.stack()]:
                source = self._current_application().page_source
                log._log(source, ll)
                return source
            else:
                return ''
            
    def get_driver(self):
        """*******Not available wait for update flutter*******
        Connect Session(Don't Create New Session & )
        """
        current_app_caps = self._current_application()
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_capabilities=current_app_caps, direct_connection=True)
        return driver
    

    def execute_script(self, script, **kwargs):
        """
        Execute a variety of native, mobile commands that aren't associated
        with a specific endpoint. See [https://appium.io/docs/en/commands/mobile-command/|Appium Mobile Command]
        for more details.

        Example:
        | &{scrollGesture}  |  create dictionary  |  left=${50}  |  top=${150}  |  width=${50}  |  height=${200}  |  direction=down  |  percent=${100}  |
        | Sleep             |  1                  |
        | Execute Script    |  mobile: scrollGesture  |  &{scrollGesture}  |

        Updated in AppiumLibrary 2
        """
        if kwargs:
            log._info(f"Provided dictionary: {kwargs}")

        return self._current_application().execute_script(script, kwargs)
    
    def get_appium_session_id(self):
        """Returns the current session ID as a reference"""
        log._info("Appium Session ID: " + self._current_application().session_id)
        return self._current_application().session_id
    
    def send_session_status_to_browserstack(self):
        """
        ***|    Description     |***
        |   *`XSend Status To BrowserStack`*   |   ส่งสถานะและข้อความไปยัง BrowserStack ตาม session_id, status, และ message ที่กำหนด |
 
        ***|    Example     |***
        | *`XSend Status To BrowserStack`* |
 
        ***|    Parameters     |***
        - ไม่มีพารามิเตอร์
 
        *`Create By Tassana Khrueawan (tassana.khr@gmail.com | Tel:097-170-3730)`*
        """
        # ประกาศค่า variables ที่ใช้ในการเชื่อมต่อกับ BrowserStack
        BROWSERSTACK_USERNAME = 'juralakp_p2Vx0U'
        BROWSERSTACK_ACCESS_KEY = 'PPed2Tj3ZNZqaGw6kLyw'
        BROWSERSTACK_URL = f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"

        session_id = BuiltIn().get_variable_value("${SESSION_ID}")
        # session_id = self.get_appium_session_id()
        
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


        