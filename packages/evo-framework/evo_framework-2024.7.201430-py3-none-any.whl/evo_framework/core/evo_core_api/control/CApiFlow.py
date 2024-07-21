logo_hd: str = """
#========================================================================================================================================
#                                                                                                                                       #
#                                 00000                                                                                                 #
#                                00   00                                                                                                #
#                 0000          0     0                                                                                                 #
#                800  007        0     0                                     0000                                                       #
#                0      7       00 00000                  4800000008         0  0                                      800008   6882    #
#                0     000  006 0 00                    580        08        0  0                                     80    0      8    #
#                800000  0000 00000                    28   00000   0000  0000  000000000000000000000000000000000    80  9  09  9  8    #
#                     000   0    00     8006           8   04   8000   0000  0        00        00              0    0   0   09 9  8    #
#                      0  0       0000000  083         8   8     8800   00  00  0000      0000   0   00  0000   0   00  000   0 9  8    #
#            58000800000          00    0    3         28  0088800 000  0   00  00 00     00 00  0  00   0000   0  00         089  8    #
#            8    00   00         00000     83          8     0     800    000   000   0   000   0  000         0  0   00000   08  8    #
#                  0000000      000   8000084           3880      008 00  00 0  0    0000      000  0 000   0   0  0  08   90   9  8    #
#            8     0     00000000                          68000008  00  00  000000000  00000000 0000 0  0000  00  0000     68088882    #
#            4800008         0  00                                   0   0                            00      00                        #
#                           000  000                                 00000                             00000000                         #
#                           0 0    0                                                                                                    #
#                           0      0                                                                                                    #
#                           00000000                                                                                                    #
#                                                                                                                                       #
# CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International       https://github.com/cyborg-ai-git     #
#========================================================================================================================================
"""
logo: str = """
#===================================================================================
#                                                                                  #
#                00                                                                #
#               0000                                                               #
#    0000       000                                                                #
#    00000     00               0000000      00                          000   00  #
#        0 0000                000   0000  00000000  0000 0000 00000    00000  00  #
#        0000000    000        00      000000000 00000  00000000  00   000 000 00  #
#  00  000000000 0000000       000  000 0000 000 00000  0000  000000   0000000 00  #
# 00000    0000      0           00000   00  000000  0000 00   00000  00    00000  #
#  000       00                         00                    000000               #
#            000                                                                   #
#            0000                                                                  #
#             00                                                                   #
#                                                                                  #
# CC BY-NC-ND 4.0                                                                  #
# Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International       #
#                                                                                  #
# https://github.com/cyborg-ai-git                                                 #
#                                                                                  #
#===================================================================================
"""
#12   assistant-get:
#                input: evo_package_assistant.entity.EAssistantQuery|ea156bed21c86c8a99ba7dc3df9f2355
#0f70389422ffdc819bf7e1da548cad0f
from evo_framework.core import *
from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
from evo_framework.core.evo_core_log.utility.IuLog import IuLog
from evo_framework.core.evo_core_api.entity.EApiConfig import EApiConfig
from evo_framework.core.evo_core_key.utility.IuKey import IuKey
from evo_framework.core.evo_core_crypto.utility.IuCryptEC import IuCryptEC
from evo_framework.core.evo_core_crypto.utility.IuCryptHash import IuCryptHash
from evo_framework.core.evo_core_log.utility.IuLog import IuLog
from evo_framework.core.evo_core_system.utility.IuSystem import IuSystem
from evo_framework.core.evo_core_convert.utility.IuConvert import IuConvert
from evo_framework.core.evo_core_setting.control.CSetting import CSetting
from evo_framework.core.evo_core_log.utility.IuLog import IuLog
from evo_framework.core.evo_core_api.entity.EActionTask import EActionTask
from evo_framework.core.evo_core_api.entity.ERequestInfo import ERequestInfo
from evo_framework.core.evo_core_api.entity.EApi import EApi
from evo_framework.core.evo_core_api.entity.EAction import EAction
from evo_framework.core.evo_core_api.entity.EnumApiAction import EnumApiAction
from evo_framework.core.evo_core_api.entity.EnumApiCrypto import EnumApiCrypto
from evo_framework.core.evo_core_api.entity.EnumApiCompress import EnumApiCompress
from evo_framework.core.evo_core_api.entity.EnumApiType import EnumApiType
from evo_framework.core.evo_core_api.entity.EnumApiVisibility import EnumApiVisibility
from evo_framework.core.evo_core_setting.utility.IuSettings import IuSettings
from evo_framework.core.evo_core_totp.utility.IuTotp import IuTotp
from evo_framework.core.evo_core_api.utility.IuApi import IuApi
from evo_framework.core.evo_core_file.utility.IuFile import IuFile
from evo_framework.core.evo_core_api.utility.IuApiRequest import IuApiRequest
from evo_framework.core.evo_core_api.utility.UApiClient import UApiClient
import requests
from functools import partial


