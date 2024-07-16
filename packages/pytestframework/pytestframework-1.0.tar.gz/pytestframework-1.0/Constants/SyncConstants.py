from enum import Enum, auto

class SyncConstants(Enum):
    WAITFORELEMENT = 1
    WAITFORELEMENTVISIBLE = auto() 
    WAITFORELEMENTNOTVISIBLE = auto() 
    WAITFORELEMENTENABLED = auto()
    WAITFORELEMENTNOTENABLED = auto()
    WAITFORELEMENTEDITABLE = auto()
    WAITFORELEMENTNOTEDITABLE = auto()
    

    def description(self):
        return {
            SyncConstants.WAITFORELEMENT: "Wait for element",
            SyncConstants.WAITFORELEMENTVISIBLE: "Wait for element to be visible",
            SyncConstants.WAITFORELEMENTNOTVISIBLE: "Wait for element not to be visible",
            SyncConstants.WAITFORELEMENTENABLED: "Wait for element to be enabled",
            SyncConstants.WAITFORELEMENTNOTENABLED: "Wait for element not to be enabled",    
            SyncConstants.WAITFORELEMENTEDITABLE: "Wait for element to be editable",
            SyncConstants.WAITFORELEMENTNOTEDITABLE: "Wait for element not to be editable"                                  
        }[self]

