# -*- coding: utf-8 -*-

import time
import robot

from .controlelement import ControlElement
from .connectionmanagement import ConnectionManagement
from AppiumLibrary.keywords._applicationmanagement import _ApplicationManagementKeywords

conelement = ControlElement()
timeout_in_secs = float(5)
cache_app = ConnectionManagement()

class WaitingElement:
    
    def __init__(self):
        #เนื่องจากปัญหาเรื่องโครงสร้าง structure เลยยังไม่สามารถใช้ได้
        # self._ce = ControlElement()
        # self._af_amk = _ApplicationManagementKeywords()
        # self._timeout_in_secs = float(5)
        pass

        

    #KeyWord

    def native_wait_element_is_visible(self,locator, timeout=None, error=None):
        """Waits until element specified with `locator` is visible.
        Fails if `timeout` expires before the element is visible. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Page Contains`, `Wait Until Page Contains 
        Element`, `Wait For Condition` and BuiltIn keyword `Wait Until Keyword
        Succeeds`.

        Example: 

        | t_wait_element_is_visible | locator | timeout (defaul=20s) |

        =========================================================

        Wait Until Element Is Visible:
        รอจนกว่าองค์ประกอบ (element) ที่ระบุจะปรากฏในหน้าแอพพลิเคชันและสามารถมองเห็นได้
        ถ้าองค์ประกอบไม่ปรากฏหรือไม่สามารถมองเห็นได้ภายในระยะเวลาที่กำหนด, การทดสอบจะล้มเหลว
        ใช้เมื่อคุณต้องการรอให้องค์ประกอบมองเห็นได้จริงก่อนที่จะดำเนินการต่อ

        ตัวอย่างการใช้งาน:

        | t_wait_element_is_visible | ตำแหน่ง | เวลาที่จะให้รอ (ค่าเริ่มต้น=20s) |

            
        """

        def check_visibility():
            visible = conelement._is_visible(locator)
            if visible:
                return
            elif visible is None:
                return error or "Element locator '%s' did not match any elements after %s" % (locator, self._format_timeout(timeout))
            else:
                return error or "Element '%s' was not visible in %s" % (locator, self._format_timeout(timeout))
        
        self._wait_until_no_error(timeout, check_visibility)

    def native_wait_until_page_contains_element(self, locator, timeout=None, error=None):
        """Waits until element specified with `locator` appears on current page.

        Fails if `timeout` expires before the element appears. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Page Contains`,
        `Wait Until Page Does Not Contain`
        `Wait Until Page Does Not Contain Element`
        and BuiltIn keyword `Wait Until Keyword Succeeds`.

        Example:

        | t_wait_until_page_contains_element | locator | timeout (defaul=20s) |


        =========================================================

        Wait Until Page Contains Element:
        รอจนกว่าองค์ประกอบ (element) ที่ระบุจะปรากฏในหน้าแอพพลิเคชัน แต่ไม่จำเป็นต้องมองเห็นได้
        ถ้าองค์ประกอบไม่ปรากฏในหน้าภายในระยะเวลาที่กำหนด, การทดสอบจะล้มเหลว
        ใช้เมื่อคุณต้องการรอให้องค์ประกอบมีอยู่ใน DOM ของหน้าเว็บ แต่ไม่จำเป็นต้องมองเห็นได้จริง

        ตัวอย่างการใช้งาน:

        | t_wait_until_page_contains_element | ตำแหน่ง | เวลาที่จะให้รอ (ค่าเริ่มต้น=20s) |
        """
        if not error:
            error = "Element '%s' did not appear in <TIMEOUT>" % locator
        self._wait_until(timeout, error, conelement._is_element_present, locator)

    def native_wait_until_page_contains(self, text, timeout=None, error=None):
        """Waits until `text` appears on current page.

        Fails if `timeout` expires before the text appears. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Page Does Not Contain`,
        `Wait Until Page Contains Element`,
        `Wait Until Page Does Not Contain Element` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        if not error:
            error = "Text '%s' did not appear in <TIMEOUT>" % text
        self._wait_until(timeout, error, conelement._is_text_present, text)

    def native_wait_until_page_does_not_contain(self, text, timeout=None, error=None):
        """Waits until `text` disappears from current page.

        Fails if `timeout` expires before the `text` disappears. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Page Contains`,
        `Wait Until Page Contains Element`,
        `Wait Until Page Does Not Contain Element` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.

        ===================================================

        จะล้มเหลวถ้า `timeout` หมดก่อนที่ `text` จะหายไป ดู
        `introduction` เพื่อข้อมูลเพิ่มเติมเกี่ยวกับ `timeout` และค่าเริ่มต้นของมัน

        `error` สามารถใช้เพื่อแทนที่ข้อความแสดงข้อผิดพลาดเริ่มต้น

        ดูเพิ่มเติมที่ `Wait Until Page Contains`,
        `Wait Until Page Contains Element`,
        `Wait Until Page Does Not Contain Element` และคำสั่ง BuiltIn `Wait Until Keyword Succeeds`.
        """

        def check_present():
            present = conelement._is_text_present(text)
            if not present:
                return
            else:
                return error or "Text '%s' did not disappear in %s" % (text, self._format_timeout(timeout))

        self._wait_until_no_error(timeout, check_present)    

    def native_wait_until_page_does_not_contain_element(self, locator, timeout=None, error=None):
        """Waits until element specified with `locator` disappears from current page.

        Fails if `timeout` expires before the element disappears. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

         See also `Wait Until Page Contains`,
        `Wait Until Page Does Not Contain`,
        `Wait Until Page Contains Element` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.

        ===================================================

        จะล้มเหลวถ้า `timeout` หมดก่อนที่ `element` จะหายไป ดู
        `introduction` เพื่อข้อมูลเพิ่มเติมเกี่ยวกับ `timeout` และค่าเริ่มต้นของมัน

        `error` สามารถใช้เพื่อแทนที่ข้อความแสดงข้อผิดพลาดเริ่มต้น

        ดูเพิ่มเติมที่ `Wait Until Page Contains`,
        `Wait Until Page Contains Element`,
        `Wait Until Page Does Not Contain Element` และคำสั่ง BuiltIn `Wait Until Keyword Succeeds`.
        """

        def check_present():
            present = conelement._is_element_present(locator)
            if not present:
                return
            else:
                return error or "Text '%s' did not disappear in %s" % (locator, self._format_timeout(timeout))

        self._wait_until_no_error(timeout, check_present)   

    
    #PRIVATE_FUNCTION
        
    def _format_timeout(self, timeout):
        timeout = robot.utils.timestr_to_secs(timeout) if timeout is not None else timeout_in_secs
        return robot.utils.secs_to_timestr(timeout)
    
    def _wait_until_no_error(self, timeout, wait_func, *args):
        timeout = robot.utils.timestr_to_secs(timeout) if timeout is not None else timeout_in_secs
        maxtime = time.time() + timeout
        while True:
            timeout_error = wait_func(*args)
            if not timeout_error:
                return
            if time.time() > maxtime:
                cache_app.log_source()
                raise AssertionError(timeout_error)
            time.sleep(0.2)

    
    def _wait_until(self, timeout, error, function, *args):
        error = error.replace('<TIMEOUT>', self._format_timeout(timeout))

        def wait_func():
            return None if function(*args) else error

        self._wait_until_no_error(timeout, wait_func)