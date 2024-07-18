from functools import singledispatch
import struct
import unittest
import sys
import os
import base64
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path + "/../../../")

from evo_framework import *
from functools import singledispatchmethod
import struct
import timeit
import io



class IuBinaryN():
    '''
    @singledispatchmethod
    @staticmethod
    def to_bytes(value):
        raise NotImplementedError(f"Cannot convert type {type(value).__name__} to bytes")

    @to_bytes.register
    @staticmethod
    def _(value: int) -> bytes:
        return value.to_bytes((value.bit_length() + 7) // 8 if value != 0 else 1, byteorder='little', signed=True)

    @to_bytes.register
    @staticmethod
    def _(value: bool) -> bytes:
        return bytes([value])

    @to_bytes.register
    @staticmethod
    def _(value: float) -> bytes:
        # Use little-endian format for floating points
        return struct.pack('<d', value)
    
    @to_bytes.register
    @staticmethod
    def _(value: str) -> bytes:
        return value.encode('utf-8')
    '''
    @staticmethod
    def toBytes(data_type,value) ->bytes:
        if data_type == int:
            if value is None:
                value = -1
            return struct.pack('<l', value)
            #return value.to_bytes((value.bit_length() + 7) // 8 if value != 0 else 1, byteorder='little', signed=True)
        elif data_type == bool:
            return struct.pack('<?', value)
        elif data_type == float:
            # Assume little-endian double precision float
             return struct.pack('<d', value)
        elif data_type == str:
            # Assume UTF-8 encoded string
            return value.encode('utf-8')
        else:
            raise ValueError(f"Unsupported type specified: {data_type}")
    
    @staticmethod
    def fromBytes(data: bytes, data_type):
        if data_type == int:
            # Assume little-endian integer
            offset = 4
            return struct.unpack('<l', data[0:offset])[0]
        elif data_type == bool:
            # Assume the first byte represents the boolean as 0 or 1
            return bool(data[0]) # struct.unpack('<?', data)[0]
        elif data_type == float:
            # Assume little-endian double precision float
            return struct.unpack('<d', data)[0]
        elif data_type == str:
            # Assume UTF-8 encoded string
            return data.decode('utf-8')
        else:
            raise ValueError(f"Unsupported type specified: {data_type}")

    
class TestEvoCoreBinary(unittest.IsolatedAsyncioTestCase):
     
    async def asyncSetUp(self):
        self.IS_DEBUG = True
        self.COUNT_TEST:int = 100000
        
    async def test_timit(self):
        IuLog.doInfo(__name__, "test_timit")
       
        
        print(
            'timit_serialize_int:',
            timeit.timeit(
                lambda: (self.timit_serialize_int()),
                number=self.COUNT_TEST,
            ),
        )
        
        print(
            'timit_serialize_bool:',
            timeit.timeit(
                lambda: (self.timit_serialize_bool()),
                number=self.COUNT_TEST,
            ),
        )
        
        print(
            'timit_serialize_float:',
            timeit.timeit(
                lambda: (self.timit_serialize_float()),
                number=self.COUNT_TEST,
            ),
        )
        
         
        print(
            'timit_serialize_str:',
            timeit.timeit(
                lambda: (self.timit_serialize_str()),
                number=self.COUNT_TEST,
            ),
        )
          
    def timit_serialize_int(self):   
        value = 1024
        int_bytes_in = IuBinaryN.toBytes(int,value)
        int_bytes_out = IuBinaryN.fromBytes(int_bytes_in, int)
        self.assertEqual(value, int_bytes_out)
        
       
    def timit_serialize_bool(self):   
        value = True
        bool_bytes_in = IuBinaryN.toBytes(bool,value)
        bool_bytes_out = IuBinaryN.fromBytes(bool_bytes_in, bool)
        self.assertEqual(value, bool_bytes_out)
        
         
    def timit_serialize_float(self):   
        value = 3.14
        float_bytes_in = IuBinaryN.toBytes(float,value)
        float_bytes_out = IuBinaryN.fromBytes(float_bytes_in, float)
        self.assertEqual(value, float_bytes_out)
         
    def timit_serialize_str(self):   
        value="str_test"
        str_bytes_in =  IuBinaryN.toBytes(str,value)
        str_bytes_out =  IuBinaryN.fromBytes(str_bytes_in, str)
        self.assertEqual(value, str_bytes_out)
        
    def timit_serialize_bytes(self):   
        int_bytes_in = IuBinaryN.toBytes(int,1024)
        int_bytes_out = IuBinaryN.fromBytes(int_bytes_in, int)
        
        bool_bytes_in = IuBinaryN.toBytes(bool,True)
        bool_bytes_out = IuBinaryN.fromBytes(bool_bytes_in, bool)
        
        float_bytes_in = IuBinaryN.toBytes(float,3.14)
        float_bytes_out = IuBinaryN.fromBytes(float_bytes_in, float)
         
        str_bytes_in =  IuBinaryN.toBytes(str,"Hello")
        str_bytes_out =  IuBinaryN.fromBytes(str_bytes_in, str)
        
        
    def timit_serialize_pb(self):
    
        eApiAction = EApiActionPb(
            id="1",
            time=123456789,  # Example timestamp
            version=1,  # Example version
            action="action",
            enumApiAction=EApiActionPb.EnumApiAction.NONE,
            mapEApiTypePb = MapEApiTypePb()# Setting EnumApiAction
        )
        
        print(eApiAction)
        
       
        eApiType = EApiTypePb(
            id="2",
            time=123456789, 
            version=1,  
            enumApiType=EApiTypePb.EnumApiType.NONE, 
            isOutput=False, 
            isUrl=False, 
            typeExt=".png", 
            data=b"data_png" 
        )
        print(eApiType)
    
        eApiAction.mapEApiTypePb.map[eApiType.id].CopyFrom(eApiType)
        print(eApiAction)
        
        data = eApiAction.SerializeToString()

        eApiActionOut = EApiActionPb()
        eApiActionOut.ParseFromString(data)
        print(eApiActionOut)
        

if __name__ == '__main__':
    unittest.main()