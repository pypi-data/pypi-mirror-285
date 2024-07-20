#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation	https://github.com/cyborg-ai-git # 
#========================================================================================================================================

from evo_framework.core import *
import lz4.frame
import gzip
from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
from evo_framework.core.evo_core_api.entity import *
from evo_framework.core.evo_core_api.entity.ERequestInfo import ERequestInfo
from evo_framework.core.evo_core_api.entity.EnumApiAction import EnumApiAction
from evo_framework.core.evo_core_api.entity.EnumApiCrypto import EnumApiCrypto
from evo_framework.core.evo_core_api.entity.EnumApiCompress import EnumApiCompress
from evo_framework.core.evo_core_api.utility.IuApi import IuApi
from evo_framework.core.evo_core_crypto import *
from evo_framework.core.evo_core_log import *
from evo_framework.core.evo_core_key import *
from evo_framework.core.evo_core_system import *

from evo_framework.core.evo_core_binary.utility.IuBinary import IuBinary
from evo_framework.core.evo_core_setting.control.CSetting import CSetting
from evo_framework.core.evo_core_text.utility.IuText import IuText
from PIL import Image
#import magic
import importlib
import subprocess

# ---------------------------------------------------------------------------------------------------------------------------------------
class IuApiRequest(object):
 # ---------------------------------------------------------------------------------------------------------------------------------------       
    @staticmethod
    def newEActionInput(id, 
                    publicKey ,
                    secretKey, 
                    data:bytes, 
                    enumApiCrypto:EnumApiCrypto = EnumApiCrypto.ECC, 
                    ) -> EAction:
        try:
          
            hashData = IuCryptHash.toSha256Bytes(data)
            sign = IuCryptEC.sign_data(hashData, secretKey)
                
            eAction = EAction()
            eAction.id = id
           
            eAction.pk = publicKey
            eAction.enumApiCrypto = EnumApiCrypto.ECC
            eAction.time = IuKey.generateTime()
            eAction.sign = sign
            
             # TODO:crypt data with eRequest chiper
            if len(data) > 10000024:
                eAction.enumApiCompress = EnumApiCompress.LZ4
                eAction.input = lz4.frame.compress(data)
            else:
                eAction.enumApiCompress = EnumApiCompress.NONE
                eAction.input = data
            
            return eAction
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception
        
 # ---------------------------------------------------------------------------------------------------------------------------------------      
    @staticmethod
    def toEActionInput(         
                    data:bytes, 
                    publicKey = None,
                    enumApiCrypto:EnumApiCrypto = EnumApiCrypto.ECC, 
                    enumApiCompress = EnumApiCompress.LZ4  
                    ) -> EAction:
        try:
            hashData = IuCryptHash.toSha256(data)
            IuLog.doVerbose(__name__, f"hashData:{hashData} data len{len(data)}")
            eActionInput = IuApi.toEObject(EAction(), data)
            
            IuLog.doVerbose(__name__, f"eActionIput:{eActionInput}")
            
            if isinstance(eActionInput, EAction):
                if len(eActionInput.id) < 32: #sha256
                    raise Exception(f"ERROR_NOT_VALID|{eActionInput.id!r}")

                # TODO:decrypt data with eRequest chiper
                
                if eActionInput.enumApiCompress == EnumApiCompress.NONE:
                    pass
                
                elif eActionInput.enumApiCompress == EnumApiCompress.LZ4:
                    eActionInput.input = lz4.frame.decompress(eActionInput.input)
                    
                elif eActionInput.enumApiCompress == EnumApiCompress.GZIP:
                    eActionInput.input = gzip.decompress(eActionInput.input)
                

                hash = IuCryptHash.toSha256Bytes(eActionInput.input)

                IuLog.doVerbose(
                    __name__,
                    f"CHUNK HASH: {eActionInput.id.hex()} {hash!r}",
                )
               
                if not eActionInput.pk:
                    raise Exception("ERROR_NOT_VALID|PK")
                
                IuLog.doVerbose(__name__, f"checkSign: {eActionInput}")
                
                signSha256 = IuCryptHash.toSha256Bytes(hash)
                
                
                #TODO:get from PKE
                if publicKey is None:
                    publicKey= eActionInput.pk
                
                isValid = IuCryptEC.verify_data(
                    hash, eActionInput.sign, publicKey
                )
                
                
                IuLog.doVerbose(
                    __name__,
                    f"checkSign: {eActionInput.id!r} {signSha256!r} isValid:{isValid}",
                )
                
                if not isValid:
                    raise Exception("ERROR_NOT_VALID|SIGN")
            
                return eActionInput
            
            else:
                raise Exception("ERROR_NOT_VALID|EAction")
        
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception
 # ---------------------------------------------------------------------------------------------------------------------------------------      
    @staticmethod
    def fromEActionOutput(         
                    data:bytes, 
                    publicKey = None,
                    enumApiCrypto:EnumApiCrypto = EnumApiCrypto.ECC, 
                    enumApiCompress = EnumApiCompress.LZ4  
                    ) -> EAction:
        try:
          
            eActionOutput = IuApi.toEObject(EAction(), data)

            if isinstance(eActionOutput, EAction):
                if len(eActionOutput.id) < 32: #sha256
                    raise Exception(f"ERROR_NOT_VALID|{eActionOutput.id!r}")

                # TODO:decrypt data with eRequest chiper
                
                if eActionOutput.enumApiCompress == EnumApiCompress.NONE:
                    pass
                
                elif eActionOutput.enumApiCompress == EnumApiCompress.LZ4:
                    eActionOutput.output = lz4.frame.decompress(eActionOutput.output)
                    
                elif eActionOutput.enumApiCompress == EnumApiCompress.GZIP:
                    eActionOutput.output = gzip.decompress(eActionOutput.output)
                

                hash = IuCryptHash.toSha256Bytes(eActionOutput.output)

                IuLog.doVerbose(
                    __name__,
                    f"CHUNK HASH: {eActionOutput.id.hex()} {hash!r}",
                )
               
                if not eActionOutput.pk:
                    raise Exception("ERROR_NOT_VALID|PK")
                
                IuLog.doVerbose(__name__, f"checkSign: {eActionOutput}")
                
                signSha256 = IuCryptHash.toSha256Bytes(hash)
                
                
                #TODO:get from PKE
                if publicKey is None:
                    publicKey= eActionOutput.pk
                
                isValid = IuCryptEC.verify_data(
                    hash, eActionOutput.sign, publicKey
                )
                
                
                IuLog.doVerbose(
                    __name__,
                    f"checkSign: {eActionOutput.id!r} {signSha256!r} isValid:{isValid}",
                )
                
                if not isValid:
                    raise Exception("ERROR_NOT_VALID|SIGN")
            
                return eActionOutput
            
            else:
                raise Exception("ERROR_NOT_VALID|EAction")
        
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception
              
 # ---------------------------------------------------------------------------------------------------------------------------------------       
    @staticmethod
    def toEActionOutput(
                    eAction:EAction, 
                    publicKey ,
                    secretKey, 
                    ) -> EAction:
        try:
            IuLog.doVerbose(__name__, f"toOutput:{eAction}")
            
            data= eAction.output
            hashData = IuCryptHash.toSha256Bytes(data)
            sign = IuCryptEC.sign_data(hashData, secretKey)
             
            #@TODO:chiper
            #get eActionInfo
            #dataCrypt= IUChacha.doEncrypt(chiper)
            dataCrypt = data
           
            #FOR SECURITY NEW 
            eActionOutput = eAction# EAction()
            #eActionOutput.id = eAction.id
            eActionOutput.pk = publicKey
            eActionOutput.enumApiCrypto = EnumApiCrypto.ECC
            eActionOutput.input = b''
            eActionOutput.sign = sign
            eActionOutput.seek = 0
            eActionOutput.length = len(eActionOutput.output)
 
            if len(data) > 100000024:
                eActionOutput.enumApiCompress = EnumApiCompress.LZ4
                eAction.output = lz4.frame.compress(dataCrypt)
            else:
                eActionOutput.enumApiCompress = EnumApiCompress.NONE
                eActionOutput.output = dataCrypt
            
            return eActionOutput
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception
                 
