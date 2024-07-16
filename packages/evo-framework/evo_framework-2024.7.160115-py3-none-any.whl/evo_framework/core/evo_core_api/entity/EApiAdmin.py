#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git | 
#========================================================================================================================================

from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

#========================================================================================================================================
"""EApiAdmin

    EApiAdmin manages administrative data within the EVO framework, such as TOTP and tokens.
    
"""
class EApiAdmin(EObject):

    VERSION:str="943c363685bc38654dba7aac000ce9bcd4886ea26b901629a252aa053cbfb10e"

    def __init__(self):
        super().__init__()
        
        self.totp:bytes = None
        self.token:bytes = None
        self.password:bytes = None
  
    def toStream(self, stream):
        super().toStream(stream)
        
        self._doWriteBytes(self.totp, stream)
        self._doWriteBytes(self.token, stream)
        self._doWriteBytes(self.password, stream)
        
    def fromStream(self, stream):
        super().fromStream(stream)
        
        self.totp = self._doReadBytes(stream)
        self.token = self._doReadBytes(stream)
        self.password = self._doReadBytes(stream)
    
    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),
                            
                f"\ttotp length:{len(self.totp) if self.totp else 'None'}",
                f"\ttoken length:{len(self.token) if self.token else 'None'}",
                f"\tpassword length:{len(self.password) if self.password else 'None'}",
                            ]) 
        return strReturn
    