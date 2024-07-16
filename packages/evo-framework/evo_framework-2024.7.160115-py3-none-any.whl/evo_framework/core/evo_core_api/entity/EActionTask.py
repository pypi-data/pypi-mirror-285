from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
from evo_framework.core.evo_core_api.entity.EAction import EAction

class EActionTask(EObject):
    #annotation
    
    def __init__(self):
        super().__init__()
        self.action:str = ""
        self.eRequest = None
        self.eActionInput:EAction = None
        self.eActionOutput:EAction = None
        self.evoCallback = None
        self.task = None
        self.evoContext:EObject = None
        self.context = None
        self.loop = None
        self.threadBackground = None
        
    def __str__(self) -> str:
        strReturn = "\n".join([
                            super().__str__(),
                            f"action:{self.action}",
                            f"eApiMediaInput:{self.eActionInput}",
                            f"eApiMediaOutput:{self.eActionOutput}",
                            f"evoCallback:{self.evoCallback}",
                            f"task:{self.task}",
                            f"evoContext:{self.evoContext}",
                            f"context:{self.context}"
                            ]) 
        return strReturn