from playwright.sync_api import Locator, expect
import logging

class Validation:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.BASIC_FORMAT)

    def IsElementEnabled(self, AutomationCtrl : Locator, enabledProp : bool ):
        assert AutomationCtrl.is_enabled() == enabledProp

    def IsElementDisabled(self, AutomationCtrl : Locator, disabledProp : bool ):
        assert AutomationCtrl.is_disabled() == disabledProp
        
    def IsElementEditable(self, AutomationCtrl : Locator, editableProp : bool ):
        assert AutomationCtrl.is_editable() == editableProp

    def IsElementNotEditable(self, AutomationCtrl : Locator, notEditableProp : bool ):
        assert AutomationCtrl.is_editable() != notEditableProp

    def IsElementVisible(self, AutomationCtrl : Locator, visibleProp : bool ):
        assert AutomationCtrl.is_visible() == visibleProp

    def IsElementNotVisible(self, AutomationCtrl : Locator, visibleProp : bool ):
        assert AutomationCtrl.is_hidden() == visibleProp

    def IsElementChecked(self, AutomationCtrl : Locator, visibleProp : bool ):
        assert AutomationCtrl.is_checked() == visibleProp

    def IsElementNotchecked(self, AutomationCtrl : Locator, visibleProp : bool ):
        assert AutomationCtrl.is_checked() != visibleProp

    def VerifyPropertyValue(self, AutomationCtrl : Locator, propName, propValue):                
        assert AutomationCtrl.get_attribute(propName) == propValue

    def ContainsPropertyValue(self, AutomationCtrl : Locator, propName, propValue):        
        assert propValue in AutomationCtrl.get_attribute(propName)
         