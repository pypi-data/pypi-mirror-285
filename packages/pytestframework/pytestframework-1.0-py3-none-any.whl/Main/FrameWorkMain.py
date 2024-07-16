from Constants.ActionConstants import ActionConstants
from Constants.ValidationConstants import ValidationConstants
from Constants.SyncConstants import SyncConstants
from playwright.sync_api import Locator
from PerformActions.Action import Action
from PerformActions.Validation import Validation
from PerformActions.Synchronisation import Synchronisation

class FrameWorkMain:

    def __init__(self) -> None:
        self.action = Action()  
        self.synchroisation = Synchronisation()
        self.validation = Validation()    

    '''Method to do actions on automation controls'''
    def performAction(self ,AutomationControl: Locator, ActConstants : ActionConstants, OptionalParam = None):        
        if ActConstants == ActionConstants.CLICK:
            # click function
            self.action.Click(AutomationControl)                        
        elif ActConstants == ActionConstants.SENDKEYS:
            # send keys function
            if OptionalParam is not None:
                self.action.SendKeys(AutomationControl, OptionalParam)
            else:
                raise ValueError("OptionalParam is required for SENDKEYS action")            
        elif ActConstants == ActionConstants.CHECK:
            # check function for radio button
            self.action.Check(AutomationControl)
        elif ActConstants == ActionConstants.UNCHECK:
            # uncheck function for radio button
            self.action.Uncheck(AutomationControl)                 
        elif ActConstants == ActionConstants.INNERTEXT:
            return self.action.InnerText(AutomationControl)
            #return
        elif ActConstants == ActionConstants.TEXTCONTENET:
            return self.action.TextContent(AutomationControl)
            #return
        elif ActConstants == ActionConstants.ALLINNERTEXT:
            return self.action.AllInnerText(AutomationControl)
            #return
        elif ActConstants == ActionConstants.ALLTEXTCONTENET:
            return self.action.AllTextContent(AutomationControl)
            #return
        elif ActConstants == ActionConstants.GETPROPERTY:
            return self.action.GetProperty(AutomationControl)
            #have to return
        elif ActConstants == ActionConstants.FOCUS:
            self.action.Focus(AutomationControl)
        elif ActConstants == ActionConstants.DOUBLECLICK:
            self.action.DoubleClick(AutomationControl)
        elif ActConstants == ActionConstants.CLEAR:
            self.action.Clear(AutomationControl)
        elif ActConstants == ActionConstants.FILL:
            self.action.Fill(AutomationControl)
        elif ActConstants == ActionConstants.TYPE :
            self.action.Type(AutomationControl)
        elif ActConstants == ActionConstants.BLUR :
            self.action.Blur(AutomationControl)
        elif ActConstants == ActionConstants.COUNT :
            return self.action.Count(AutomationControl)
            #return
        elif ActConstants == ActionConstants.ALL :
            return self.action.All(AutomationControl)
            #return
        elif ActConstants == ActionConstants.FIRST: 
            self.action.First(AutomationControl)
            #return
        elif ActConstants == ActionConstants.LAST :
            self.action.Last(AutomationControl)
            #return
        else:
            # Invalid Enum
            pass        

    '''Method to wait for a condition on automation control'''
    def performSync(self, AutomationCtrl : Locator, syncConstants : SyncConstants, TimeoutInMillSec : int = None):
          
        if syncConstants == SyncConstants.WAITFORELEMENT:
            self.synchroisation.WaitForElement(AutomationCtrl, Timeout = TimeoutInMillSec)
        
        elif syncConstants == SyncConstants.WAITFORELEMENTVISIBLE:
            self.synchroisation.WaitForElementToBeVisible(AutomationCtrl, TimeoutInMillSec)
        
        elif syncConstants == SyncConstants.WAITFORELEMENTNOTVISIBLE:
            self.synchroisation.WaitForElementNotToBeVisible(AutomationCtrl, TimeoutInMillSec)
        
        elif syncConstants == SyncConstants.WAITFORELEMENTENABLED:
            self.synchroisation.WaitForElementToBeEnabled(AutomationCtrl, TimeoutInMillSec)
        
        elif syncConstants == SyncConstants.WAITFORELEMENTNOTENABLED:
            self.synchroisation.WaitForElementNotToBeEnabled(AutomationCtrl, TimeoutInMillSec)
        
        elif syncConstants == SyncConstants.WAITFORELEMENTEDITABLE:
            self.synchroisation.WaitForElementToBeEditable(AutomationCtrl, TimeoutInMillSec)
        
        elif syncConstants == SyncConstants.WAITFORELEMENTNOTEDITABLE:
            self.synchroisation.WaitForElementNotToBeEditable(AutomationCtrl, TimeoutInMillSec)
        
    '''Method to validate the property on automation control'''
    def performValidation(self, AutomationCtrl : Locator, validationConstants : ValidationConstants, propertyValue = None, propertyName = None):        
        
        if validationConstants == ValidationConstants.ISENABLED:
            self.validation.IsElementEnabled(AutomationCtrl, propertyValue)

        elif validationConstants == ValidationConstants.ISDISABLED:
            self.validation.IsElementDisabled(AutomationCtrl, propertyValue)

        elif validationConstants == ValidationConstants.ISEDITABLE:
            self.validation.IsElementEditable(AutomationCtrl, propertyValue)

        elif validationConstants == ValidationConstants.ISNOTEDITABLE:
            self.validation.IsElementNotEditable(AutomationCtrl, propertyValue)

        elif validationConstants == ValidationConstants.ISVISIBLE:
            self.validation.IsElementVisible(AutomationCtrl, propertyValue)

        elif validationConstants == ValidationConstants.ISHIDDEN:
            self.validation.IsElementNotVisible(AutomationCtrl, propertyValue)

        elif validationConstants == ValidationConstants.ISCHECKED:
            self.validation.IsElementChecked(AutomationCtrl, propertyValue)

        elif validationConstants == ValidationConstants.ISUNCHECKED:
            self.validation.IsElementNotchecked(AutomationCtrl, propertyValue)

        elif validationConstants == ValidationConstants.VerifyProperty:        
            self.validation.VerifyPropertyValue(AutomationCtrl, propertyName,  propertyValue)

        elif validationConstants == ValidationConstants.ContainsProperty:
            self.validation.ContainsPropertyValue(AutomationCtrl, propertyName, propertyValue)


    
    # Reports, logging
    # OBJECTREPO ~ xml [optional]
