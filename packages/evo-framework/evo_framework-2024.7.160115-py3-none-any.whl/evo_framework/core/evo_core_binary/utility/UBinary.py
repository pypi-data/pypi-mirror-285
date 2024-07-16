import struct
import io
from evo_framework.entity import *
from evo_framework.core.evo_core_log.utility.IuLog import IuLog
from  evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
class UBinary:  
    __instance = None

    def __init__(self):
        if UBinary.__instance != None:
            raise Exception("ERROR_SINGLETON")
        else:
            UBinary.__instance = self
            self.mapEClass = {}
           
# -----------------------------------------------------------------------------
    @staticmethod
    def getInstance():
        if UBinary.__instance == None:
            uObject = UBinary()
            uObject.doInit()
           # loop = asyncio.get_running_loop()
           # asyncio.run_coroutine_threadsafe(cObject.doInit(), loop)
            #asyncio.run(cObject.doInit()) 
            
        return UBinary.__instance
# -----------------------------------------------------------------------------
    def doInit(self):
        try:
            self.offsetInt = 4
            self.offsetLong = 8
            self.offsetFloat = 4
            self.offsetDouble = 8
            '''
            self.DoSetEClass("ERequest","evo_framework.core.evo_core_api.entity.ERequest")
            self.DoSetEClass("EResponse","evo_framework.core.evo_core_api.entity.EResponse")
            self.DoSetEClass("EApiActionItem", "evo_framework.core.evo_core_api.entity.EApiActionItem")
            self.DoSetEClass("EApiAction", "evo_framework.core.evo_core_api.entity.EApiAction")
            #@TODO:Add from evo_package_shop
            self.DoSetEClass("EShop", "evo.evo_packages.evo_package_shop.entity.EShop")
            self.DoSetEClass("EShopProduct", "evo.evo_packages.evo_package_shop.entity.EShopProduct")
            '''
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise
        
        
    def DoSetEClass(self,idClassName:str, classPackage:str):
        self.mapEClass[idClassName] = classPackage
    
    
    def DoGetEClass(self,idClassName:str) -> str:
        return self.mapEClass.get(idClassName)
    

    def DoDelEClass(self,idClassName:str):
        del self.mapEClass[idClassName]
    
   
       

    def DoWriteString(self, value: str, stream: io.BytesIO):
        if value is None:
            stream.write(struct.pack('<l', -1))
        else:
            encoded = value.encode('UTF-8')
            stream.write(struct.pack('<l', len(encoded)) + encoded)

    def DoReadString(self, stream: io.BytesIO) -> str:
        length = struct.unpack('<l', stream.read(self.offsetInt))[0]
        if length == -1:
            return None
        return stream.read(length).decode('UTF-8')

    def DoWriteInt(self, value: int, stream: io.BytesIO):
        stream.write(struct.pack('<l', value if value is not None else -1))

    def DoReadInt(self, stream: io.BytesIO) -> int:
        return struct.unpack('<l', stream.read(self.offsetInt))[0]

    def DoWriteLong(self, value: int, stream: io.BytesIO):
        stream.write(struct.pack('<q', value if value is not None else -1))

    def DoReadLong(self, stream: io.BytesIO) -> int:
        return struct.unpack('<q', stream.read(self.offsetLong))[0]

    def DoWriteBytes(self, value: bytes, stream: io.BytesIO):
        if value is None:
            stream.write(struct.pack('<l', -1))
        else:
            stream.write(struct.pack('<l', len(value)) + value)

    def DoReadBytes(self, stream: io.BytesIO) -> bytes:
        length = struct.unpack('<l', stream.read(self.offsetInt))[0]
        if length == -1:
            return None
        return stream.read(length)

    def DoWriteFloat(self, value: float, stream: io.BytesIO):
        stream.write(struct.pack('<f', value if value is not None else -1.0))

    def DoReadFloat(self, stream: io.BytesIO) -> float:
        return struct.unpack('<f', stream.read(self.offsetFloat))[0]

    def DoWriteDouble(self, value: float, stream: io.BytesIO):
        stream.write(struct.pack('<d', value if value is not None else -1.0))

    def DoReadDouble(self, stream: io.BytesIO) -> float:
        return struct.unpack('<d', stream.read(self.offsetDouble))[0]

    def DoWriteBoolean(self, value: bool, stream: io.BytesIO):
        stream.write(struct.pack('<?', value if value is not None else False))

    def DoReadBoolean(self, stream: io.BytesIO) -> bool:
        return struct.unpack('<?', stream.read(1))[0]

   
    def DoWriteEObject(self, value, stream: io.BytesIO):
        if value is None:
            self.DoWriteInt(-1, stream)
        else:
            self.DoWriteInt(0, stream)
            self.DoWriteString(value.__class__.__name__, stream)
            
            value.toStream(stream)
        #stream.flush()

   
    def DoReadEObject(self,EClass, stream: io.BytesIO):
        offset = 4
        arrayByteLength = stream.read(offset)
        length = struct.unpack('<l', arrayByteLength[0:offset])[0]
        #print("\n DoReadEObject",length)
        if length == -1:
            return None
        else:
            className = self.DoReadString(stream)
            #print("\n DoReadEObject",className)
            eObject =  EClass()#self.toClass(className)
            eObject.fromStream(stream)
            return eObject
        
   
    def DoWriteMap(self, value: EvoMap, stream: io.BytesIO):
        #print("\n\nDoWriteMap",value)
        if value is None:
            self.DoWriteInt(-1, stream)
        else:
            self.DoWriteInt(len(value.__dictionary.items()), stream)
           # self.DoWriteString(value.name, stream)
            for key, value in value.__dictionary.items():
                self.DoWriteEObject(value,stream)
            
        #stream.flush()

    
    def DoReadMap(self, EClass, stream: io.BytesIO) -> EvoMap:
        offset = 4
        arrayByteLength = stream.read(offset)     
        count = struct.unpack('<l', arrayByteLength[0:offset])[0]

        #print("count:" + str(count))

        if count == -1:
            return None
        else:
            value = EvoMap()
            value.__dictionary.clear()   
           # value.name = self.DoReadString(stream)
            #print("\n DoReadMap",value.name,count)
            
            for i in range(0,count):
                eObject=self.DoReadEObject(EClass, stream)   
                #print(eObject)  
                value.doSet(eObject)
            return value
    
    '''
    def DoReadMap(self, stream: io.BytesIO) -> EvoMap:
        offset = 4
        arrayByteLength = stream.read(offset)     
        count = struct.unpack('<l', arrayByteLength[0:offset])[0]

        #print("count:" + str(count))

        if count == -1:
            return None
        else:
            value = EvoMap()
            value.dictionary.clear()   
           # value.name = self.DoReadString(stream)
            #print("\n DoReadMap",value.name,count)
            
            for i in range(0,count):
                eObject=self.DoReadEObject(stream)   
                #print(eObject)  
                value.doSet(eObject)
            return value
    '''
   
    def toClass(self, path: str):
        try:
                       
            if(path in self.mapEClass):
                path = self.mapEClass.get(path)
                
           # print("\ntoClass:",path)
                
            import importlib
            module_name, class_name = path.rsplit(".", 1)
            
            MyClass = getattr(importlib.import_module(path), class_name)
            instance = MyClass()
            return instance     
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        