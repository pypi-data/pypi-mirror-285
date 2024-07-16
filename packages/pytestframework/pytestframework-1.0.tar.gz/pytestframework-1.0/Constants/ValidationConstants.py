from enum import Enum, auto

class ValidationConstants(Enum):
    ISENABLED = 1
    ISDISABLED = auto() 
    ISEDITABLE = auto() 
    ISNOTEDITABLE = auto()
    ISVISIBLE = auto()
    ISHIDDEN = auto()
    ISCHECKED = auto()
    ISUNCHECKED = auto()
    VerifyProperty = auto()  
    ContainsProperty = auto()     

    def description(self):
        return {
            ValidationConstants.ISENABLED: "Is Enabled",
            ValidationConstants.ISEDITABLE: "Is Editable",
            ValidationConstants.ISVISIBLE: "Is visible",
            ValidationConstants.ISCHECKED: "Is Checked",
            ValidationConstants.ISDISABLED: "Is Disabled",
            ValidationConstants.VerifyProperty: "Verify any attribute/property value",
            ValidationConstants.ContainsProperty: "Verify any attribute/property contains value"
        }[self]