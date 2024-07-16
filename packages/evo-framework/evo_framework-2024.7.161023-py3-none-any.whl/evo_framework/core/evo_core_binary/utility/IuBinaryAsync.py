import struct
import io

from  evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
class IuBinaryAsync(object):

    @staticmethod
    async def DoWriteString(value: str, stream: io.BytesIO):
        if value == None:
            await IuBinaryAsync.DoWriteInt(-1, stream)
        else:
            arrayByte = value.encode('UTF-8')
            arrayByteLength = struct.pack('<l', len(arrayByte))
            await stream.write(arrayByteLength + arrayByte)
        await stream.flush()
        
    @staticmethod
    async def DoReadString(stream: io.BytesIO) -> str:
        offset = 4
        arrayByteLength = await stream.read(offset)
        length = struct.unpack('<l', arrayByteLength[0:offset])[0]
        if length == -1:
            return None
        else:
            arrayValue = await stream.read(length)
            return arrayValue.decode('UTF-8')
    @staticmethod
    async def DoWriteInt(value: int, stream: io.BytesIO):
        arrayByteLength = struct.pack('<l', value)
        await stream.write(arrayByteLength)
        await stream.flush()

    @staticmethod
    async def DoReadInt(stream: io.BytesIO) -> int:
        offset = 4
        arrayByteLength = await stream.read(offset)
        return struct.unpack('<l', arrayByteLength[0:offset])[0]

    @staticmethod
    async def DoWriteLong(value, stream: io.BytesIO):
        arrayByteLength = struct.pack('<q', value)
        await stream.write(arrayByteLength)
        await stream.flush()
        
    @staticmethod
    async def DoReadLong(stream: io.BytesIO) -> int:
        offset = 8
        arrayByteLength = await stream.read(offset)
        return struct.unpack('<q', arrayByteLength[0:offset])[0]

    @staticmethod
    async def DoWriteBytes(value: bytes, stream: io.BytesIO):
        if value is None:
            arrayByteLength = struct.pack('<l', -1)
            await stream.write(arrayByteLength)
        else:
            arrayByteLength = struct.pack('<l', len(value))
            await stream.write(arrayByteLength+value)
        await stream.flush()
    
    @staticmethod
    async def DoReadBytes(stream: io.BytesIO) -> bytes:
        offset = 4
        arrayByteLength = await stream.read(offset)
        length = struct.unpack('<l', arrayByteLength[0:offset])[0]
        if length == -1:
            return None
        else:
            arrayValue = await stream.read(length)
            return arrayValue
    @staticmethod
    async def DoWriteFloat(value: float, stream: io.BytesIO):
        arrayByteLength = struct.pack('<f', value)
        await stream.write(arrayByteLength)
        await stream.flush()

    @staticmethod
    async def DoReadFloat(stream: io.BytesIO) -> float:
        offset = 4
        arrayByteLength = await stream.read(offset)
        return struct.unpack('<f', arrayByteLength[0:offset])[0]
    
    @staticmethod
    async def DoWriteDouble(value: float, stream: io.BytesIO):
        arrayByteLength = struct.pack('<d', value)
        await stream.write(arrayByteLength)
        await stream.flush()

    @staticmethod
    async def DoReadDouble(stream: io.BytesIO) -> float:
        offset = 8
        arrayByteLength = await stream.read(offset)
        return struct.unpack('<d', arrayByteLength[0:offset])[0]
    
    @staticmethod
    async def DoWriteBoolean(value: bool, stream: io.BytesIO):
        arrayByte = struct.pack('<?', value)
        await stream.write(arrayByte)
        await stream.flush()

    @staticmethod
    async def DoReadBoolean(stream: io.BytesIO) -> bool:
        arrayByte = await stream.read(1)
        return struct.unpack('<?', arrayByte)[0]

    @staticmethod
    async def DoWriteEObject(value, stream: io.BytesIO):
        if value == None:
            await IuBinaryAsync.DoWriteInt(-1, stream)
        else:
            await IuBinaryAsync.DoWriteInt(0, stream)
            await IuBinaryAsync.DoWriteString(value.__class__.__module__, stream)
            value.ToStream(stream)
        await stream.flush()

    @staticmethod
    async def DoReadEObject(stream: io.BytesIO):
        offset = 4
        arrayByteLength = await stream.read(offset)
        length = struct.unpack('<l', arrayByteLength[0:offset])[0]
        #print("\n DoReadEObject",length)
        if length == -1:
            return None
        else:
            className = await IuBinaryAsync.DoReadString(stream)
            #print("\n DoReadEObject",className)
            eObject = await IuBinaryAsync.toClass(className)
            eObject.FromStream(stream)
            return eObject
        
    @staticmethod
    async def DoWriteMap(value: EvoMap, stream: io.BytesIO):
        #print("\n\nDoWriteMap",value)
        if value == None:
            await IuBinaryAsync.DoWriteInt(-1, stream)
        else:
            await IuBinaryAsync.DoWriteInt(len(value.__dictionary.items()), stream)
            await IuBinaryAsync.DoWriteString(value.name, stream)
            for key, value in value.__dictionary.items():
                await IuBinaryAsync.DoWriteEObject(value,stream)
            
        await stream.flush()

    @staticmethod
    async def DoReadMap(stream: io.BytesIO) -> EvoMap:
        offset = 4
        arrayByteLength = await stream.read(offset)     
        count = struct.unpack('<l', arrayByteLength[0:offset])[0]

        #print("count:" + str(count))

        if count == -1:
            return None
        else:
            value = EvoMap()
            value.__dictionary.clear()   
            value.name = await IuBinaryAsync.DoReadString(stream)
            #print("\n DoReadMap",value.name,count)
            
            for i in range(0,count):
                eObject=await IuBinaryAsync.DoReadEObject(stream)   
                print(eObject)  
                value.doSet(eObject)
            return value
    
    @staticmethod
    async def toClass(path: str):
        try:
            
           # print("\ntoClass:",path)
            #@TODO:to fix 
            if (path=="EApiMedia"):
                path="evo.evo_packages.evo_package_fastapi.entity.EApiMedia"
                
            if (path=="EShop"):
                path="evo.evo_packages.evo_package_shop.entity.EShop"
                
            if (path=="EShopProduct"):
                path="evo.evo_packages.evo_package_shop.entity.EShopProduct"
            
            import importlib
            module_name, class_name = path.rsplit(".", 1)
            
            MyClass = getattr(importlib.import_module(path), class_name)
            instance = MyClass()
            return instance     
        except ImportError:
            print('Module does not exist')
        return None
