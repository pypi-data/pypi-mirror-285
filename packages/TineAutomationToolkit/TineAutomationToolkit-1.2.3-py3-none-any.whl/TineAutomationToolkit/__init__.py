# -*- coding: utf-8 -*-
from TineAutomationToolkit.keywords import *


class TineAutomationToolkit(
    ToolkitsTest,
    WaitingElement,
    ConnectionManagement,
    ControlElement,
    Scroll,
    CaptureScreenShot,
    KeyEvent,
    Touch,
    ConvertObject
    ):

    def __init__(self):
        pass

    def main(self):
        print("This Main นี้คือ เมน")