import struct
import io

from  evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
from evo_framework.core.evo_core_binary.utility.UBinary import UBinary
from evo_framework.core.evo_core_log.utility.IuLog import IuLog
from PIL import Image
class IuBinary(object):
   
    #for other languages 
    @staticmethod
    def DoSetEClass(idClassName:str, classPackage:str):
        UBinary.getInstance().DoSetEClass(idClassName, classPackage)
    
    @staticmethod
    def DoGetEClass(idClassName:str):
        return  UBinary.getInstance().DoGetEClass(idClassName)
    
    
    @staticmethod
    def DoDelEClass(idClassName:str):
        UBinary.getInstance().DoDelEClass(idClassName)
    
    
    @staticmethod
    def doWriteString(value: str, stream: io.BytesIO):
        UBinary.getInstance().DoWriteString(value,stream)
        
    @staticmethod
    def doReadString(stream: io.BytesIO) -> str:
        return UBinary.getInstance().DoReadString(stream)
   
    @staticmethod
    def doWriteInt(value: int, stream: io.BytesIO):
       UBinary.getInstance().DoWriteInt(value,stream)

    @staticmethod
    def doReadInt(stream: io.BytesIO) -> int:
       return UBinary.getInstance().DoReadInt(stream)

    @staticmethod
    def doWriteLong(value, stream: io.BytesIO):
       UBinary.getInstance().DoWriteLong(value,stream)
        
    @staticmethod
    def doReadLong(stream: io.BytesIO) -> int:
        return UBinary.getInstance().DoReadLong(stream)
    
    @staticmethod
    def doWriteByte(value: bytes, stream: io.BytesIO):
        UBinary.getInstance().DoWriteBytes(value,stream)
    
    @staticmethod
    def doReadByte(stream: io.BytesIO) -> bytes:
        return UBinary.getInstance().DoReadBytes(stream)

    @staticmethod
    def doWriteBytes(value: bytes, stream: io.BytesIO):
        UBinary.getInstance().DoWriteBytes(value,stream)
    
    @staticmethod
    def doReadBytes(stream: io.BytesIO) -> bytes:
        return UBinary.getInstance().DoReadBytes(stream)
    
    @staticmethod
    def doWriteFloat(value: float, stream: io.BytesIO):
        UBinary.getInstance().DoWriteFloat(value,stream)

    @staticmethod
    def doReadFloat(stream: io.BytesIO) -> float:
        return UBinary.getInstance().DoReadFloat(stream)
    
    @staticmethod
    def DoWriteDouble(value: float, stream: io.BytesIO):
        UBinary.getInstance().DoWriteDouble(value,stream)

    @staticmethod
    def DoReadDouble(stream: io.BytesIO) -> float:
        return UBinary.getInstance().DoReadDouble(stream)
    
    @staticmethod
    def doWriteBoolean(value: bool, stream: io.BytesIO):
       UBinary.getInstance().DoWriteBoolean(value,stream)

    @staticmethod
    def doReadBoolean(stream: io.BytesIO) -> bool:
        return UBinary.getInstance().DoReadBoolean(stream)

    @staticmethod
    def DoWriteEObject(value, stream: io.BytesIO):
        UBinary.getInstance().DoWriteEObject(value,stream)

    @staticmethod
    def DoReadEObject(ECLASS, stream: io.BytesIO):
       return UBinary.getInstance().DoReadEObject(ECLASS,stream)
        
    @staticmethod
    def doWriteMap(value: EvoMap, stream: io.BytesIO):
        UBinary.getInstance().DoWriteMap(value,stream)

    @staticmethod
    def doReadMap(ECLASS, stream: io.BytesIO) -> EvoMap:
        return UBinary.getInstance().DoReadMap(ECLASS,stream)
#------------------------------------------------------------------------------------------------------------
    @staticmethod
    def toIntBytes(value:int) -> bytes:
        try:
            return struct.pack('<l', value if value is not None else 0) 
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
    
    @staticmethod
    def fromIntBytes(data:bytes) -> int:
        try:
             return struct.unpack('<l', data)[0] 
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception    
# ---------------------------------------------------------------------------------------------------------------------------------------       
    @staticmethod
    def toFloatBytes(value:int) -> bytes:
        try:
            return struct.pack('<f', value if value is not None else 0.0) 
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
   
    @staticmethod
    def fromFloatBytes(data:bytes) -> float:
        try:
            return struct.unpack('<f', data)[0] 
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception        
# --------------------------------------------------------------------------------------------------------------------------------------- 
    @staticmethod
    def toLongBytes(self, value: int):
        try:
            return struct.pack('<q', value if value is not None else 0)
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception   
        
    
    @staticmethod
    def fromLongBytes(self, data:bytes) -> int:
        try:
            return struct.unpack('<q', data)[0]
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception   
# ---------------------------------------------------------------------------------------------------------------------------------------       
    @staticmethod
    def toDoubleBytes(self, value: float):
        try:
            return struct.pack('<d', value if value is not None else 0.0)
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception  
    
    @staticmethod
    def fromDoubleBytes(self, data:bytes) -> float:
        try:
            return struct.unpack('<d', data)[0]
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception   
# ---------------------------------------------------------------------------------------------------------------------------------------    
    @staticmethod
    def toBoolBytes(self, value: bool):
        try:
            struct.pack('<?', value if value is not None else False)
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception   
    
    @staticmethod
    def fromBoolBytes(self, data:bytes) -> bool:
        try:
            return struct.unpack('<?', data)[0]
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception   
        
# --------------------------------------------------------------------------------------------------------------------------------------- 
    def fromImageBytes(data:bytes, format="RGBA") -> Image:
        try:
            stream = io.BytesIO(data)
            image = Image.open(stream)
            image = image.convert(format)
            stream.close()
            return image
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
# --------------------------------------------------------------------------------------------------------------------------------------- 
    def toImageBytes(image:Image, format="PNG") -> bytes:
        try:
            stream = io.BytesIO()
            image.save(stream, format="PNG")
            data = stream.getvalue()
            stream.close()
            return data
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
# ---------------------------------------------------------------------------------------------------------------------------------------       
    @staticmethod
    def toStrBytes(value:str) -> bytes:
        try:
            return value.encode() 
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
# ---------------------------------------------------------------------------------------------------------------------------------------       
    @staticmethod
    def fromStrBytes(data:bytes) -> str:
        try:
            return data.decode()
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
#---------------------------------------------------------------------------------------------------------------------------------------      
    @staticmethod
    def toFileBytes(pathFile:str) -> bytes:
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

