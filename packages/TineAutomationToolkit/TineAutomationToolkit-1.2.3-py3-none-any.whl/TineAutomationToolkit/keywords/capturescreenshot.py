# -*- coding: utf-8 -*-

import os
import robot

from .connectionmanagement import ConnectionManagement
from AppiumLibrary.keywords._logging import _LoggingKeywords

cache_app = ConnectionManagement()
log = _LoggingKeywords()

class CaptureScreenShot:

    def __init__(self):
        pass
    
    #KeyWord

    def native_capture_page_screenshot(self, filename=None):
        """Takes a screenshot of the current page and embeds it into the log.

        `filename` argument specifies the name of the file to write the
        screenshot into. If no `filename` is given, the screenshot will be
        embedded as Base64 image to the log.html. In this case no file is created in the filesystem.

        Warning: this behavior is new in 1.7. Previously if no filename was given
        the screenshots where stored as separate files named `appium-screenshot-<counter>.png`

        Example:

        |t_capture_page_screenshot | None |

        =========================================================

        ถ่ายภาพหน้าจอของหน้าปัจจุบันและฝังลงในบันทึก

        อาร์กิวเมนต์ filename ระบุชื่อของไฟล์ที่จะเขียนภาพหน้าจอลงไป หากไม่มีการระบุ filename, ภาพหน้าจอจะถูกฝังเป็นรูปภาพ Base64 ลงใน log.html
        ในกรณีนี้ไม่มีไฟล์ใดถูกสร้างขึ้นในระบบไฟล์

        คำเตือน: พฤติกรรมนี้เป็นใหม่ในเวอร์ชัน 1.7 ก่อนหน้านี้หากไม่มีการระบุชื่อไฟล์ ภาพหน้าจอจะถูกเก็บเป็นไฟล์แยกต่างหากชื่อว่า 
        appium-screenshot-<counter>.png

        ตัวอย่างการใช้งาน:

        |t_capture_page_screenshot | None |


        """
        if filename:
            path, link = self._get_screenshot_paths(filename)

            if hasattr(cache_app._current_application(), 'get_screenshot_as_file'):
                cache_app._current_application().get_screenshot_as_file(path)
            else:
                cache_app._current_application().save_screenshot(path)

            # Image is shown on its own row and thus prev row is closed on purpose
            log._html('</td></tr><tr><td colspan="3"><a href="%s">'
                       '<img src="%s" width="800px"></a>' % (link, link))
            return path
        else:
            base64_screenshot = cache_app._current_application().get_screenshot_as_base64()
            log._html('</td></tr><tr><td colspan="3">'
                       '<img src="data:image/png;base64, %s" width="800px">' % base64_screenshot)
            return None

    #Private_Function
        
    def _get_screenshot_paths(self, filename):
        filename = filename.replace('/', os.sep)
        logdir = log._get_log_dir()
        path = os.path.join(logdir, filename)
        link = robot.utils.get_link_path(path, logdir)
        return path, link
