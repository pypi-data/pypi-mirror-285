#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation	https://github.com/cyborg-ai-git # 
#========================================================================================================================================

from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
from evo_framework.core.evo_core_binary.utility.IuBinary import IuBinary
from evo_framework.core.evo_core_key.utility.IuKey import IuKey
from evo_framework.core.evo_core_log.utility.IuLog import IuLog
import io
import struct

#cached
int_packer = struct.Struct('<l')
long_packer = struct.Struct('<q')
float_packer = struct.Struct('<f')
double_packer = struct.Struct('<d')
bool_packer = struct.Struct('<?')
# ---------------------------------------------------------------------------------------------------------------------------------------
# EObject
# ---------------------------------------------------------------------------------------------------------------------------------------
"""
EObject Class
    A class representing a generic entity object with methods for generating IDs and timestamps,
    and for serializing/deserializing to/from bytes and streams.
"""
class EObject(object):
    """
    EObject
    A class representing an entity with a unique ID and timestamp.
    """
    
    def __init__(self):
        """
        Initializes the EObject instance with a unique ID and the current time.
        """
        self.id: bytes = None
        self.time: int = IuKey.generateTime()
           
# ---------------------------------------------------------------------------------------------------------------------------------------
    def doGenerateID(self, id: str = None, size: int = 32):
        """
        Generates a unique ID for the EObject.
        
        Parameters:
        id (str): An optional string to base the ID on.
        size (int): The size of the ID to generate.
        """
        self.id = IuKey.generateId(id, size)

# ---------------------------------------------------------------------------------------------------------------------------------------
    def doGenerateTime(self, time: int = None):
        """
        Generates the current time for the EObject.
        
        Parameters:
        time (int): An optional time value to set.
        """
        self.time = IuKey.generateTime()

# ---------------------------------------------------------------------------------------------------------------------------------------
    def toBytes(self) -> bytes:
        """
        Serializes the EObject to a byte array.
        
        Returns:
        bytes: The byte array representation of the EObject.
        """
        with io.BytesIO() as stream:
            self.toStream(stream)
            return stream.getvalue()

# ---------------------------------------------------------------------------------------------------------------------------------------
    def fromBytes(self, data: bytes):
        """
        Deserializes the EObject from a byte array.
        
        Parameters:
        data (bytes): The byte array to deserialize.
        
        Returns:
        EObject: The deserialized EObject instance.
        """
        if data:
            with io.BytesIO(data) as stream:
                self.fromStream(stream)
            return self
        return None

# ---------------------------------------------------------------------------------------------------------------------------------------
    def toStream(self, stream):
        """
        Serializes the EObject to a stream.
        
        Parameters:
        stream (io.BytesIO): The stream to serialize to.
        """
        self._doWriteBytes(self.id, stream)
        self._doWriteLong(self.time, stream)

# ---------------------------------------------------------------------------------------------------------------------------------------
    def fromStream(self, stream):
        """
        Deserializes the EObject from a stream.
        
        Parameters:
        stream (io.BytesIO): The stream to deserialize from.
        """
        self.id = self._doReadBytes(stream)
        self.time = self._doReadLong(stream)

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doWriteStr(self, value: str, stream: io.BytesIO):
        """
        Writes a string to a stream.
        
        Parameters:
        value (str): The string to write.
        stream (io.BytesIO): The stream to write to.
        """
        if value is None:
            stream.write(int_packer.pack(-1))
        else:
            encoded = value.encode('UTF-8')
            stream.write(int_packer.pack(len(encoded)) + encoded)

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doReadStr(self, stream: io.BytesIO) -> str:
        """
        Reads a string from a stream.
        
        Parameters:
        stream (io.BytesIO): The stream to read from.
        
        Returns:
        str: The string read from the stream.
        """
        length = int_packer.unpack(stream.read(4))[0]
        if length == -1:
            return None
        return stream.read(length).decode('UTF-8')
# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doWriteInt(self, value: int, stream: io.BytesIO):
        """
        Writes an integer to a stream.
        
        Parameters:
        value (int): The integer to write.
        stream (io.BytesIO): The stream to write to.
        """
        stream.write(int_packer.pack(value if value is not None else -1))

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doReadInt(self, stream: io.BytesIO) -> int:
        """
        Reads an integer from a stream.
        
        Parameters:
        stream (io.BytesIO): The stream to read from.
        
        Returns:
        int: The integer read from the stream.
        """
        return int_packer.unpack(stream.read(4))[0]

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doWriteLong(self, value: int, stream: io.BytesIO):
        """
        Writes a long integer to a stream.
        
        Parameters:
        value (int): The long integer to write.
        stream (io.BytesIO): The stream to write to.
        """
        stream.write(long_packer.pack(value if value is not None else -1))

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doReadLong(self, stream: io.BytesIO) -> int:
        """
        Reads a long integer from a stream.
        
        Parameters:
        stream (io.BytesIO): The stream to read from.
        
        Returns:
        int: The long integer read from the stream.
        """
        return long_packer.unpack(stream.read(8))[0]

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doWriteBytes(self, value: bytes, stream: io.BytesIO):
        """
        Writes a byte array to a stream.
        
        Parameters:
        value (bytes): The byte array to write.
        stream (io.BytesIO): The stream to write to.
        """
        if value is None:
            self._doWriteInt(-1, stream)
        else:
            self._doWriteInt(len(value), stream)
            stream.write(value)

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doReadBytes(self, stream: io.BytesIO) -> bytes:
        """
        Reads a byte array from a stream.
        
        Parameters:
        stream (io.BytesIO): The stream to read from.
        
        Returns:
        bytes: The byte array read from the stream.
        """
        length = self._doReadInt(stream)
        if length == -1:
            return None
        return stream.read(length)

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doWriteFloat(self, value: float, stream: io.BytesIO):
        """
        Writes a float to a stream.
        
        Parameters:
        value (float): The float to write.
        stream (io.BytesIO): The stream to write to.
        """
        stream.write(float_packer.pack(value if value is not None else -1.0))

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doReadFloat(self, stream: io.BytesIO) -> float:
        """
        Reads a float from a stream.
        
        Parameters:
        stream (io.BytesIO): The stream to read from.
        
        Returns:
        float: The float read from the stream.
        """
        return float_packer.unpack(stream.read(4))[0]

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doWriteDouble(self, value: float, stream: io.BytesIO):
        """
        Writes a double to a stream.
        
        Parameters:
        value (float): The double to write.
        stream (io.BytesIO): The stream to write to.
        """
        stream.write(double_packer.pack(value if value is not None else -1.0))

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doReadDouble(self, stream: io.BytesIO) -> float:
        """
        Reads a double from a stream.
        
        Parameters:
        stream (io.BytesIO): The stream to read from.
        
        Returns:
        float: The double read from the stream.
        """
        return double_packer.unpack(stream.read(8))[0]

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doWriteBool(self, value: bool, stream: io.BytesIO):
        """
        Writes a boolean to a stream.
        
        Parameters:
        value (bool): The boolean to write.
        stream (io.BytesIO): The stream to write to.
        """
        stream.write(bool_packer.pack(value if value is not None else False))

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doReadBool(self, stream: io.BytesIO) -> bool:
        """
        Reads a boolean from a stream.
        
        Parameters:
        stream (io.BytesIO): The stream to read from.
        
        Returns:
        bool: The boolean read from the stream.
        """
        return bool_packer.unpack(stream.read(1))[0]

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doWriteEObject(self, value, stream: io.BytesIO):
        """
        Writes an EObject to a stream.
        
        Parameters:
        value (EObject): The EObject to write.
        stream (io.BytesIO): The stream to write to.
        """
        if value is None:
            self._doWriteBool(True, stream)
        else:
            self._doWriteBool(False,stream)
            value.toStream(stream)
        
# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doReadEObject(self, EClass, stream: io.BytesIO):
        """
        Reads an EObject from a stream.
        
        Parameters:
        EClass: The class of the EObject to read.
        stream (io.BytesIO): The stream to read from.
        
        Returns:
        EObject: The EObject read from the stream.
        """
        isNull = self._doReadBool(stream)
        if isNull:
            return None
        eObject = EClass()  
        eObject.fromStream(stream)
        return eObject

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doWriteMap(self, value, stream: io.BytesIO):
        """
        Writes a map of EObjects to a stream.
        
        Parameters:
        value (EvoMap): The map of EObjects to write.
        stream (io.BytesIO): The stream to write to.
        """
        if value is None:
            self._doWriteInt(-1, stream)
        else:
            self._doWriteInt(len(value.keys()), stream)
            for obj in value.values():
                self._doWriteEObject(obj, stream)

# ---------------------------------------------------------------------------------------------------------------------------------------
    def _doReadMap(self, EClass, stream: io.BytesIO):
        """
        Reads a map of EObjects from a stream.
        
        Parameters:
        EClass: The class of the EObjects to read.
        stream (io.BytesIO): The stream to read from.
        
        Returns:
        EvoMap: The map of EObjects read from the stream.
        """
        count = self._doReadInt(stream)  # Directly read and unpack count
        if count == -1:
            return None
        value = EvoMap()
        for _ in range(count):
            eObject = self._doReadEObject(EClass, stream)
            value.doSet(eObject)
        return value

# ---------------------------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        """
        Returns a string representation of the EObject.
        
        Returns:
        str: The string representation of the EObject.
        """
        try:
            return  "\n".join([ 
                                f"\n{self.__class__.__name__}:",
                                f"\tid: {IuKey.toString(self.id)}",   
                                f"\ttime: {self.time}",
                            ]
                            )
        except Exception as exception:
            IuLog.doError(__name__, f"ERROR_NOT_VALID_TYPE|{self.__class__.__name__} {self.id.hex()}|")
            raise exception
        

# ---------------------------------------------------------------------------------------------------------------------------------------
    def toString(self, indention=1) -> str:
        """
        Returns a string representation of the EObject with specified indentation.
        
        Parameters:
        indention (int): The number of indentation levels to apply.
        
        Returns:
        str: The string representation of the EObject with specified indentation.
        """
        indentionStr = ""
        for i in range(0, indention):
            indentionStr += "\t"
        return self.__str__().replace("\t", indentionStr)

# ---------------------------------------------------------------------------------------------------------------------------------------
    def toStringID(self) -> str:
        """
        Returns a string representation of the id with specified format hex or UTF-8.
        
        Parameters:
     
        Returns:
        str: Returns a string representation of the id with specified format hex or UTF-8.
        """
       
        return IuKey.toString(self.id)
# ---------------------------------------------------------------------------------------------------------------------------------------
    def to_dict_with_types(self):
        """
        Converts the EObject to a dictionary with attribute types.
        
        Returns:
        dict: The dictionary representation of the EObject with attribute types.
        """
        attr_dict = {}
        annotations = self.__class__.__annotations__ 

        for attr in annotations.keys():
            value = getattr(self, attr, None)
            attr_type = type(value).__name__ if value is not None else annotations[attr].__name__
            attr_dict[attr] = {'value': value, 'type': attr_type}

        # Include any additional instance attributes not present in annotations
        for attr in set(vars(self).keys()) - set(annotations.keys()):
            value = getattr(self, attr, None)
            attr_dict[attr] = {
                'value': value,
                'type': type(value).__name__
            }

        return attr_dict
# ---------------------------------------------------------------------------------------------------------------------------------------
