from enum import IntEnum

class EnumApiCompress(IntEnum):
    NONE = 0
    GZIP = 1
    LZ4 = 2
    ZIP = 3