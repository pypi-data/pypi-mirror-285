from enum import Enum, auto

class ActionConstants(Enum):
    CLICK = 1    
    SENDKEYS = auto()     
    HOVER = auto()    
    SELECTBYINDEX = auto()
    SELECTBYVALUE = auto()
    FOCUS = auto()
    OUTFOCUS = auto()
    TYPE = auto()
    CHECK = auto()
    UNCHECK = auto()
    
    INNERTEXT = auto()
    TEXTCONTENET = auto()
    ALLINNERTEXT = auto()
    ALLTEXTCONTENET = auto()
    GETPROPERTY = auto()    
    FOCUS = auto()
    DOUBLECLICK = auto()
    CLEAR = auto()
    FILL = auto()
    TYPE = auto()
    BLUR = auto()
    COUNT = auto()
    ALL = auto()
    FIRST = auto()
    LAST = auto()
    
    def description(self):
        return {
            ActionConstants.CLICK: "Click",
            ActionConstants.SENDKEYS: "Send Keys",
            ActionConstants.HOVER: "Hover",
            ActionConstants.SELECTBYINDEX: "Select by Index",
            ActionConstants.SELECTBYVALUE: "Select by Value",
            ActionConstants.FOCUS: "Focus",
            ActionConstants.OUTFOCUS: "Blur",
            ActionConstants.TYPE: "Type",
            ActionConstants.CHECK: "Check",
            ActionConstants.UNCHECK: "Uncheck",
            ActionConstants.INNERTEXT : "Get Inner Text of an element",
            ActionConstants.TEXTCONTENET: "Get Text Content",
            ActionConstants.ALLINNERTEXT: "Get all mathcing elements Inner Text",
            ActionConstants.ALLTEXTCONTENET: "Get all matching elements Text Content",
            ActionConstants.GETPROPERTY: "Get Property or Attribute of an element",    
            ActionConstants.FOCUS: "Focus on the element",
            ActionConstants.DOUBLECLICK: "Double Click",
            ActionConstants.CLEAR: "Clear contents",
            ActionConstants.FILL: "Fill in the text to locator",
            ActionConstants.TYPE: "Type",
            ActionConstants.BLUR: "Blur",
            ActionConstants.COUNT: "Get count of all matching elements",
            ActionConstants.ALL: "Returns the list of all matching elements",
            ActionConstants.FIRST: "Returns the first matching element",
            ActionConstants.LAST: "Returns the last matching element",
            }[self]

