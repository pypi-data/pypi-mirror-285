#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation	https://github.com/cyborg-ai-git # 
#========================================================================================================================================

from evo_framework.core import *
import lz4.frame
from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
from evo_framework.core.evo_core_api.entity import *

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
class IuApi(object):

 # ---------------------------------------------------------------------------------------------------------------------------------------       
    @staticmethod
    def newEAction(action:str) -> EAction:
        try: 
            eAction = EAction()
            eAction.doGenerateID()
            eAction.doGenerateTime()
            eAction.action= action
            return eAction      
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
# --------------------------------------------------------------------------------------------------------------------------------------- 
    @staticmethod
    async def newEApiFilePath(pathFile:str) -> EApiFile:
        try: 
            data, ext, name = await IuApi.fromFile(pathFile)
            eApiFile =EApiFile()
            eApiFile.doGenerateID()
            eApiFile.doGenerateTime()
            eApiFile.name = name
            eApiFile.data = data
            eApiFile.ext = ext
            eApiFile.hash = IuCryptHash.toSha256Bytes(eApiFile.data)
            return eApiFile
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception

# --------------------------------------------------------------------------------------------------------------------------------------- 
    @staticmethod
    async def newEApiFileBytes(data:bytes, name:str, ext:str) -> EApiFile:
        try: 
            eApiFile =EApiFile()
            eApiFile.doGenerateID()
            eApiFile.doGenerateTime()
            eApiFile.name = name
            eApiFile.data = data
            eApiFile.ext = ext
            eApiFile.hash = IuCryptHash.toSha256Bytes(eApiFile.data)
            return eApiFile
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception

# --------------------------------------------------------------------------------------------------------------------------------------- 
    @staticmethod
    async def newEApiText(text:str, language:str="en-US", isComplete:bool=True) -> EApiText:
        try: 
            eApiText = EApiText()
            eApiText.doGenerateID()
            eApiText.doGenerateTime()
            eApiText.text = text
            eApiText.language = language
            eApiText.isComplete = isComplete
            return eApiText
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
 # --------------------------------------------------------------------------------------------------------------------------------------- 
    @staticmethod
    async def addCApi(module:str):
        try:
            from evo_framework.core.evo_core_api.control.CApi import CApi
            
            if not module:
                raise Exception("ERROR_NONE_MODULE")
                
            arrayModule= module.split(".")
            className = arrayModule[-1]
            packageName = arrayModule[0]
            
            await IuApi.doInstallPackage(packageName)

            IuLog.doDebug(__name__, f"{module} {className}")
            ClassCApiAction = getattr(importlib.import_module(module), className)
            if ClassCApiAction:
                cApi=ClassCApiAction.getInstance()
                if isinstance(cApi,CApi):
                    cApi.doAddApi()
                else:
                    raise Exception("ERROR_IS_NOT_CAPI")         
            else:
                raise Exception("ERROR_NOT_VALID_MODULE_{module}")
        except Exception as exception:
            IuLog.doError(__name__, f"ERROR_INSTALL_PACKAGE|{packageName}")
            #IuLog.doException(__name__, exception)
            #raise 
# ---------------------------------------------------------------------------------------------------------------------------------------            
    """For local test package
    """    
    @staticmethod
    async def doInstallPackageLocal(packageName:str):
        pathPackageLocal = CSetting.getInstance().doGet("CYBORGAI_PATH_PACKAGE_LOCAL")
        
        if not IuText.StringEmpty(pathPackageLocal):
            pathAppend=f"{pathPackageLocal}/{packageName}-python/"
            IuLog.doInfo(__name__, f"doInstallPackageLocal:{pathAppend}")
            sys.path.append(pathAppend)
        
