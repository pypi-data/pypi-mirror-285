from playwright.sync_api import Locator, expect
import logging

class Synchronisation:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.BASIC_FORMAT)
        self.GlobalTimeOut = 5000               

    def GetTimeout(self, Timeout:int = None) -> int:        
        if Timeout == None:
            return self.GlobalTimeOut
        else:
            return Timeout

    def WaitForElement(self, AutomationCtrl : Locator, Timeout : int = None):
        Timeout = self.GetTimeout(Timeout)
        AutomationCtrl.wait_for(state='visible', timeout = Timeout)        
        expect(AutomationCtrl).to_be_attached(timeout = Timeout)
        expect(AutomationCtrl).to_be_visible(timeout = Timeout)
        expect(AutomationCtrl).to_be_in_viewport(timeout = Timeout)

    def WaitForElementToBeVisible(self, AutomationCtrl : Locator, Timeout : int = None): 
        Timeout = self.GetTimeout(Timeout)   
        expect(AutomationCtrl).to_be_visible(timeout = Timeout)
        AutomationCtrl.is_visible(timeout = Timeout)
    
    def WaitForElementNotToBeVisible(self, AutomationCtrl : Locator, Timeout : int = None):  
        Timeout = self.GetTimeout(Timeout)      
        expect(AutomationCtrl).not_to_be_visible(timeout = Timeout)
        AutomationCtrl.is_hidden(timeout = Timeout)
        
    def WaitForElementToBeEnabled(self, AutomationCtrl : Locator, Timeout : int = None):
        Timeout = self.GetTimeout(Timeout)
        expect(AutomationCtrl).to_be_enabled(timeout = Timeout)
        AutomationCtrl.is_enabled(timeout = Timeout)        

    def WaitForElementNotToBeEnabled(self, AutomationCtrl : Locator, Timeout : int = None):
        Timeout = self.GetTimeout(Timeout) 
        expect(AutomationCtrl).not_to_be_enabled(timeout = Timeout)
        AutomationCtrl.is_disabled(timeout = Timeout)

    def WaitForElementToBeEditable(self, AutomationCtrl : Locator, Timeout : int = None):  
        Timeout = self.GetTimeout(Timeout)
        expect(AutomationCtrl).to_be_editable(timeout = Timeout)
        AutomationCtrl.is_editable(timeout = Timeout) 

    def WaitForElementNotToBeEditable(self, AutomationCtrl : Locator, Timeout : int = None): 
        Timeout = self.GetTimeout(Timeout)
        expect(AutomationCtrl).not_to_be_editable(timeout = Timeout)        

    
