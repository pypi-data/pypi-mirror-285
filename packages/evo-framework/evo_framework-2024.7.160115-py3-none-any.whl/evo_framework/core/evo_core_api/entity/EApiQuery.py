#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git | 
#========================================================================================================================================

from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

#========================================================================================================================================
"""EApiQuery

    EApiQuery defines the structure for querying within the EVO framework, including collection, object ID, and query string.
    
"""
class EApiQuery(EObject):

    VERSION:str="fc52f9a50c68071cc0e309bb8acf6f80867123fd0ad7215c89408e4db444ae52"

    def __init__(self):
        super().__init__()
        
        self.collection:str = None
        self.eObjectID:str = None
        self.query:str = None
  
    def toStream(self, stream):
        super().toStream(stream)
        
        self._doWriteStr(self.collection, stream)
        self._doWriteStr(self.eObjectID, stream)
        self._doWriteStr(self.query, stream)
        
    def fromStream(self, stream):
        super().fromStream(stream)
        
        self.collection = self._doReadStr(stream)
        self.eObjectID = self._doReadStr(stream)
        self.query = self._doReadStr(stream)
    
    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),
                            
                f"\tcollection:{self.collection}",
                f"\teObjectID:{self.eObjectID}",
                f"\tquery:{self.query}",
                            ]) 
        return strReturn
    