# ---------------------------------------------------------------------------------------------------------------------------------------
# CApiFlow
# ---------------------------------------------------------------------------------------------------------------------------------------
class CApiFlow:
    __instance = None

    def __init__(self):
        if CApiFlow.__instance is not None:
            raise Exception("ERROR_SINGLETON")
        else:
            super().__init__()
            CApiFlow.__instance = self
            self.version = "2024.7.120000"
            self.path = os.path.dirname(os.path.abspath(__file__))
            self.eApiConfig: EApiConfig = EApiConfig()
            self.isSetEConfig: bool = False
            self.mapEAction: EvoMap = EvoMap()
            self.mapERequestInfo: EvoMap = EvoMap()
            self.isEndPoint = False
            self.strSettingsStart: str = None
            self.pathTemp: str = None

# ---------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getInstance():
        if CApiFlow.__instance is None:
            cObject = CApiFlow()
        return CApiFlow.__instance

# ---------------------------------------------------------------------------------------------------------------------------------------
    def doInit(self, isEndPoint=False):
        try:
            self.pathTemp = CSetting.getInstance().doGet("CYBORGAI_PATH_TMP")
            
            if self.pathTemp is None:
                self.pathTemp = "/tmp/cyborgai/chunk"
                IuLog.doWarning(__name__, f"PATH_TMP:{self.pathTemp}")
            
            IuFile.doCreateDirs(self.pathTemp)

            self.isEndPoint = isEndPoint
            CSetting.getInstance().doInit()
            # @TODO:add to PostQuantum Crypto
            self.eApiConfig.enumApiCrypto = EnumApiCrypto.ECC
            self.eApiConfig.os = IuSystem.get_os_info()
            print(logo)
            self.__doGenenerateCryptoKey()

            if not self.isEndPoint:
                pass
            else:
                IuLog.doVerbose(
                    __name__,
                    f"\nPUBLICK KEY:\n{IuConvert.toHex(self.eApiConfig.publicKey)}",
                )

        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise Exception

# ---------------------------------------------------------------------------------------------------------------------------------------
    async def doInitEApiConfig(self):
        try:
            IuLog.doVerbose(__name__, f"eApiConfig:\n{self.eApiConfig}\n")

            if not self.isEndPoint:
                if self.eApiConfig.enumApiVisibility != EnumApiVisibility.LOCAL:
                    await self.__doSetEApiConfig()
                   
                    IuLog.doVerbose(
                        __name__, f"cyborgai peerID:{  self.eApiConfig.cyborgaiToken}"
                    )
                else:
                    IuLog.doWarning(
                        __name__, "LOCAL PEER NO CALL TO REGISTER THE PEER"
                    )
                    self.eApiConfig.cyborgaiToken = f"{self.eApiConfig.remoteUrl}"

        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise Exception

# ---------------------------------------------------------------------------------------------------------------------------------------
    def doGenerateTotp(self) -> str:
        try:
            randBase32 = IuTotp.doGenerateRand()
            urlTotp = IuTotp.doGenerateUrl(
                randBase32, self.eApiConfig.label, f"CyborgAI_{self.eApiConfig.label}"
            )
            return urlTotp
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception

# ---------------------------------------------------------------------------------------------------------------------------------------
    def __doGenenerateCryptoKey(self):
        try:
            if self.eApiConfig.enumApiCrypto == EnumApiCrypto.ECC:
                privateKeyStr = CSetting.getInstance().doGet("CYBORGAI_SK")

                if privateKeyStr is None:
                    sk, pk = IuCryptEC.generate_key_pair()
                    IuLog.doVerbose(__name__, f"key generate :{sk} {pk}")
                    self.eApiConfig.secretKey = sk
                    self.eApiConfig.publicKey = pk.to_string()
                    self.eApiConfig.isFirstStart = True
                    # IuLog.doVerbose(__name__, f"\nSECRET KEY:\n{IuConvert.toBase64(sk.to_string())}\nATTENTION NOT SHARE")
                    skBase64 = IuConvert.toBase64(sk.to_string())
                    totp = self.doGenerateTotp()  
                    cyborgaiID = IuCryptHash.toSha256(self.eApiConfig.publicKey)
                    mapSettings = {"CYBORGAI_ID": cyborgaiID, "CYBORGAI_SK": skBase64, "CYBORGAI_ADMIN_OTP": totp}

                    self.eApiConfig.strBase64Start = IuSettings.doEncryptSettings(mapSettings)
                else:
                    sk, pk = IuCryptEC.get_key_pair(privateKeyStr)
                    IuLog.doVerbose(__name__, f"key regenerate :{sk} {pk}")
                    self.eApiConfig.secretKey = sk
                    self.eApiConfig.publicKey = pk.to_string()
                    self.eApiConfig.isFirstStart = False

            else:
                # TODO:add PQ crypto
                raise Exception(f"NOT_VALID_{self.eApiConfig.enumApiCrypto}")

            IuLog.doVerbose(__name__, f"sk,{self.eApiConfig.secretKey}")
            self.eApiConfig.id = IuCryptHash.toSha256Bytes(self.eApiConfig.publicKey)
            self.eApiConfig.doGenerateTime()

            if self.eApiConfig.secretKey is None:
                raise Exception("NOT_VALID_PRIVATE_KEY")

        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise

# ---------------------------------------------------------------------------------------------------------------------------------------
    async def __doSetEApiConfig(self) :
        try:
            IuLog.doVerbose(__name__, f"self{self.eApiConfig}")
            self.eApiConfig.cyborgaiToken = await UApiClient.getInstance().doSetPeer(self.eApiConfig)
        except Exception as exception:
            IuLog.doError(__name__, f"{exception}")
            raise

# ---------------------------------------------------------------------------------------------------------------------------------------
    async def onEActionInput(
        self, dataERequest: bytes, checkSign: bool = False
    ) -> Tuple[ERequestInfo, EAction | Any]:
        try:
            IuLog.doDebug(__name__, f"dataERequest length: {len(dataERequest)}")
            
            eActionInput = IuApiRequest.toEAction(data=dataERequest)

            IuLog.doVerbose(__name__, f"eActionInput:{eActionInput}")
            
            bytesChunk = eActionInput.input
            
            if  eActionInput.id not in self.mapERequestInfo.keys():          
                eRequestInfoTmp = ERequestInfo()
                eRequestInfoTmp.id = eActionInput.id
                eRequestInfoTmp.length = eActionInput.length
                eRequestInfoTmp.doStartTime()
                self.mapERequestInfo.doSet(eRequestInfoTmp)
                
            eRequestInfo:ERequestInfo = self.mapERequestInfo.doGet(eActionInput.id)
            
            lengthOffset = len(eActionInput.input)
            if  lengthOffset == eActionInput.length:
                eRequestInfo.isChunk = False
                eRequestInfo.chunkCount = 1             
                return (eRequestInfo, eActionInput)
                       
            else:
                file_path = f"{self.pathTemp}/{eActionInput.id.hex()}.eam"
                
                if os.path.exists(file_path):
                    # File exists, check its size
                    current_size = os.path.getsize(file_path)
                    if current_size != eActionInput.length:
                        # If the size is not correct, delete the file
                        os.remove(file_path)
                
                # Create and pre-allocate the file if it doesn't exist
                if not os.path.exists(file_path):
                    with open(file_path, 'wb') as file:
                        file.write(b'\0' * eActionInput.length)
                        IuLog.doDebug(__name__, f"file created: {file_path} {eActionInput.length}={os.path.getsize(file_path)}")
                
                async with aiofiles.open(file_path, mode='r+b') as file:
                    await file.seek(eActionInput.seek)
                    await file.write(bytesChunk)
                    await file.close()
               
                eRequestInfo.lengthCurrent += lengthOffset
                
                if  eRequestInfo.lengthCurrent == eActionInput.length:
                    async with aiofiles.open(file_path, mode="rb") as file:
                        dataInput = await file.read()
                        IuLog.doDebug(__name__, f"COMPLETE CHUNK: {len(dataInput)} {file_path}")
                    
                    #os.remove(file_path)
                    
                    eRequestInfo.isChunk=False  
                    eActionInput.input = dataInput
                    
                    return (eRequestInfo, eActionInput)
                
                else:
                    eRequestInfo.chunkCount += 1
                    eRequestInfo.isChunk=True
                    return (eRequestInfo, None)

        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise Exception

