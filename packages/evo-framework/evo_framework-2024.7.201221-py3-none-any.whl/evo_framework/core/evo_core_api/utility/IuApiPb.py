
from evo_framework.core import *
import lz4.frame
from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_crypto import *
from evo_framework.core.evo_core_log import *
from evo_framework.core.evo_core_api.entity import *
from evo_framework.core.evo_core_key import *
from evo_framework.core.evo_core_system import *

class IuApiPb(object):
    @staticmethod
    def toBytes(eObjectInput:EObject) -> bytes :
            stream = io.BytesIO()
            eObjectInput.toStream(stream)
            data=bytes(stream.getbuffer())
            return data

    @staticmethod
    def toEObject(eObjectInput:EObject, data: bytes) -> EObject :
        if data != b'':
            stream = io.BytesIO(data)
            #eObject = typeClass()
            eObjectInput.fromStream(stream)
            return eObjectInput
        else:
            return None
        
    @staticmethod
    def FromERequest(data: bytes) -> ERequest:
        try:
         
            dataDecompressed = lz4.frame.decompress(data)
        
            if dataDecompressed != b'':
                eRequest = IuApi.toEObject(ERequest(),dataDecompressed)
                bytesChunk = eRequest.data
                hash = IuCryptHash.toSha256(bytesChunk)
                hashData = eRequest.hash.hex()
                IuLog.doVerbose(__name__,f"CHUNK HASH: {eRequest.chunk} {hash} == {hashData} {hashData==hash}")
                if hash != hashData:
                    raise Exception(f"NOT_VALID_HASH_{hash}")
                
                return eRequest
          
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
            
        
    @staticmethod
    def FromERequestNew(data: bytes) -> ERequest:
        try:
            
            #dataDecompressed = lz4.frame.decompress(data)            
            eRequest = IuApi.toEObject(ERequest(),data)
            if isinstance(eRequest,ERequest):
                if eRequest.enumCompress == EnumApiCompress.LZ4:
                    dataCompress = eRequest.data
                    dataDecompressed = lz4.frame.decompress(dataCompress)
                    
                if eRequest.enumCrypto == EnumApiCrypto.PQ:
                    #check sign, pk, chiper
                    pass
                
                eRequest.data = dataDecompressed
            return eRequest
          
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
    
    @staticmethod  
    def FromEResponseLZ4(data: bytes) -> EResponse:
       # pprint(data)
        dataDecompressed = lz4.frame.decompress(data)
        if dataDecompressed != b'':
            stream = io.BytesIO(dataDecompressed)
            eResponse = EResponse()
            eResponse.fromStream(stream)
            return eResponse
        else:
            return None

    @staticmethod
    def toEResponse(iD:str, result=0, api="",data=b'', typeApi:EnumApiType=EnumApiType.NONE)->bytes:
       
        eResponse = EResponse()
        eResponse.id = iD
        eResponse.result = result
       
        eResponse.data = data
        eResponse.enumApiType = typeApi
        stream = io.BytesIO()
        eResponse.toStream(stream)
        dataOut=bytes(stream.getbuffer())
       
        #IuBinary.DoWriteBytes()
        dataCompressed = lz4.frame.compress(dataOut)
       
        return dataCompressed
    
    @staticmethod
    def toBytesLZ4(eObjectInput:EObject) -> bytes :
            stream = io.BytesIO()
            eObjectInput.toStream(stream)
            data=bytes(stream.getbuffer())
            dataCompressed = lz4.frame.compress(data)   
            return dataCompressed
    
  
    @staticmethod
    def ToEResponseLZ4(eResponse:EResponse)->bytes:
        stream = io.BytesIO()
        eResponse.toStream(stream)
        data=bytes(stream.getbuffer())
        dataDecompressed = lz4.frame.compress(data)
        return dataDecompressed
   
    @staticmethod
    def ToERequestLZ4(eRequest:ERequest)->bytes:
        stream = io.BytesIO()
        eRequest.toStream(stream)
        data=bytes(stream.getbuffer())
        dataDecompressed = lz4.frame.compress(data)
        return dataDecompressed
    
    @staticmethod
    def toChunkLZ4(arrayByte:bytes)->bytes:
        dataCompressed = lz4.frame.compress(arrayByte)
        stream = io.BytesIO()
        IuBinary.DoWriteBytes(dataCompressed, stream)
        data=bytes(stream.getbuffer())
        return data
    
    @staticmethod
    def fromChunkLZ4(stream:io.BytesIO)->bytes:
        dataCompressed = IuBinary.DoReadBytes(stream)
        dataDecompressed = lz4.frame.decompress(dataCompressed)     
        return dataDecompressed
    
    @staticmethod
    def fromEObjectLZ4(eObjectInput:EObject, stream:io.BytesIO)->EObject:
        dataCompressed = IuBinary.DoReadBytes(stream)
        dataDecompressed = lz4.frame.decompress(dataCompressed)
        return IuApi.toEObject(eObjectInput,dataDecompressed)
