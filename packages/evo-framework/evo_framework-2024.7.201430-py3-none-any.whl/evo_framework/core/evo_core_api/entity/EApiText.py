#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git | 
#========================================================================================================================================

from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

#========================================================================================================================================
"""EApiText

    EApiText handles textual data within the EVO framework, including header, language, text content, and completeness or error status.
    
"""
class EApiText(EObject):

    VERSION:str="dbc89d3e2dbe14495d89b2f296b8ed972db21cb20af752590e1f93d06b23569b"

    def __init__(self):
        super().__init__()
        
        self.header:str = None
        self.language:str = None
        self.text:str = None
        self.isComplete:bool = None
        self.isError:bool = None
        self.tokenTot:int = 0
  
    def toStream(self, stream):
        super().toStream(stream)
        
        self._doWriteStr(self.header, stream)
        self._doWriteStr(self.language, stream)
        self._doWriteStr(self.text, stream)
        self._doWriteBool(self.isComplete, stream)
        self._doWriteBool(self.isError, stream)
        self._doWriteInt(self.tokenTot, stream)
        
    def fromStream(self, stream):
        super().fromStream(stream)
        
        self.header = self._doReadStr(stream)
        self.language = self._doReadStr(stream)
        self.text = self._doReadStr(stream)
        self.isComplete = self._doReadBool(stream)
        self.isError = self._doReadBool(stream)
        self.tokenTot = self._doReadInt(stream)
    
    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),
                            
                f"\theader:{self.header}",
                f"\tlanguage:{self.language}",
                f"\ttext:{self.text}",
                f"\tisComplete:{self.isComplete}",
                f"\tisError:{self.isError}",
                f"\ttokenTot:{self.tokenTot}",
                            ]) 
        return strReturn