#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git |
#========================================================================================================================================
from evo_framework.core.evo_core_log.utility.IuLog import *
from evo_framework.core.evo_core_api.entity import *
from evo_framework.core.evo_core_api.utility.IuApi import IuApi
from evo_framework.core.evo_core_yaml.utility.IuYaml import IuYAml
from evo_framework.core.evo_core_text.utility.IuText import IuText
from evo_framework.core.evo_core_crypto.utility.IuCryptChacha import IuCryptChacha
import os,sys
import importlib.metadata
import re
import yaml
import lz4
import base64
class UBridge:
    __instance = None

    def __init__(self):
        UBridge.__instance = self
        self.currentPathConfig = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------------------------------------------------------------------  
    @staticmethod
    def getInstance():
        if UBridge.__instance is None:
            cObject = UBridge()
            cObject.doInit()
        return UBridge.__instance

# ----------------------------------------------------------------------------------------------------------------------------------------  
    def doInit(self):
        try:
           pass       
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise Exception
# --------------------------------------------------------------------------------------------------------------------------------------        
    async def doGetEApiConfig(self, mapPeer:dict) -> EApiConfig:
        try:
            IuLog.doVerbose(__name__, f"mapPeer:\n{mapPeer}")
           
            eApiConfig = EApiConfig()
            eApiConfig.doGenerateID()
            
            mapPeerConfig = mapPeer["peer"]
            
            if mapPeerConfig is None:
                raise Exception("ERROR_NOT_VALID_PEER")
            
            label = mapPeerConfig["label"]
            if label is None:
                raise Exception("ERROR_NOT_VALID_label")
            
            description = mapPeerConfig["description"]
            if description is None:
                raise Exception("ERROR_NOT_VALID_description")
            
            urlLogo = mapPeerConfig["urlLogo"]
            if urlLogo is None:
                raise Exception("ERROR_NOT_VALID_urlLogo")
            
            enumEApiBridgeType = EnumEApiBridgeType.FASTAPI
            if "enumEApiBridgeType" in mapPeerConfig:
                enumEApiBridgeTypeStr = str(mapPeerConfig["enumEApiBridgeType"]).upper()
                if(enumEApiBridgeTypeStr == "FASTAPI"):
                    enumEApiBridgeType = EnumEApiBridgeType.FASTAPI
                elif(enumEApiBridgeTypeStr == "FASTAPI_WEBRTC"):
                    enumEApiBridgeType = EnumEApiBridgeType.FASTAPI_WEBRTC
                elif(enumEApiBridgeTypeStr == "WEBRTC"):
                    enumEApiBridgeType = EnumEApiBridgeType.WEBRTC
                elif(enumEApiBridgeTypeStr == "WEBSOCKET"):
                    enumEApiBridgeType = EnumEApiBridgeType.WEBSOCKET
                elif(enumEApiBridgeTypeStr == "EVORPC"):
                    enumEApiBridgeType = EnumEApiBridgeType.EVORPC
                else:
                    raise Exception(f"ERROR_NOT_VALID|{enumEApiBridgeTypeStr}|")
                
                
            enumApiVisibility = EnumApiVisibility.PRIVATE
            enumApiVisibilityStr = str(mapPeerConfig["enumApiVisibility"])
            if enumApiVisibilityStr is None:
                raise Exception("ERROR_NOT_VALID_enumApiVisibility")
            else:
                if enumApiVisibilityStr.upper() == "PUBLIC":
                    enumApiVisibility=EnumApiVisibility.PUBLIC
                elif enumApiVisibilityStr.upper() == "LOCAL":
                    enumApiVisibility=EnumApiVisibility.LOCAL
            
            #LOCAL, NGROK, PINNGY, CLOUDFLARE, REMOTEIP]
            enumApiTunnel = EnumApiTunnel.LOCAL
            enumApiTunnelStr = str(mapPeerConfig["enumApiTunnel"])
            if enumApiTunnelStr is None:
                raise Exception("ERROR_NOT_VALID_enumApiTunnel")
            else:
                if enumApiTunnelStr.upper() == "NGROK":
                    enumApiTunnel=EnumApiTunnel.NGROK
                elif enumApiTunnelStr.upper() == "PINNGY":
                    enumApiTunnel=EnumApiTunnel.PINGGY
                elif enumApiTunnelStr.upper() == "CLOUDFLARE":
                    enumApiTunnel=EnumApiTunnel.CLOUDFLARE
                elif enumApiTunnelStr.upper() == "REMOTEIP":
                    enumApiTunnel=EnumApiTunnel.CYBORGAI
               
                
            localAddress:str = None  
            if "localAddress" in mapPeerConfig:
                localAddress = mapPeerConfig["localAddress"]
                    
            if IuText.StringEmpty(localAddress):
                localAddress = "127.0.0.1"
                IuLog.doInfo(__name__, f"Use default localAddress {localAddress}")
                
            localPort = mapPeerConfig["localPort"]
            if localPort is None:
                localPort = 8081
                IuLog.doInfo(__name__, f"Use default localPort {str(localPort)}")
             
            remotePort = mapPeerConfig["remotePort"]
            if remotePort is None:
                remotePort = 8081
                IuLog.doInfo(__name__, f"Use default remotePort {str(remotePort)}")
                
            remoteUrl:str = None 
            if "remoteUrl" in mapPeerConfig:
                if not IuText.StringEmpty(mapPeerConfig["remoteUrl"]):
                    remoteUrl = mapPeerConfig["remoteUrl"]
        
            eApiConfig.enumEApiBridgeType = enumEApiBridgeType
            eApiConfig.label = label
            eApiConfig.description = description
            eApiConfig.urlLogo = urlLogo
            eApiConfig.enumApiVisibility = enumApiVisibility
            eApiConfig.enumApiTunnel = enumApiTunnel
            eApiConfig.localAddress = localAddress
            eApiConfig.localPort = localPort
            eApiConfig.remotePort = remotePort
            eApiConfig.remoteUrl = remoteUrl
     
            return eApiConfig  
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise Exception
# --------------------------------------------------------------------------------------------------------------------------------------       
    async def doAddCApi(self, mapPeer:dict):
        try:      
            mapApi= mapPeer["peer"]["api"]
            IuLog.doVerbose(__name__, f"mapApi:\n{mapApi}")
            for cApi, isEnabled in mapApi.items():
                try:
                    if isEnabled:                    
                        await IuApi.addCApi(cApi)        
                except Exception as exception:
                    IuLog.doException(__name__, exception)
                
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise Exception
# --------------------------------------------------------------------------------------------------------------------------------------
    async def doRunPeer(self, pathYaml:str):
        try:
            mapPeer = IuYAml.doLoad(f"{pathYaml}")  
            if mapPeer is None:
                raise Exception("ERROR_NOT_VALID_YAML")
            
            if mapPeer["LOG_LEVEL"] is not None:
                logLevel = mapPeer["LOG_LEVEL"]
                IuLog.doSetLevel(logLevel)
               
            IuLog.doVerbose(__name__, f"doRunPeer {pathYaml}")
            
            mapPeer = IuYAml.doLoad(f"{pathYaml}")   
            eApiConfigYaml = await self.doGetEApiConfig(mapPeer)
            
            cBridge = None
            if eApiConfigYaml.enumEApiBridgeType == EnumEApiBridgeType.FASTAPI or eApiConfigYaml.enumEApiBridgeType == EnumEApiBridgeType.FASTAPI_WEBRTC:
                await IuApi.doInstallPackage("evo_bridge_fastapi")
                from evo_bridge_fastapi.control.CFastApiServer import CFastApiServer
                cBridge = CFastApiServer.getInstance()
            else:
                raise Exception(f"ERROR_NOT_SUPPORTED|{eApiConfigYaml.enumEApiBridgeType}|")
            '''
            elif eApiConfigYaml.enumEApiBridgeType == EnumEApiBridgeType.WEBRTC:
                IuApi.doInstallPackage("evo_package_webrtc")
                from evo_package_webrtc.bridge.BWertcApi import BWertcApi
                cBridge = CFastApiServer.getInstance()
            elif eApiConfigYaml.enumEApiBridgeType == EnumEApiBridgeType.WEBSOCKET:
                IuApi.doInstallPackage("evo_package_webrtc")
                from evo_package_webrtc.bridge.BWertcApi import BWertcApi
                cBridge = CFastApiServer.getInstance()
            '''

            if cBridge is not None:
                eApiConfig = cBridge.eApiConfig
                eApiConfig.enumEApiBridgeType = eApiConfigYaml.enumEApiBridgeType
                eApiConfig.label = eApiConfigYaml.label
                eApiConfig.description = eApiConfigYaml.description
                eApiConfig.urlLogo = eApiConfigYaml.urlLogo
                eApiConfig.enumApiVisibility =eApiConfigYaml.enumApiVisibility
                eApiConfig.enumApiTunnel = eApiConfigYaml.enumApiTunnel
                eApiConfig.localAddress = eApiConfigYaml.localAddress
                eApiConfig.localPort = eApiConfigYaml.localPort
                eApiConfig.remotePort = eApiConfigYaml.remotePort
                eApiConfig.remoteUrl = eApiConfigYaml.remoteUrl
                
                IuLog.doDebug(__name__, f"{cBridge.eApiConfig}")
                
                #CApi add dynamic
                await self.doAddCApi(mapPeer)
            
                await cBridge.doRunServer()
            else:
                raise Exception(f"ERROR_CBRIDGE_NONE|{eApiConfigYaml.enumEApiBridgeType}|")
            
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise
# -------------------------------------------------------------------------------------------------------------------------------------- 
        def doDecryptSettings(self, secretEnv:str, strBase64:str) ->dict:
        
            if secretEnv is None:
                raise Exception("ERROR_CYBORGAI_SECRET_REQUIRED")

            if strBase64 is None:
                raise Exception("ERROR_strBase64_NONE")
            
            arraySecret=secretEnv.split("~")
            dataKey =  base64.b64decode(arraySecret[0])
            dataCompress = base64.b64decode(strBase64)
            dataDecompress = lz4.frame.decompress(dataCompress)
            dataPlain = IuCryptChacha.doDecryptCombined(dataKey, dataDecompress)
            strPlain= dataPlain.decode()
            
            return yaml.safe_load(strPlain)
# -------------------------------------------------------------------------------------------------------------------------------------- 
        def doGetTotp(self, pathEnv:str):
            try:
                envText = IuApi.doLoadFile(pathFile=pathEnv, isJson=False)
                
                if IuText.StringEmpty(envText):
                    IuLog.doError(__name__, f"ERROR_READ_FILE|{envText}")

                # Regular expression to extract the values of CYBORGAI_SECRET and CYBORGAI_SETTINGS
                secret_pattern = re.compile(r"CYBORGAI_SECRET='(.*?)'")
                settings_pattern = re.compile(r"CYBORGAI_SETTINGS='(.*?)'")

                # Extracting the values
                secretEnv = secret_pattern.search(envText).group(1)
                settingsBase64 = settings_pattern.search(envText).group(1)

                #print(secretEnv, settingsBase64)
                
                mapSettings = self.doDecryptSettings(secretEnv, settingsBase64)
                # print(mapSettings)
                
                print(mapSettings['CYBORGAI_ADMIN_OTP'])
            except Exception as exception:
                IuLog.doError(__name__, f"ERROR_TOTP|{exception}")
# -------------------------------------------------------------------------------------------------------------------------------------- 