#------------------------------------------------------------------
    @staticmethod
    def getFileType(eApiMedia:EApiMedia) -> str:
        try:
            pass
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
    @staticmethod
    async def toFile(eApiMedia:EApiMedia) -> str:
        try:
            if(eApiMedia is None):
                raise Exception("eApiMedia_null")
                    
            if(eApiMedia.typeExt is None):
                raise Exception("eApiMedia_typeInputExt_null")
            
            if eApiMedia.isUrl: 
                return eApiMedia.data.decode("UTF-8")       
            else:      
                idFile = IuKey.generateId() 
                if(eApiMedia.data is None):
                    raise Exception("eApiMedia.dataInput_null")
                 
                typeExt = f"{eApiMedia.typeExt}"
                
                if not typeExt.startswith(".") :
                    typeExt = f".{typeExt}"

                pathFile = f"/tmp/{idFile}{typeExt}"
                
                IuLog.doVerbose(__name__,f"pathFile: {eApiMedia.iD} {len(eApiMedia.data)} {pathFile}")
                
                async with aiofiles.open(pathFile, mode='wb') as file:
                    await file.write(eApiMedia.data)
                    await file.flush()
                '''
                with open(pathFile, 'wb') as file:
                    file.write(eApiMedia.dataInput)
                    file.flush()
                    
                '''
                    
                return pathFile

        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
        
    @staticmethod
    async def toPathProperty(eApiMedia:EApiMedia, key:str) -> str:
        try:
            if(eApiMedia is None):
                raise Exception("eApiMedia_null")

            eApiMediaInput = eApiMedia.mapParameter.DoGet(key)
            
            if(eApiMediaInput is None):
                    raise Exception(f"{key}_null")
            
            return await IuApi.toFile(eApiMediaInput)
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
    @staticmethod
    def toTextProperty(eApiMedia:EApiMedia, key:str) -> str:
        try:
            if(eApiMedia is None):
                raise Exception("eApiMedia_null")

            eApiMediaInput = eApiMedia.mapParameter.DoGet(key)
            
            if(eApiMediaInput is None):
                IuLog.doInfo(__name__,f"{eApiMedia} key:{key} is None")
                return None
                #    raise Exception(f"{key}_null")
            return IuApi.toText(eApiMediaInput)
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
    
    
    @staticmethod
    def getByteArray(eApiMedia:EApiMedia, key:str) -> bytes:
        try:
            if(eApiMedia is None):
                raise Exception("eApiMedia_null")

            eApiMediaInput = eApiMedia.mapParameter.DoGet(key)
            
            if(eApiMediaInput is None):
                IuLog.doInfo(__name__,f"{eApiMedia} key:{key} is None")
                return None
                
            return eApiMediaInput.data 
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
    
    
        
    @staticmethod
    def toIntMapPopertyInput(eApiMedia:EApiMedia, key:str) -> int:
        try:
            if(eApiMedia is None):
                raise Exception("eApiMedia_null")

            eApiMediaInput = eApiMedia.mapParameter.DoGet(key)
            
            if(eApiMediaInput is None):
                    raise Exception(f"{key}_null")
            
            return IuApi.toInt(eApiMediaInput)
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
    @staticmethod
    def toFileMapPopertyInput(eApiMedia:EApiMedia, key:str) -> str:
        try:
            if(eApiMedia is None):
                raise Exception("eApiMedia_null")

            eApiMediaInput = eApiMedia.mapParameter.DoGet(key)
            
            if(eApiMediaInput is None):
                    raise Exception(f"{key}_null")
            
            return IuApi.toFile(eApiMediaInput)
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
    @staticmethod
    def toByteArrayMapPopertyInput(eApiMedia:EApiMedia, key:str) -> bytes:
        try:
            if(eApiMedia is None):
                raise Exception("eApiMedia_null")

            eApiMediaInput = eApiMedia.mapParameter.DoGet(key)
            
            if(eApiMediaInput is None):
                    raise Exception(f"{key}_null")
            
            return IuApi.toByteArray(eApiMediaInput)
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
    @staticmethod
    def toText(eApiMedia:EApiMedia) -> str:
        try:
            if(eApiMedia is None):
                raise Exception("eApiMedia_null")
            
            if(eApiMedia.data is None):
                    raise Exception("eApiMedia.dataInput_null")
            
            text = eApiMedia.data.decode('utf-8')
            return text
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
    @staticmethod
    def toInt(eApiMedia:EApiMedia) -> int:
        try:
            if(eApiMedia is None):
                raise Exception("eApiMedia_null")
            
            if(eApiMedia.dataInput is None):
                    raise Exception("eApiMedia.dataInput_null")
            
            intVal = int.from_bytes(eApiMedia.data, byteorder='little')
            return intVal
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
        
    @staticmethod
    def toByteArray(pathFile:str) -> bytes:
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
        
    @staticmethod
    def toEFastMediaOutput(eApiMedia:EApiMedia, pathOutput, enumTypeApi=EnumApiType.COMPLETE) -> EApiMedia:
        try:
                     
            fileNameOutput, fileExtensionOutput = IuSystem.extract_details_from_url(pathOutput)        
            eApiMediaOutput = EApiMedia()
            eApiMediaOutput.iD = eApiMedia.iD
            eApiMediaOutput.doGenerateTime()
            #eApiMediaOutput.dataOutput = f"{fileNameOutput}{fileExtensionOutput}"
            eApiMediaOutput.enumApiType = enumTypeApi
            eApiMediaOutput.typeExt = fileExtensionOutput
            IuLog.doVerbose(__name__,f"eApiMedia.isUrlOutput: {eApiMedia.isUrl}")
                
            if (eApiMedia.isUrl):
                eApiMediaOutput.data = pathOutput.encode('UTF-8')
                '''
                source_path = pathOutput
                IuLog.doInfo(__name__,f"source_path:{source_path}")
                destination_path =  f"{CSetting.getInstance().eSettings.path_output}{fileNameOutput}{fileExtensionOutput}"
                IuLog.doInfo(__name__,f"destination_path:{destination_path}")
                shutil.copy(source_path, destination_path)

                IuLog.doVerbose(__name__,f"File copied from {source_path} to {destination_path}")
                
                urlFile = f"{CSetting.getInstance().eSettings.remoteUrl}/assets/{fileNameOutput}{fileExtensionOutput}"
                IuLog.doVerbose(__name__,f"urlFile:{urlFile}")
                
                eApiMediaOutput.data = urlFile.encode('UTF-8')
                '''
            else:
                eApiMediaOutput.data = IuApi.toByteArray(pathOutput)
            
            #os.remove(pathOutput)
            
            return eApiMediaOutput
   
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
         
    @staticmethod
    def toEFastMediaOutputText(eApiMedia:EApiMedia, output) -> EApiMedia:
        try: 
            eApiMediaOutput = EApiMedia()
            eApiMediaOutput.iD = eApiMedia.iD
            eApiMediaOutput.doGenerateTime()
           
            eApiMediaOutput.typeExt = "text"
            eApiMediaOutput.isUrl = eApiMedia.isUrl
            
            IuLog.doVerbose(__name__,f"eApiMedia.isUrlOutput: {eApiMedia.isUrl}")
                
            
            eApiMediaOutput.data = output.encode("UTF-8")
 
            #os.remove(pathOutput)
            
            return eApiMediaOutput
   
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
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