from playwright.sync_api import Locator
import logging

class Action:

    def __init__(self) -> None:
        logging.basicConfig(level=logging.DEBUG)        
        pass


    def Click(self, AutomationCtrl : Locator):
        try:
            AutomationCtrl.click()
            logging.info(f"Clicked on element with selector: {AutomationCtrl}")            
        except Exception as e:
            logging.error(f"Error occurred while clicking element with selector {AutomationCtrl} : {e}")            

    def SendKeys(self, AutomationCtrl : Locator, TextToSend):
        try:
            AutomationCtrl.fill(TextToSend)
            logging.info(f"Fill on input field with selector: '{AutomationCtrl}' with text: {TextToSend}")            
        except Exception as e:
            logging.error(f"Error occurred while filling input field: '{AutomationCtrl}' with text: '{TextToSend}' : {e}")
      
    def Hover(self, AutomationCtrl : Locator):
        try:
            AutomationCtrl.hover()
            logging.info(f"Hover on element with selector: '{AutomationCtrl}'")            
        except Exception as e:
            logging.error(f"Error occurred while hovering element with selector: {AutomationCtrl} : {e}")
    
    def Type(self, AutomationCtrl : Locator, TextToSend):
        try:
            AutomationCtrl.type(TextToSend)
            logging.info(f"Type on input field with selector: '{AutomationCtrl}' with text: {TextToSend}")            
        except Exception as e:
            logging.error(f"Error occurred while typing input field '{AutomationCtrl}' with text '{TextToSend}' : {e}")
    
    def Check(self, AutomationCtrl : Locator):
        try:
            AutomationCtrl.check(force=True)
            logging.info(f"Checked input field with selector: '{AutomationCtrl}'")            
        except Exception as e:
            logging.error(f"Error occurred while checking input field '{AutomationCtrl}' : {e}")
    
    def Uncheck(self, AutomationCtrl : Locator):
        try:
            AutomationCtrl.uncheck(force=True)
            logging.info(f"Unchecked input field with selector: '{AutomationCtrl}'")            
        except Exception as e:
            logging.error(f"Error occurred while unchecking input field '{AutomationCtrl}' : {e}")

    def InnerText(self, AutomationCtrl: Locator):
        try:
            text = AutomationCtrl.inner_text()
            logging.info(f"Retrieved inner text from element with selector: {AutomationCtrl}")
            return text
        except Exception as e:
            logging.error(f"Error in InnerText: {e}")

    def TextContent(self, AutomationCtrl: Locator):
        try:
            content = AutomationCtrl.text_content()
            logging.info(f"Retrieved text content from element with selector: {AutomationCtrl}")
            return content
        except Exception as e:
            logging.error(f"Error in TextContent: {e}")
    
    def AllInnerText(self, AutomationCtrl: Locator):
        try:
            all_texts = AutomationCtrl.all_inner_texts()
            logging.info(f"Retrieved all inner texts from elements with selector: {AutomationCtrl}")
            return all_texts
        except Exception as e:
            logging.error(f"Error in AllInnerText: {e}")
    
    def AllTextContent(self, AutomationCtrl: Locator):
        try:
            all_contents = AutomationCtrl.all_text_contents()
            logging.info(f"Retrieved all text contents from elements with selector: {AutomationCtrl}")
            return all_contents
        except Exception as e:
            logging.error(f"Error in AllTextContent: {e}")
    
    def GetProperty(self, AutomationCtrl: Locator, GetProperty=None):
        try:
            property_value = AutomationCtrl.get_attribute(GetProperty)
            logging.info(f"Retrieved property '{GetProperty}' from element with selector: {AutomationCtrl}")
            return property_value
        except Exception as e:
            logging.error(f"Error in GetProperty: {e}")
    
    def Focus(self, AutomationCtrl: Locator):
        try:
            AutomationCtrl.focus()
            logging.info(f"Focused on element with selector: {AutomationCtrl}")
        except Exception as e:
            logging.error(f"Error in Focus: {e}")
    
    def DoubleClick(self, AutomationCtrl: Locator):
        try:
            AutomationCtrl.dblclick(force=True)
            logging.info(f"Double-clicked on element with selector: {AutomationCtrl}")
        except Exception as e:
            logging.error(f"Error in DoubleClick: {e}")
    
    def Clear(self, AutomationCtrl: Locator):
        try:
            AutomationCtrl.clear(force=True)
            logging.info(f"Cleared element with selector: {AutomationCtrl}")
        except Exception as e:
            logging.error(f"Error in Clear: {e}")
    
    def Fill(self, AutomationCtrl: Locator, TextToSend):
        try:
            AutomationCtrl.fill(TextToSend)
            logging.info(f"Filled element with selector: {AutomationCtrl} with text: {TextToSend}")
        except Exception as e:
            logging.error(f"Error in Fill: {e}")
    
    def Type(self, AutomationCtrl: Locator, TextToSend):
        try:
            AutomationCtrl.type(TextToSend)
            logging.info(f"Typed into element with selector: {AutomationCtrl} with text: {TextToSend}")
        except Exception as e:
            logging.error(f"Error in Type: {e}")
    
    def Blur(self, AutomationCtrl: Locator):
        try:
            AutomationCtrl.blur()
            logging.info(f"Blurred element with selector: {AutomationCtrl}")
        except Exception as e:
            logging.error(f"Error in Blur: {e}")
    
    def Count(self, AutomationCtrl: Locator):
        try:
            count = AutomationCtrl.count()
            logging.info(f"Counted elements with selector: {AutomationCtrl}. Count: {count}")
            return count
        except Exception as e:
            logging.error(f"Error in Count: {e}")
    
    def All(self, AutomationCtrl: Locator):
        try:
            all_elements = AutomationCtrl.all()
            logging.info(f"Retrieved all elements with selector: {AutomationCtrl}")
            return all_elements
        except Exception as e:
            logging.error(f"Error in All: {e}")
    
    def First(self, AutomationCtrl: Locator):
        try:
            first_element = AutomationCtrl.first
            logging.info(f"Retrieved first element with selector: {AutomationCtrl}")
            return first_element
        except Exception as e:
            logging.error(f"Error in First: {e}")
    
    def Last(self, AutomationCtrl: Locator):
        try:
            last_element = AutomationCtrl.last
            logging.info(f"Retrieved last element with selector: {AutomationCtrl}")
            return last_element
        except Exception as e:
            logging.error(f"Error in Last: {e}")
    
    ######################


    def InnerText(self, AutomationCtrl: Locator):
        try:
            return AutomationCtrl.inner_text()
        except Exception as e:
            logging.error(f"Error in InnerText: {e}")
    
    def TextContent(self, AutomationCtrl: Locator):
        try:
            return AutomationCtrl.text_content()
        except Exception as e:
            logging.error(f"Error in TextContent: {e}")

    def AllInnerText(self, AutomationCtrl: Locator):
        try:
            return AutomationCtrl.all_inner_texts()
        except Exception as e:
            logging.error(f"Error in AllInnerText: {e}")

    def AllTextContent(self, AutomationCtrl: Locator):
        try:
            return AutomationCtrl.all_text_contents()
        except Exception as e:
            logging.error(f"Error in AllTextContent: {e}")

    def GetProperty(self, AutomationCtrl: Locator, GetProperty=None):
        try:
            return AutomationCtrl.get_attribute(GetProperty)
        except Exception as e:
            logging.error(f"Error in GetProperty: {e}")

    def Focus(self, AutomationCtrl: Locator):
        try:
            AutomationCtrl.focus()
        except Exception as e:
            logging.error(f"Error in Focus: {e}")

    def DoubleClick(self, AutomationCtrl: Locator):
        try:
            AutomationCtrl.dblclick(force=True)
        except Exception as e:
            logging.error(f"Error in DoubleClick: {e}")

    def Clear(self, AutomationCtrl: Locator):
        try:
            AutomationCtrl.clear(force=True)
        except Exception as e:
            logging.error(f"Error in Clear: {e}")

    def Fill(self, AutomationCtrl: Locator, TextToSend):
        try:
            AutomationCtrl.fill(TextToSend)
        except Exception as e:
            logging.error(f"Error in Fill: {e}")

    def Type(self, AutomationCtrl: Locator, TextToSend):
        try:
            AutomationCtrl.type(TextToSend)
        except Exception as e:
            logging.error(f"Error in Type: {e}")

    def Blur(self, AutomationCtrl: Locator):
        try:
            AutomationCtrl.blur()
        except Exception as e:
            logging.error(f"Error in Blur: {e}")

    def Count(self, AutomationCtrl: Locator):
        try:
            return AutomationCtrl.count()
        except Exception as e:
            logging.error(f"Error in Count: {e}")

    def All(self, AutomationCtrl: Locator):
        try:
            return AutomationCtrl.all()
        except Exception as e:
            logging.error(f"Error in All: {e}")

    def First(self, AutomationCtrl: Locator):
        try:
            return AutomationCtrl.first
        except Exception as e:
            logging.error(f"Error in First: {e}")

    def Last(self, AutomationCtrl: Locator):
        try:
            return AutomationCtrl.last
        except Exception as e:
            logging.error(f"Error in Last: {e}")
        