# ---------------------------------------------------------------------------------------------------------------------------------------
    async def onEActionOutput(self, eAction: EAction) -> bytes:
        try:
            IuLog.doDebug(__name__, f"onEActionOutput:{eAction}")
            isComplete = False
            if (
                eAction.enumApiAction == EnumApiAction.COMPLETE
                or eAction.enumApiAction == EnumApiAction.ERROR
                or eAction.enumApiAction == EnumApiAction.NONE
            ):
                isComplete = True
                
            eActionOutput = IuApiRequest.toEActionOutput(
                                                eAction = eAction,
                                                publicKey=self.eApiConfig.publicKey, 
                                                secretKey=self.eApiConfig.secretKey,
                                                )

            dataEResponse = eActionOutput.toBytes()
            
            if dataEResponse is None:
                raise Exception("ERROR_NOT_VALID|RESPONSE")
        
            eRequestInfo:ERequestInfo = self.mapERequestInfo.doGet(eActionOutput.id)
            IuLog.doVerbose(
                __name__, f"eResponse {len(dataEResponse)} {eActionOutput}"
            )

            if isComplete:
                eRequestInfo.doStopTime()
                IuLog.doVerbose(
                    __name__,
                    f"response:{eRequestInfo.id.hex()} time: {eRequestInfo.elapsedTimeStr} ",
                )
                self.mapERequestInfo.doDel(eRequestInfo.id)
            else:
                IuLog.doVerbose(
                    __name__,
                    f"response:{eRequestInfo.id.hex()} partial time: {eRequestInfo.doGetElapsedPartial()} ",
                )

            #@TODO:to EHeader chunk
           
            
            return eActionOutput.toBytes()

        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise

# ---------------------------------------------------------------------------------------------------------------------------------------
    def doGetEApi(self, action) -> EApi:
        try:
            eApi = self.eApiConfig.mapEApi.doGet(IuKey.generateId(action))

            if isinstance(eApi, EApi):
                return eApi

            else:
                raise Exception(f"ERROR_NOT_VALID|api|{action}")
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise 
# ---------------------------------------------------------------------------------------------------------------------------------------
    async def onAction(self, eApi: EApi, eActionTask: EActionTask):
        try:
            eActionTask.eActionOutput = await eApi.callback(eActionTask.eActionInput)
            return eActionTask.eActionOutput
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception

# ---------------------------------------------------------------------------------------------------------------------------------------
    async def onActionStream(self, eApi: EApi, eActionTask: EActionTask):
        try:
            async for eActionOutput in eApi.callback(eActionTask.eActionInput):
                yield eActionOutput
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise 