# ---------------------------------------------------------------------------------------------------------------------------------------            
    """For local test package
    """    
    @staticmethod
    async def doInstallPypi(packageName:str):
        IuLog.doVerbose(__name__, f"{packageName} installing...")
        result = subprocess.run(
        [sys.executable, "-m", "pip", "install","-U", "--no-cache-dir", packageName],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        if result.returncode == 0:
            IuLog.doVerbose(__name__, f"{packageName} installed successfully: {result.stdout}")
        else:
            raise Exception(f"ERROR_INSTALL_{packageName}_{result.stderr}") 
# ---------------------------------------------------------------------------------------------------------------------------------------       
    @staticmethod
    async def doInstallPackage(packageName:str):
        try:
            try:
                IuLog.doVerbose(__name__, f"{packageName}")
                __import__(packageName)
            except Exception as exception:
                try:
                    await IuApi.doInstallPackageLocal(packageName)
                    IuLog.doVerbose(__name__, f"{packageName}")
                    __import__(packageName)
                except Exception as exception:
                    await IuApi.doInstallPypi(packageName)
            else:
                IuLog.doVerbose(__name__, f"{packageName} installed")
        except Exception as exception:
            #IuLog.doError(__name__, f"ERROR_INSTALL_PACKAGE|{packageName}")
           # IuLog.doException(__name__, exception)
            raise 
# ---------------------------------------------------------------------------------------------------------------------------------------           
    @staticmethod
    def toEObject(eObject:EObject, data: bytes) -> EObject :
        if data is None:
            raise Exception("ERROR_DATA_REQUIRED")
        return eObject.fromBytes(data)
# ---------------------------------------------------------------------------------------------------------------------------------------        
    @staticmethod
    def fromByteArray(pathFile:str, data:bytes) -> bytes:
        try:
            IuLog.doVerbose(__name__,f"pathFile: {pathFile}")
            if(pathFile is None):
                raise Exception("pathFile_null")
            dataOutput = None
            with open(pathFile, 'rb') as file:
                    dataOutput = file.read()
                 
            IuLog.doVerbose(__name__,f"pathFile len: {len(dataOutput)}")
            
            return dataOutput   
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
# ---------------------------------------------------------------------------------------------------------------------------------------    
    @staticmethod
    async def toFile(data:bytes, typeExt:str) -> str:
        try:    
           
            idFile = IuKey.generateId().hex() 
            
            if(data is None):
                raise Exception("ERROR_data_null")
           
            if(typeExt is None):
                raise Exception("ERROR_typeExt_null")
            
            if not typeExt.startswith(".") :
                typeExt = f".{typeExt}"
            directoryOutput = "/tmp/cyborgai/file"
            
            if not os.path.exists(directoryOutput):
                os.makedirs(directoryOutput)
            
            pathFile = f"{directoryOutput}/{idFile}{typeExt}"
            
            IuLog.doVerbose(__name__,f"pathFile: {idFile} {len(data)} {pathFile}")
            
            async with aiofiles.open(pathFile, mode='wb') as file:
                await file.write(data)
                await file.flush()     
                return pathFile

        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
# ---------------------------------------------------------------------------------------------------------------------------------------      
    @staticmethod
    async def fromFile(pathFile: str) -> tuple:
        try:
            if pathFile is None:
                raise Exception("ERROR_fpathFile_null")

            IuLog.doVerbose(__name__, f"pathFile: {pathFile}")

            async with aiofiles.open(pathFile, mode='rb') as file:
                data = await file.read()
             
            arrayPathFile= pathFile.split('/')
            arrayFileName = arrayPathFile[-1].split(".")
            file_name = arrayFileName[0]
            file_extension = f".{arrayFileName[-1]}"
            
            # Check the MIME type
            #mime = magic.Magic(mime=True)
            #mime_type = mime.from_buffer(content)
            #IuLog.doVerbose(__name__, f"MIME type: {mime_type}")

            return data, file_extension, file_name

        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise
        
# ---------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def doLoadFile(pathFile, isJson=True):
        try:
            IuLog.doDebug(__name__,f"pathFile:{pathFile} isJson:{isJson}")
            with open(pathFile, 'r',encoding='utf-8') as fileData:
                if isJson:
                   return json.load(fileData) 
                else:
                    return fileData.read()   
            
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception  
# ---------------------------------------------------------------------------------------------------------------------------------------