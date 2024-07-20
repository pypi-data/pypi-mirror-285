
from  evo_framework.entity.EObject import EObject
from  evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
from evo_framework.core.evo_core_crypto.utility.IuCryptHash import IuCryptHash
class EFileChunk(EObject):
    #annotation
    def __init__(self):
        super().__init__()
        self.chunk:int = 0
        self.chunkTotal:int = 0
        self.extension:str = None
        self.length:int = 0   

    def toStream(self, stream):
        super().toStream(stream)
        self._doWriteInt(self.chunk, stream)
        self._doWriteInt(self.chunkTotal, stream)
        self._doWriteStr(self.extension, stream)
        self._doWriteInt(self.length, stream)
 
    def fromStream(self, stream):
        super().fromStream(stream)
        self.chunk = self._doReadInt(stream)
        self.chunkTotal = self._doReadInt(stream)
        self.extension = self._doReadStr(stream)
        self.length = self._doReadInt(stream)
    
    def toString(self) -> str:
        strReturn = "\n".join([
                            super().toString(),
                            f"chunk:{self.chunk}",
                            f"chunkTotal:{self.chunkTotal}",
                            f"extension:{self.extension}",
                            f"length:{self.length}"
                            ]) 
        return strReturn
    