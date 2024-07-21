#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git | 
#========================================================================================================================================

import struct
import io
from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

from evo_framework.core.evo_core_api.entity.EnumApiAction import EnumApiAction
from evo_framework.core.evo_core_api.entity.EnumApiCrypto import EnumApiCrypto
from evo_framework.core.evo_core_api.entity.EnumApiCompress import EnumApiCompress
from evo_framework.core.evo_core_api.entity.EnumApiAction import EnumApiAction
from evo_framework.core.evo_core_key.utility.IuKey import IuKey
#========================================================================================================================================
"""EAction

    EAction describes an action within the EVO framework, including action type, input/output data, and error handling.
    
"""
class EAction(EObject):

    VERSION:str="9f474efe9285429321596424548861debf4e77f83a086f3e1f91a53da0b799e3"

    __struct_format = '<iqiiiiiiiiiii'
    __sizeHeader = struct.calcsize(__struct_format)
   
    def __init__(self):
        super().__init__()  
        #self.id:bytes = b''
        #self.time:int = 0
        self.seek:int = 0
        self.pk:bytes = b''
        self.sign:bytes = b''
        self.enumApiCrypto:EnumApiCrypto = EnumApiCrypto.ECC
        self.enumApiCompress:EnumApiCompress = EnumApiCompress.NONE
        self.enumApiAction:EnumApiAction = EnumApiAction.NONE
        self.action:str = ""  
        self.input:bytes = b''
        self.output:bytes = b''
        self.error:bytes = b''
        self.length:int = -1
    
    def toBytes(self):
        result = (struct.pack(
            self.__struct_format,
            len(self.id),
            self.time,
            self.seek,
            len(self.pk),
            len(self.sign),
            self.enumApiCrypto.value,
            self.enumApiCompress.value,
            self.enumApiAction.value,
            len(self.action.encode()),
            len(self.input),
            len(self.output),
            len(self.error),
            self.length if self.length >0 else len(self.input) #for chunk
        ))
        
        return result + self.id + self.pk + self.sign + self.action.encode() + self.input + self.output + self.error


    def fromBytes(self, packed_data):
        buffer = io.BytesIO(packed_data)
        (idLength, self.time, self.seek, pkLength, signLength, 
        enumApiCrypto, enumApiCompress, enumApiAction, 
        actionLength, inputLength, outputLength, errorLength, 
        self.length) = struct.unpack(self.__struct_format, buffer.read(self.__sizeHeader))
        
        if enumApiCrypto > 0:
            self.enumApiCrypto = EnumApiCrypto(enumApiCrypto)
        if enumApiCompress > 0:
            self.enumApiCompress = EnumApiCompress(enumApiCompress)
        if enumApiAction > 0:
            self.enumApiAction = EnumApiAction(enumApiAction)
        
        self.id = buffer.read(idLength) if idLength > 0 else b''
        self.pk = buffer.read(pkLength) if pkLength > 0 else b''
        self.sign = buffer.read(signLength) if signLength > 0 else b''
        self.action = buffer.read(actionLength).decode() if actionLength > 0 else ''
        self.input = buffer.read(inputLength) if inputLength > 0 else b''
        self.output = buffer.read(outputLength) if outputLength > 0 else b''
        self.error = buffer.read(errorLength) if errorLength > 0 else b''
        
        return self

    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),
                #f"\tid: {self.id!r}",
                #f"\ttime: {self.time}",       
                f"\tenumApiCrypto:{self.enumApiCrypto}",
                f"\tenumApiCompress:{self.enumApiCompress}",
                f"\tenumApiAction:{self.enumApiAction}",
                f"\tseek: {self.seek}",
                f"\tpk length:{len(self.pk) if self.pk else 'None'}",
                f"\tsign length:{len(self.sign) if self.sign else 'None'}",
                f"\taction:{self.action}",
                f"\tinput length:{len(self.input) if self.input else 'None'}",
                f"\toutput length:{len(self.output) if self.output else 'None'}",
                f"\terror:{self.error!r}",
                ]) 
        return strReturn
        
#<
#----------------------------------------------------------------------------------------------------------------------------------------
#EXTENSION
#----------------------------------------------------------------------------------------------------------------------------------------
    def doSetInput(self, eObject:EObject):
        from evo_framework.core.evo_core_api.utility.IuApi import IuApi
        self.input = eObject.toBytes()
        self.time = IuKey.generateTime()
#----------------------------------------------------------------------------------------------------------------------------------------
    def doGetInput(self, EObjectClass:type) -> EObject:
        from evo_framework.core.evo_core_api.utility.IuApi import IuApi
        return IuApi.toEObject(EObjectClass(), self.input)     
#----------------------------------------------------------------------------------------------------------------------------------------
    def doSetOutput(self, eObject:EObject):
        from evo_framework.core.evo_core_api.utility.IuApi import IuApi
        self.output = eObject.toBytes()
        self.time = IuKey.generateTime()
#----------------------------------------------------------------------------------------------------------------------------------------
    def doGetOutput(self, EObjectClass:type) -> EObject:
        from evo_framework.core.evo_core_api.utility.IuApi import IuApi
        return IuApi.toEObject(EObjectClass(), self.output)     
#----------------------------------------------------------------------------------------------------------------------------------------
    def doSetError(self,error:str):
        self.enumApiAction = EnumApiAction.ERROR
        self.isError = True
        self.error = error.encode()
        self.time = IuKey.generateTime()
#----------------------------------------------------------------------------------------------------------------------------------------
#>