# ---------------------------------------------------------------------------------------------------------------------------------------      
    @staticmethod
    def newEAction(id:bytes, data:bytes, offsetStart:int=0, offsetEnd:int=-1, length:int=-1 ) -> EAction:
        try:  
            eHeader = EAction()
            eHeader.id = id
            eHeader.seek = offsetStart
           # eHeader.offsetEnd = offsetStart if offsetStart >0 else len(data)
            eHeader.length = length if length >0 else len(data)
            eHeader.input = data
            return eHeader     
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception

# ---------------------------------------------------------------------------------------------------------------------------------------      
    @staticmethod
    def toEAction(data:bytes) -> EAction:
        try:  
           # eHeader = IuApi.toEObject(EAction(), data )
            eAction = EAction() 
            eAction.fromBytes(data)
            
            IuLog.doVerbose(__name__, f"toEAction:{eAction}")
            
            if eAction.id is None:
                raise Exception("ERROR_NOT_VALID|EAction")

            if len(eAction.id) < 32: #sha256
                raise Exception(f"ERROR_NOT_VALID|EAction.id|{eAction.id!r}")
            
            #todo check security
            
            return eAction    
            
                
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception
# ---------------------------------------------------------------------------------------------------------------------------------------  
'''        
# ---------------------------------------------------------------------------------------------------------------------------------------      
    @staticmethod
    def toOutput(eActionInfo:ERequestInfo,
                    eAction:EAction, 
                    publicKey ,
                    secretKey,  
                    offsetStart:int=0, 
                    offsetEnd:int=-1, 
                    length:int=-1 ) -> bytes:
        try:  
            eActionOutput = IuApiRequest.toEActionOutput(eActionInfo,eAction,publicKey, secretKey )   
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception
'''    