
import hashlib
class IuCryptHash:
    @staticmethod
    def toSha256(input):
        if input is None:
            return "SHA256_NONE"
        if isinstance(input,str):
            input_bytes = input.encode('utf-8')
        else:
            input_bytes = input         
        sha256_hash = hashlib.sha256(input_bytes)
        hash_hex = sha256_hash.hexdigest()
        return hash_hex
    
    @staticmethod
    def toSha256Bytes(input) -> bytes:
        if input is None:
            return b"SHA256_NONE"  # Return bytes
        if isinstance(input, str):
            input_bytes = input.encode('utf-8')
        else:
            input_bytes = input
        sha256_hash = hashlib.sha256(input_bytes)
        return sha256_hash.digest()