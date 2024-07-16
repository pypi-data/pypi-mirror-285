import ecdsa
from ecdsa.util import sigencode_string, sigdecode_string
from evo_framework.core.evo_core_convert.utility.IuConvert import IuConvert
import base64
import hashlib
class IuCryptEC:
    @staticmethod
    def generate_key_pair():
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        pk = sk.verifying_key
        return sk, pk
    
    @staticmethod
    def get_key_pair(private_key_str):
        sk_bytes = IuConvert.fromBase64(private_key_str)
        sk = ecdsa.SigningKey.from_string(sk_bytes, hashfunc=hashlib.sha256, curve=ecdsa.SECP256k1)
        pk = sk.verifying_key
        return sk, pk

    @staticmethod
    def sign_data(data, private_key):
        signature = private_key.sign(data, sigencode=sigencode_string) 
        return signature

    @staticmethod
    def verify_data(data, signature, public_key):
        try:
            pk = IuCryptEC.get_public_key_from_bytes(public_key)
            return pk.verify(signature, data, sigdecode=sigdecode_string)
        except ecdsa.BadSignatureError:
            return False
        
    @staticmethod
    def get_private_key_from_bytes(private_key_bytes):
        return ecdsa.SigningKey.from_string(private_key_bytes, hashfunc=hashlib.sha256, curve=ecdsa.SECP256k1)

    @staticmethod
    def get_public_key_from_bytes(public_key_bytes):
        return ecdsa.VerifyingKey.from_string(public_key_bytes, hashfunc=hashlib.sha256, curve=ecdsa.SECP256k1)