# ---------------------------------------------------------------------------------------------------------------------------------------
    async def onActionCallBack(self, eApi: EApi, eActionTask: EActionTask):
        try:
            eActionTask.eActionOutput = await eApi.callback(eActionTask.eActionInput)
            await eActionTask.evoCallback(eActionTask)
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise 

# ---------------------------------------------------------------------------------------------------------------------------------------
    async def onActionStreamCallback(self, eApi: EApi, eActionTask: EActionTask):
        try:
            async for eActionOutput in eApi.callback(eActionTask.eActionInput):
                eActionTask.eActionOutput = eActionOutput
                await eActionTask.evoCallback(eActionTask)
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise 

# ---------------------------------------------------------------------------------------------------------------------------------------
    async def doActionCallBack(self, eActionTask: EActionTask):
        try:
            IuLog.doDebug(__name__, f"OnActionThread: {eActionTask}")
            eApi = self.doGetEApi(eActionTask.action)
            
            self.run_in_background(self.onActionStreamCallback, eApi, eActionTask)

        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise 

# ---------------------------------------------------------------------------------------------------------------------------------------
    def start_async_loop(self, loop):
        try:
            asyncio.set_event_loop(loop)
            loop.run_forever()
        except Exception as exception:
            IuLog.doException(__name__, exception)

# ---------------------------------------------------------------------------------------------------------------------------------------
    def run_in_background(self, target, actionFunc, eActionTask: EActionTask):
        try:
            eActionTask.loop = asyncio.new_event_loop()
            eActionTask.threadBackground = threading.Thread(
                target=self.start_async_loop, args=(eActionTask.loop,), daemon=True
            )
            eActionTask.threadBackground.start()
            self.mapEAction.doSet(eActionTask)

            if asyncio.iscoroutinefunction(target):
                coroutine = partial(target, actionFunc, eActionTask)
                asyncio.run_coroutine_threadsafe(coroutine(), eActionTask.loop)
            else:
                raise TypeError(
                    f"target function {target.__name__} must be an asynchronous function"
                )
        except Exception as exception:
            IuLog.doException(__name__, exception)

# ---------------------------------------------------------------------------------------------------------------------------------------
    async def doStop(self):
        try:
            for eAction in self.mapEAction.__dictionary.values:
                try:
                    if isinstance(eAction, EActionTask):
                        if eAction.loop:
                            asyncio.run_coroutine_threadsafe(
                                eAction.loop.stop(), eAction.loop
                            )
                            eAction.threadBackground.join()
                            eAction.loop = None
                            eAction.threadBackground = None
                except Exception as exception:
                    IuLog.doException(__name__, exception)
        except Exception as exception:
            IuLog.doException(__name__, exception)

# ---------------------------------------------------------------------------------------------------------------------------------------
    async def doEAction(self, dataERequest) -> bytes:
        try:
            IuLog.doDebug(__name__, f"doEAction: {len(dataERequest)}")
            eRequestInfo, eActionInput = await self.onEActionInput(dataERequest, checkSign=True)
            IuLog.doDebug(__name__, f"eRequestInfo: {eRequestInfo} {eActionInput}")
            if not eRequestInfo.isChunk:
                try:
                    eApi = self.doGetEApi(eActionInput.action)
                    eActionTask = EActionTask()
                    eActionTask.id = eRequestInfo.id
                    eActionTask.action = eActionInput.action
                    eActionTask.eActionInput = eActionInput
                                  
                    async for eActionOutput in self.onActionStream(eApi, eActionTask):
                        IuLog.doDebug(__name__, f"eActionOutput:{eActionOutput}")
                        dataResponse = await self.onEActionOutput(eActionOutput)
                        IuLog.doInfo(
                            __name__,
                            f"{eActionInput.action!r} id:{eActionOutput.id.hex()} len:{len(dataResponse)} {eRequestInfo.doGetElapsedPartial()}",
                        )
                        yield dataResponse
                        
                except Exception as exception:
                    IuLog.doException(__name__, exception)
                    eActionInput.doSetError(f"{exception}")
                    dataResponse = await self.onEActionOutput(eActionInput)
                    yield dataResponse              
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise 
