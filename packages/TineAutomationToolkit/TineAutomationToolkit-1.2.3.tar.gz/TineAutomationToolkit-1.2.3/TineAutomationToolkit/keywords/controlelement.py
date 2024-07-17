# -*- coding: utf-8 -*-
import json
import ast

from AppiumLibrary.locators import ElementFinder
from TineAutomationToolkit.detect.flutterfinderwidget import FlutterDetectWidget , FlutterFinderWidget
from AppiumLibrary.keywords._logging import _LoggingKeywords
from .connectionmanagement import ConnectionManagement
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.touch_action import TouchAction
from TineAutomationToolkit.detect import DetectElement
from unicodedata import normalize



cache_app = ConnectionManagement()
log = _LoggingKeywords()
element_finder_t = ElementFinder()
detect_widget_finder = DetectElement()
widget_finder = FlutterFinderWidget()


def isstr(s):
    return isinstance(s, str)


class ControlElement:

    def __init__(self):
         #เนื่องจากปัญหาเรื่องโครงสร้าง structure เลยยังไม่สามารถใช้ได้
        # self._element_finder_t = ElementFinder()
        # self._co = ConnectionManagement()
        # self._log = _LoggingKeywords()
        pass
    #KeyWord
    
        #Switch_Mode
        
    def native_switch_mode(self,mode):
        """The keyword is used for switching content between Native_app and Flutter
        It is necessary to open the app using the AppiumFlutterLibrary and the automation name: Flutter.
        
        Example: 

        | t_switch_mode   |  NATIVE_APP |  
        
        | t_switch_mode   |  FLUTTER |

        =========================================================

        คีย์เวิร์ดใช้สำหรับการสลับเนื้อหาระหว่าง Native_app กับ Flutter
        จำเป็นต้อง OpenApp ด้วย Library: AppiumFlutterLibrary และ automationname : Flutter 

        ตัวอย่างการใช้งาน: 

        | t_switch_mode   |  NATIVE_APP 
        
        | t_switch_mode   |  FLUTTER
        """
        driver = cache_app._current_application()

        if mode == 'NATIVE_APP':
            driver.switch_to.context('NATIVE_APP')
            print("... Status Mode : Native_app")
        if mode == 'FLUTTER':
            driver.switch_to.context('FLUTTER')
            print("... Status Mode : Flutter")
 
    #NATIVE_APP

    def native_click_element(self,locator):
        """Click element identified by `locator`.

        Key attributes for arbitrary elements are `index` and `name`. See
        `introduction` for details about locating elements.

        Example:

        |t_click_element | locator |

        =========================================================

        คลิกที่องค์ประกอบที่ระบุด้วย locator (ตัวระบุตำแหน่ง)    
        กด click หรือ tap element
        ตาม locator ที่ระบุเข้ามา

        ตัวอย่างการใช้งาน:
        
        |t_click_element | ตัวระบุตำแหน่ง |


        **** locator ได้แก่ id , name , xpath เป็นต้น  ****

        """
        log._info("Clicking element '%s'." % locator)
        self._element_find_t(locator, True , True).click()

    def native_click_element_at_coordinates(self, coordinate_X, coordinate_Y):
        """*DEPRECATED!!* Since selenium v4, use other keywords.

        click element at a certain coordinate 
        
        Example:

        | native_click_element_at_coordinates | coordinate_X | coordinate_Y |

        =========================================================

        
        ไม่แนะนำให้ใช้!! ตั้งแต่เวอร์ชัน 4 ของ Selenium, ให้ใช้คีย์เวิร์ดอื่นแทน

        คลิกที่องค์ประกอบที่พิกัดที่กำหนด

        ตัวอย่างการใช้งาน:

        | native_click_element_at_coordinates | ระยะพิกัด X | ระยะพิกัด Y |

        """
        log._info("Pressing at (%s, %s)." % (coordinate_X, coordinate_Y))
        driver = cache_app._current_application()
        action = TouchAction(driver)
        action.press(x=coordinate_X, y=coordinate_Y).release().perform()

        #Get
   
    def native_get_element_attribute(self, locator, attribute):
        """Get element attribute using given attribute: name, value,...

        Examples:

        | Get Element Attribute | locator | name |
        | Get Element Attribute | locator | value |

         =========================================================

        ใช้การดึงข้อมูลแอตทริบิวต์ของอีเลเมนต์โดยใช้ชื่อแอตทริบิวต์: ชื่อ, ค่า, ตำแหน่ง ,ฯลฯ เป็นต้น

        ตัวอย่าง:

        | ดึงข้อมูลแอตทริบิวต์อีเลเมนต์ | ตัวระบุตำแหน่ง | ชื่อ |
        | ดึงข้อมูลแอตทริบิวต์อีเลเมนต์ | ตัวระบุตำแหน่ง | ค่า |
        """
        elements = self._element_find_t(locator, False, True)
        ele_len = len(elements)
        if ele_len == 0:
            raise AssertionError("Element '%s' could not be found" % locator)
        elif ele_len > 1:
            log._info("CAUTION: '%s' matched %s elements - using the first element only" % (locator, len(elements)))

        try:
            attr_val = elements[0].get_attribute(attribute)
            log._info("Element '%s' attribute '%s' value '%s' " % (locator, attribute, attr_val))
            return attr_val
        except:
            raise AssertionError("Attribute '%s' is not valid for element '%s'" % (attribute, locator))

    def native_get_element_location(self, locator):
        """Get element location
        Key attributes for arbitrary elements are `id` and `name`.

        =========================================================

        รับตำแหน่งขององค์ประกอบ
        คุณสมบัติหลักสำหรับองค์ประกอบทั่วไปคือ `id` และ `name` 
        """
        element = self._element_find_t(locator, True, True)
        element_location = element.location
        log._info("Element '%s' location: %s " % (locator, element_location))
        return element_location

    def native_get_element_size(self, locator):
        """Get element size
        Key attributes for arbitrary elements are `id` and `name`

        =========================================================

        รับขนาดขององค์ประกอบ
        คุณสมบัติหลักสำหรับองค์ประกอบทั่วไปคือ `id` และ `name`
        """
        element = self._element_find_t(locator, True, True)
        element_size = element.size
        log._info("Element '%s' size: %s " % (locator, element_size))
        return element_size

    def native_get_text(self, locator):
        """Get element text (for hybrid and mobile browser use `xpath` locator, others might cause problem)

        Example:

        | ${text} | Get Text | //*[contains(@text,'foo')] |

        New in AppiumLibrary 1.4.

        =========================================================

        ดึงข้อความจากอีเลเมนต์ (สำหรับการใช้งานในไฮบริดและเบราว์เซอร์มือถือ ใช้ตัวระบุตำแหน่ง xpath, อื่นๆ อาจทำให้เกิดปัญหา)

        ตัวอย่างการใช้งาน:

        | ${text} | ดึงข้อความ | //*[contains(@text,'foo')] |

        ใหม่ใน AppiumLibrary 1.4.
        """
        text = self._get_text(locator)
        log._info("Element '%s' text is '%s' " % (locator, text))
        return text

    #Should be
    
    def native_page_should_not_contain_element(self, locator, loglevel='INFO'):
        """Verifies that current page not contains `locator` element.

        If this keyword fails, it automatically logs the page source
        using the log level specified with the optional `loglevel` argument.
        Giving `NONE` as level disables logging.

        =========================================================

        หากคำสั่งนี้ล้มเหลว ระบบจะบันทึกแหล่งข้อมูลของหน้าโดยอัตโนมัติ
        โดยใช้ระดับการบันทึกที่กำหนดไว้ในอาร์กิวเมนต์ `loglevel` ที่เป็นอุปกรณ์เสริม
        การกำหนดค่า `NONE` เป็นระดับจะปิดการบันทึก
        """
        if self._is_element_present(locator):
            cache_app.log_source(loglevel)
            raise AssertionError("Page should not have contained element '%s'" % locator)
        log._info("Current page not contains element '%s'." % locator)
    
      #Input
    
    def native_input_text(self, locator, text):
        """Types the given `text` into text field identified by `locator`.

        See `introduction` for details about locating elements.

        Example:

        | t_input_text | text |

        =========================================================

        พิมพ์ข้อความที่กำหนดให้ (text) ลงในช่องข้อความที่ระบุด้วย locator
        
        ดู introduction เพื่อดูรายละเอียดเกี่ยวกับการระบุตำแหน่งของอีเลเมนต์

        ตัวอย่างการใช้งาน:

        | t_input_text | ข้อความที่ต้องการจะใส่ |

        """
        log._info("Typing text '%s' into text field '%s'" % (text, locator))
        self._element_input_text_by_locator(locator, text)

    def native_element_text_should_be(self, locator, expected, message=''):
        """Verifies element identified by ``locator`` exactly contains text ``expected``.
        In contrast to `Element Should Contain Text`, this keyword does not try
        a substring match but an exact match on the element identified by ``locator``.
        ``message`` can be used to override the default error message.

        New in AppiumLibrary 1.4.

        =========================================================

        ตรวจสอบว่าองค์ประกอบที่ระบุโดย ``locator`` มีข้อความ ``expected`` อย่างแม่นยำ
        ต่างจาก `Element Should Contain Text`, คำสั่งนี้ไม่พยายามทำการจับคู่ข้อความย่อย แต่ทำการจับคู่ข้อความอย่างแม่นยำบนองค์ประกอบที่ระบุโดย ``locator``
        ``message`` สามารถใช้เพื่อแทนที่ข้อความแสดงข้อผิดพลาดเริ่มต้น

        ใหม่ใน AppiumLibrary 1.4

        """
        log._info("Verifying element '%s' contains exactly text '%s'."
                    % (locator, expected))
        element = self._element_find_t(locator, True, True)
        actual = element.text
        if expected != actual:
            if not message:
                message = "The text of element '%s' should have been '%s' but "\
                          "in fact it was '%s'." % (locator, expected, actual)
            raise AssertionError(message)

    def native_element_should_be_visible(self , locator, loglevel='INFO'):
        """Verifies that element identified with locator is visible.

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.

        New in AppiumLibrary 1.4.5
        """
        if not self._element_find_t(locator, True, True).is_displayed():
            cache_app.log_source(loglevel)
            raise AssertionError("Element '%s' should be visible "
                                 "but did not" % locator)

    def native_is_keyboard_shown(self):
        """Return true if Android keyboard is displayed or False if not displayed
        No parameters are used.

        =========================================================

        คืนค่าเป็นจริงหากแป้นพิมพ์แอนดรอยด์ถูกแสดง หรือคืนค่าเป็นเท็จหากไม่ได้แสดง
        ไม่ใช้อาร์กิวเมนต์ใดๆ
        """
        driver = cache_app._current_application()
        return driver.is_keyboard_shown()
    
    def native_hide_keyboard(self, key_name=None):
        """Hides the software keyboard on the device. (optional) In iOS, use `key_name` to press
        a particular key, ex. `Done`. In Android, no parameters are used.

        =========================================================

        ซ่อนแป้นพิมพ์ซอฟต์แวร์บนอุปกรณ์ (เพิ่มเติม) ใน iOS, ใช้ `key_name` 
        เพื่อกดปุ่มที่ระบุ เช่น `Done` ใน Android, ไม่ใช้อาร์กิวเมนต์ใดๆ
        """
        driver = cache_app._current_application()
        driver.hide_keyboard(key_name)

    def native_get_webelements(self, locator):
        """Returns list of [http://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.remote.webelement|WebElement] objects matching ``locator``.

        Example:
        | @{elements}    | Get Webelements | id=my_element |
        | Click Element  | @{elements}[2]  |               |

        This keyword was changed in AppiumLibrary 1.4 in following ways:
        - Name is changed from `Get Elements` to current one.
        - Deprecated argument ``fail_on_error``, use `Run Keyword and Ignore Error` if necessary.

        New in AppiumLibrary 1.4.
        
        =========================================================

        คืนค่าเป็นรายการของออบเจ็กต์ [WebElement](http://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.remote.webelement) ที่ตรงกับ ``locator``.

        ตัวอย่าง:
        | @{elements}    | รับ Webelements | id=my_element |
        | คลิกองค์ประกอบ | @{elements}[2]  |               |

        คำสั่งนี้ได้รับการเปลี่ยนแปลงใน AppiumLibrary 1.4 ดังนี้:
        - ชื่อถูกเปลี่ยนจาก `Get Elements` เป็นชื่อปัจจุบัน
        - อาร์กิวเมนต์ที่ไม่แนะนำอีกต่อไป ``fail_on_error``, ใช้ `Run Keyword and Ignore Error` ถ้าจำเป็น

        ใหม่ใน AppiumLibrary 1.4
        """
        return self._element_find_t(locator, False, True)

    #Flutter (Not available , อยู่ในช่วงทดสอบ ยังไม่สามารถใช้งานได้)

    def flutter_get_widget_diagnostic(self , locator ,subtreeDepth=0 , includeProperties=True):
        """ ********* (Not Support BrowserStack) **********
        
        Returns a JSON map of the DiagnosticsNode that is associated with the Widget identified by finder.
        The subtreeDepth argument controls how many layers of children will be included in the result. It defaults to zero, which means that no children of the Widget identified by finder will be part of the result.
        The includeProperties argument controls whether properties of the DiagnosticsNodes will be included in the result. It defaults to true.
        Widgets describe configuration for the rendering tree. Individual widgets may create multiple RenderObjects to actually layout and paint the desired configuration.
        
        =========================================================
        getWidgetDiagnostics method คือ เมธอดที่ใช้ในการดึงข้อมูลการวินิจฉัยหรือรายละเอียดต่าง ๆ ของ widget 
        ที่ระบุในแอปพลิเคชัน Flutter โดยข้อมูลเหล่านี้จะเป็นข้อมูลเชิงลึกเกี่ยวกับสถานะและคุณสมบัติต่าง ๆ ของ widget
        นั้น ๆ ซึ่งสามารถใช้ในการดีบักหรือวิเคราะห์การทำงานของ widget ได้

        โครงสร้าง
        Future<Map<String, Object?>> getWidgetDiagnostics(
        SerializableFinder finder,
        {int subtreeDepth = 0,
        bool includeProperties = true,
        Duration? timeout}
        )
        รายละเอียดเพิ่มเติม
        ค่าของ subtreeDepth กำหนดว่าคุณต้องการดึงข้อมูลการวินิจฉัยจากโครงสร้างของ widget ลึกเท่าใด:

        subtreeDepth = 0
        ความหมาย: ดึงข้อมูลเฉพาะ widget ที่ระบุเท่านั้น ไม่รวม widget ลูกหรือ widget ที่อยู่ในโครงสร้างภายใน
        ตัวอย่าง: หากคุณมี widget A ซึ่งมี widget ลูก B และ C, เมื่อตั้งค่าเป็น 0 คุณจะได้รับข้อมูลเฉพาะ widget A เท่านั้น

        subtreeDepth = 1
        ความหมาย: ดึงข้อมูลของ widget ที่ระบุรวมถึง widget ลูกในระดับแรก
        ตัวอย่าง: หากคุณมี widget A ซึ่งมี widget ลูก B และ C, และ B มี widget ลูก D และ E, เมื่อตั้งค่าเป็น 1 คุณจะได้รับข้อมูลของ widget A, B, และ C แต่จะไม่รวม D และ E
        
        subtreeDepth = 2
        ความหมาย: ดึงข้อมูลของ widget ที่ระบุรวมถึง widget ลูกในระดับที่สอง
        ตัวอย่าง: หากคุณมี widget A ซึ่งมี widget ลูก B และ C, B มี widget ลูก D และ E และ C มี widget ลูก F, เมื่อตั้งค่าเป็น 2 คุณจะได้รับข้อมูลของ widget A, B, C, D, E, และ F
        """
        counterTextFinder = widget_finder.by_value_key(locator)
        driver = cache_app._current_application()
        diagnostics = driver.execute_script('flutter:getWidgetDiagnostics', counterTextFinder, { 'includeProperties': includeProperties, 'subtreeDepth': subtreeDepth })
        #json
        formatted_json = json.dumps(diagnostics, indent=2, ensure_ascii=False)
        return  formatted_json

    def flutter_get_value_widget_is_visible(self,formatted_json, key_to_check, value_to_check):
        """ *********(FIXING) (Not Support BrowserStack) **********
        ตรวจสอบค่าของ key ใน JSON data และเทียบกับ value
        ว่าปรากฏใน JSON DATA หรือไม่
        
        example : flutter_get_value_widget_should_be | json data | key_to_check = "description" | value_to_check = "\"ถัดไป\""
                  flutter_get_value_widget_should_be | json data | key_to_check = "value" | value_to_check = "ถัดไป"
                  flutter_get_value_widget_should_be | json data | key_to_check = "description" | value_to_check = "Color(0xffabaca8)"
                  flutter_get_value_widget_should_be | json data | key_to_check = "valueProperties" | value_to_check = {"red": 171,"green": 172,"blue": 168,"alpha": 255}
                  flutter_get_value_widget_should_be | json data | key_to_check = "description" | value_to_check = Text-[<'billAndPayPayForOther/stickyButtonNextStep/chmButtonSet/chmButton/primary/textButton'>]
        """    
        result = self._flutter_check_widget_value_in_json(formatted_json, key_to_check, value_to_check)
        return  (f"Inspecter results: {result}")
    
    def flutter_get_properties_value_widget(self, data_json , name_value="description" ):
        """ *********(Not Support BrowserStack) **********
        JSON data ตรวจสอบและดึงค่าที่อยู่ใน properties ตามชื่อ name_value ที่ให้มา 
        จากนั้นนำค่าเป็นเก็บเป็น array เพื่อเรียกใช้

        data_json = ได้มากจาก flutter_get_widget_diagnostic
        name_value = แต่ละ widget มีไม่เหมือนกันสามารถดูได้ จากข้อมูลที่ได้มากจาก flutter_get_widget_diagnostic
        
        example : flutter_get_properties_value_widget | json data | name_value = "description" 
                  flutter_get_properties_value_widget | json data | name_value = "value" 
                  flutter_get_properties_value_widget | json data | name_value = "level" 
                  flutter_get_properties_value_widget | json data | name_value = "valueProperties" 
                  flutter_get_properties_value_widget | json data | name_value = "red" 
        """   
        data = json.loads(data_json)
        Results = [prop[name_value] for prop in data['properties']]
        return  Results
    
    def flutter_get_top_left_widget(self,locator,LoadList=True):
        """ ********* Maybe Support BrowserStack  **********
        Get Position Top Left Widget And Return

        ===============================================

        Get ค่ามุมบนซ้ายของ Widget นั้น
        Locator = key ของ Widget นั้น หรือตำแหน่ง
        LoadList หากต้องการให้ Return ออกเป็น List ให้ค่า LoadList = True แต่ถ้า LoadList=False จะได้ค่ารูปแบบ json.loads 
        True : [('dx', 173.3056640625), ('dy', 679.3333333333334)]
        False : {'dx': 173.3056640625, 'dy': 679.3333333333334}

        Example : flutter_get_top_left_widget | locator | LoadList=True
        """   
        counterTextFinder = widget_finder.by_value_key(locator)
        driver = cache_app._current_application()
        topleft = driver.execute_script('flutter:getTopLeft',counterTextFinder)
        #dump & load Json
        json_data = json.dumps(topleft)
        parsed_data = json.loads(json_data)
        #LoadList
        if LoadList == True :
            data_list = list(parsed_data.items())
        if LoadList == False:
            data_list = parsed_data
        #return
        return  data_list
    
    def flutter_get_top_right_widget(self,locator,LoadList=True):
        """ ********* Maybe Support BrowserStack  **********
        Get Position Top Right Widget And Return

        ===============================================

        Get ค่ามุมบนขวาของ Widget นั้น
        Locator = key ของ Widget นั้น หรือตำแหน่ง
        LoadList หากต้องการให้ Return ออกเป็น List ให้ค่า LoadList = True แต่ถ้า LoadList=False จะได้ค่ารูปแบบ json.loads 
        True : [('dx', 173.3056640625), ('dy', 679.3333333333334)]
        False : {'dx': 173.3056640625, 'dy': 679.3333333333334}

        Example : flutter_get_top_right_widget | locator | LoadList=True
        """   
        counterTextFinder = widget_finder.by_value_key(locator)
        driver = cache_app._current_application()
        topright = driver.execute_script('flutter:getTopRight',counterTextFinder)
        #dump & load Json
        json_data = json.dumps(topright)
        parsed_data = json.loads(json_data)
        #LoadList
        if LoadList == True :
            data_list = list(parsed_data.items())
        if LoadList == False:
            data_list = parsed_data
        #return
        return  data_list
    
    def flutter_get_bottom_left_widget(self,locator,LoadList=True):
        """ ********* Maybe Support BrowserStack  **********
        Get Position Bottom Left Widget And Return

        ===============================================

        Get ค่ามุมล่างซ้ายของ Widget นั้น
        Locator = key ของ Widget นั้น หรือตำแหน่ง
        LoadList หากต้องการให้ Return ออกเป็น List ให้ค่า LoadList = True แต่ถ้า LoadList=False จะได้ค่ารูปแบบ json.loads 
        True : [('dx', 173.3056640625), ('dy', 679.3333333333334)]
        False : {'dx': 173.3056640625, 'dy': 679.3333333333334}

        Example : flutter_get_bottom_left_widget | locator | LoadList=True
        """   
        counterTextFinder = widget_finder.by_value_key(locator)
        driver = cache_app._current_application()
        bottomleft = driver.execute_script('flutter:getBottomLeft',counterTextFinder)
        #dump & load Json
        json_data = json.dumps(bottomleft)
        parsed_data = json.loads(json_data)
        #LoadList
        if LoadList == True :
            data_list = list(parsed_data.items())
        if LoadList == False:
            data_list = parsed_data
        #return
        return  data_list
    
    def flutter_get_bottom_right_widget(self,locator,LoadList=True):
        """ ********* Maybe Support BrowserStack  **********
        Get Position Bottom Right Widget And Return

        ===============================================

        Get ค่ามุมล่างขวาของ Widget นั้น
        Locator = key ของ Widget นั้น หรือตำแหน่ง
        LoadList หากต้องการให้ Return ออกเป็น List ให้ค่า LoadList = True แต่ถ้า LoadList=False จะได้ค่ารูปแบบ json.loads 
        True : [('dx', 173.3056640625), ('dy', 679.3333333333334)]
        False : {'dx': 173.3056640625, 'dy': 679.3333333333334}

        Example : flutter_get_bottom_right_widget | locator | LoadList=True
        """   
        counterTextFinder = widget_finder.by_value_key(locator)
        driver = cache_app._current_application()
        bottomright = driver.execute_script('flutter:getBottomRight',counterTextFinder)
        #dump & load Json
        json_data = json.dumps(bottomright)
        parsed_data = json.loads(json_data)
        #LoadList
        if LoadList == True :
            data_list = list(parsed_data.items())
        if LoadList == False:
            data_list = parsed_data
        #return
        return  data_list
    
    def flutter_get_center_widget(self,locator,LoadList=True):
        """ ********* Maybe Support BrowserStack  **********
        Get Position Center Widget And Return

        ===============================================

        Get ค่ากึ่งกลางของ Widget นั้น
        Locator = key ของ Widget นั้น หรือตำแหน่ง
        LoadList หากต้องการให้ Return ออกเป็น List ให้ค่า LoadList = True แต่ถ้า LoadList=False จะได้ค่ารูปแบบ json.loads 
        True : [('dx', 173.3056640625), ('dy', 679.3333333333334)]
        False : {'dx': 173.3056640625, 'dy': 679.3333333333334}

        Example : flutter_get_center_widget | locator | LoadList=True
        """   
        counterTextFinder = widget_finder.by_value_key(locator)
        driver = cache_app._current_application()
        center = driver.execute_script('flutter:getCenter',counterTextFinder)
        #dump & load Json
        json_data = json.dumps(center)
        parsed_data = json.loads(json_data)
        #LoadList
        if LoadList == True :
            data_list = list(parsed_data.items())
        if LoadList == False:
            data_list = parsed_data
        #return
        return  data_list
    
    def flutter_get_element_attribute(self, locator, attribute):
        """ *******Not available wait for update flutter*******

        Because FinderType is Limited

        Get element attribute using given attribute: name, value,...

        Examples:

        | Get Element Attribute | locator | name |
        | Get Element Attribute | locator | value |
        """
        elements = self._element_find_flutter(locator, False, True)
        # elements = self._element_find_t(locator, False, True)
        ele_len = len(elements)
        if ele_len == 0:
            raise AssertionError("Element '%s' could not be found" % locator)
        elif ele_len > 1:
            self._info("CAUTION: '%s' matched %s elements - using the first element only" % (locator, len(elements)))

        try:
            attr_val = elements[0].get_attribute(attribute)
            log._info("Element '%s' attribute '%s' value '%s' " % (locator, attribute, attr_val))
            return attr_val
        except:
            raise AssertionError("Attribute '%s' is not valid for element '%s'" % (attribute, locator))
        
    def flutter_check_element_enable(self,locator):
        """ *******Not available wait for update flutter*******

        Get element enable 

        Examples:

        | Check Element Enable | locator |
        """
        print("ยังอยู่ในช่วงทดสอบ ยังไม่สามารถใช้งานได้")
    
    #PRIVATE_FUNCTION

    def _element_find_flutter(self, locator, first_only, required, tag=None):
        application = cache_app._current_application()
        elements = None
        if isstr(locator):
            _locator = locator
            element = detect_widget_finder.find_attribute(application , _locator , tag)
            if required and len(elements) == 0:
                raise ValueError("Element locator '" + locator + "' did not match any elements.")
            if first_only:
                if len(elements) == 0: return None
                return elements[0]
        elif isinstance(locator, WebElement):
            if first_only:
                return locator
            else:
                elements = [locator]

        
        return element
        
    def _element_find_t(self, locator, first_only, required, tag=None):
        application = cache_app._current_application()
        elements = None
        if isstr(locator):
            _locator = locator
            elements = element_finder_t.find(application, _locator, tag)
            if required and len(elements) == 0:
                raise ValueError("Element locator '" + locator + "' did not match any elements.")
            if first_only:
                if len(elements) == 0: return None
                return elements[0]
        elif isinstance(locator, WebElement):
            if first_only:
                return locator
            else:
                elements = [locator]
        # do some other stuff here like deal with list of webelements
        # ... or raise locator/element specific error if required
        return elements
    
    def _is_visible(self, locator):
        element = self._element_find_t(locator, True, False)
        if element is not None:
            return element.is_displayed()
        return None
    
    def _is_element_present(self, locator):
        application = cache_app._current_application()
        elements = element_finder_t.find(application, locator, None)
        return len(elements) > 0

    def _get_text(self, locator):
        element = self._element_find_t(locator, True, True)
        if element is not None:
            return element.text
        return None
    
    def _element_input_text_by_locator(self, locator, text):
        try:
            element = self._element_find_t(locator, True, True)
            element.send_keys(text)
        except Exception as e:
            raise e
    
    def _is_text_present(self, text):
        text_norm = normalize('NFD', text)
        source_norm = normalize('NFD', cache_app.get_source())
        return text_norm in source_norm
    
    def _flutter_check_widget_value_in_json(self,data, key, value):
        """
        ตรวจสอบค่าของ key ใน JSON data ที่ได้จาก widget 

        :param data: JSON data ที่จะตรวจสอบ
        :param key: key ที่จะตรวจสอบ
        :param value: ค่าที่ต้องการเปรียบเทียบ
        :return: True ถ้าพบ key และ value ตรงกัน, False ถ้าไม่พบ
        """
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key and v == value:
                    return True
                if isinstance(v, (dict, list)):
                    if self._flutter_check_widget_value_in_json(v, key, value):
                        return True
        elif isinstance(data, list):
            for item in data:
                if self._flutter_check_widget_value_in_json(item, key, value):
                    return True
        return False