#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git # 
#========================================================================================================================================

from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

from evo_framework.core.evo_core_api.entity.EnumApiCrypto import EnumApiCrypto
import time

#========================================================================================================================================
"""ERequest

    ERequestInfo DESCRIPTION
    
"""
class ERequestInfo(EObject):

    VERSION:str="b9427bfc10a33401d5c9381fc699e0b53f5851ca34b02c1ab9ea18bbe0751201"

    def __init__(self):
        super().__init__()    
        #INTERNAL
        self.enumApiCrypto:EnumApiCrypto = EnumApiCrypto.ECC
       # self.pk:bytes = None
        #self.cipher:bytes = None
        self.startTime = None
        self.endTime = None
        self.elapsedTime = None
        self.elapsedTimeStr:str = None
        self.isChunk:bool = False
        self.chunkCount:int = 0
        self.lengthCurrent:int = 0
        self.length:int = 0
       

    def __str__(self) -> str:
        strReturn = "\n".join([
                super().__str__(),            
                f"\tenumApiCrypto:{self.enumApiCrypto}",
                #f"\tpk length:{len(self.pk) if self.pk else 'None'}",
                #f"\tcipher length:{len(self.cipher) if self.cipher else 'None'}",
                f"\tstartTime: {self.startTime}",
                f"\tendTime: {self.endTime}",
                f"\telapsedTimeStr: {self.elapsedTimeStr}",  
                f"\tlengthCurrent: {self.lengthCurrent}",
                f"\tlength: {self.length}",   
                f"\tchunkCount: {self.chunkCount}",   
                f"\tisChunk: {self.isChunk}",   
                ]) 
        return strReturn

#<
#Extension

    def doStartTime(self):
        self.startTime = time.time_ns()
            
    def doStopTime(self):
        self.endTime =time.time_ns()
        self.elapsedTime = self.endTime - self.startTime
        elapsedTimeSecond = self.elapsedTime / 1e9
        self.elapsedTimeStr =  f"{elapsedTimeSecond:.9f} s"
        
    def doGetElapsedPartial(self)->str:
        elapsedTimeTmp = time.time_ns() - self.startTime
        elapsedTimeSecond = elapsedTimeTmp / 1e9
        return f"{elapsedTimeSecond:.9f} s"
#>