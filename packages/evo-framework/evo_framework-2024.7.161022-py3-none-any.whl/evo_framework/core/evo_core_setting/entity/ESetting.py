from  evo_framework.entity.EObject import EObject

class ESetting(EObject):
    #annotation
    def __init__(self):
        super().__init__()
        self.isOutput:bool = False
        self.isUrl:bool = False
        self.typeExt:str = None
        self.data:bytes =None
          
    def toStream(self, stream):
        super().toStream(stream)
        self._doWriteBool(self.isOutput, stream)
        self._doWriteBool(self.isUrl, stream)
        self._doWriteStr(self.typeExt, stream)
        self._doWriteBytes(self.data, stream)
      
        
    def fromStream(self, stream):
        super().fromStream(stream)
        self.isOutput = self._doReadBool(stream)
        self.isUrl = self._doReadBool(stream)
        self.typeExt = self._doReadStr(stream)
        self.data = self._doReadBytes(stream)
       
    def __str__(self) -> str:
        strReturn = "\n".join([
                            super().__str__(),
                            f"isOutput:{self.isOutput}",
                            f"isUrl:{self.isUrl}",
                            f"typeExt:{self.typeExt}",
                            f"data:{self.data[:100]}",
                            ]) 
        return strReturn
