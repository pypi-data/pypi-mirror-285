import base64
class IuConvert:
    @staticmethod
    def toBase64(data: bytes, charset: str = 'utf-8') -> str:
        # Encode bytes to base64 and decode it using the specified charset
        return base64.b64encode(data).decode(charset)

    @staticmethod
    def fromBase64(strBase64: str, charset: str = 'utf-8') -> bytes:
        # Decode a base64 string to bytes
        return base64.b64decode(strBase64)

    @staticmethod
    def toHex(data: bytes) -> str:
        # Return hexadecimal string representation of bytes
        if data is None:
            return "NONE"
        else:
            return data.hex()

    @staticmethod
    def fromHex(strHex: str) -> bytes:
        # Convert a hex string back to bytes
        if strHex is None:
            return b"NONE"
        else:
            return bytes.fromhex(strHex)
       