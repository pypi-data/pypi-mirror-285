#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git | 
#========================================================================================================================================

from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

from evo_framework.core.evo_core_api.entity.EnumEApiFileType import EnumEApiFileType
#========================================================================================================================================
"""EApiFile

    EApiFile represents file-related data within the EVO framework, including file type, URL, name, extension, hash, and data content.
    
"""
class EApiFile(EObject):

    VERSION:str="e56e2edb1d4d40fa8b3449fa3b00c865e551697d2511a7fa3fa4fc0ff9b4293f"

    def __init__(self):
        super().__init__()
        
        self.enumEApiFileType:EnumEApiFileType = EnumEApiFileType.FILE
        self.isUrl:bool = None
        self.url:str = None
        self.name:str = None
        self.ext:str = None
        self.hash:bytes = None
        self.data:bytes = None
  
    def toStream(self, stream):
        super().toStream(stream)
        
        self._doWriteInt(self.enumEApiFileType.value, stream)
        self._doWriteBool(self.isUrl, stream)
        self._doWriteStr(self.url, stream)
        self._doWriteStr(self.name, stream)
        self._doWriteStr(self.ext, stream)
        self._doWriteBytes(self.hash, stream)
        self._doWriteBytes(self.data, stream)
        
    def fromStream(self, stream):
        super().fromStream(stream)
        
        self.enumEApiFileType = EnumEApiFileType(self._doReadInt(stream))
        self.isUrl = self._doReadBool(stream)
        self.url = self._doReadStr(stream)
        self.name = self._doReadStr(stream)
        self.ext = self._doReadStr(stream)
        self.hash = self._doReadBytes(stream)
        self.data = self._doReadBytes(stream)
    
    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),
                            
                f"\tenumEApiFileType:{self.enumEApiFileType}",
                f"\tisUrl:{self.isUrl}",
                f"\turl:{self.url}",
                f"\tname:{self.name}",
                f"\text:{self.ext}",
                f"\thash length:{len(self.hash) if self.hash else 'None'}",
                f"\tdata length:{len(self.data) if self.data else 'None'}",
                            ]) 
        return strReturn
#<
#----------------------------------------------------------------------------------------------------------------------------------------
#EXTENSION
#----------------------------------------------------------------------------------------------------------------------------------------
    async def toFile(self) -> str:
        from evo_framework.core.evo_core_api.utility.IuApi import IuApi
        return await IuApi.toFile(self.data, self.ext)     
#----------------------------------------------------------------------------------------------------------------------------------------
    async def fromFile(self, pathFile:str):
        from evo_framework.core.evo_core_api.utility.IuApi import IuApi
        from evo_framework.core.evo_core_text.utility.IuText import IuText
        self.data, self.ext, self.name = await IuApi.fromFile(pathFile) 
        
        if (not IuText.StringEmpty(self.ext)):
            if self.ext == ".png":
                self.enumEApiFileType = EnumEApiFileType.IMAGE
                
            elif self.ext == ".png":
                self.enumEApiFileType = EnumEApiFileType.IMAGE
                
            elif self.ext == ".jpg":
                self.enumEApiFileType = EnumEApiFileType.IMAGE
                
            elif self.ext == ".jpeg":
                self.enumEApiFileType = EnumEApiFileType.IMAGE
                
            elif self.ext == ".gif":
                self.enumEApiFileType = EnumEApiFileType.IMAGE
                
            elif self.ext == ".wav":
                self.enumEApiFileType = EnumEApiFileType.AUDIO
                
            elif self.ext == ".mp3":
                self.enumEApiFileType = EnumEApiFileType.AUDIO
                
            elif self.ext == ".mp4":
                self.enumEApiFileType = EnumEApiFileType.VIDEO
                
            elif self.ext == ".mov":
                self.enumEApiFileType = EnumEApiFileType.VIDEO
                
            elif self.ext == ".pdf":
                self.enumEApiFileType = EnumEApiFileType.PDF
                
            else:
                self.enumEApiFileType = EnumEApiFileType.FILE
                     
#----------------------------------------------------------------------------------------------------------------------------------------
#>

    