#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git # 
#========================================================================================================================================

from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

#========================================================================================================================================
"""EApi

    EApi outlines the API configuration details such as description, input, output, and required fields.
    
"""
class EApi(EObject):

    VERSION:str="b1df89b91207299e2d58191eaa0d9836640f13e2ea94af662f98e5265ccf53a0"

    def __init__(self):
        super().__init__()
        self.description:str = None
        self.input:str = None
        self.output:str = None
        self.required:str = None

#<
        #INTERNAL
        self.context = {}
        self.callback = None
        self.isEnabled:bool = True
#>
  
    def toStream(self, stream):
        super().toStream(stream)
        
        self._doWriteStr(self.description, stream)
        self._doWriteStr(self.input, stream)
        self._doWriteStr(self.output, stream)
        self._doWriteStr(self.required, stream)
        
    def fromStream(self, stream):
        super().fromStream(stream)
        
        self.description = self._doReadStr(stream)
        self.input = self._doReadStr(stream)
        self.output = self._doReadStr(stream)
        self.required = self._doReadStr(stream)
    
    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),
                            
                f"\tdescription:{self.description}",
                f"\tinput:{self.input}",
                f"\toutput:{self.output}",
                f"\trequired:{self.required}",
                            ]) 
        return strReturn
    