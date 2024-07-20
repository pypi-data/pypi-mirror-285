#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git |
#========================================================================================================================================
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os
# ------------------------------------------------------------------------------------------------
class IuCryptChacha:
    @staticmethod
    def generateKey() -> bytes:
        """Generates a random 32-byte key."""
        return os.urandom(32)
# ------------------------------------------------------------------------------------------------   
    @staticmethod
    def generateNonce() -> bytes:
        """Generates a random 12-byte nonce."""
        return os.urandom(12)
# ------------------------------------------------------------------------------------------------
    @staticmethod
    def doEncrypt(key: bytes, plaintext: bytes, nonce: bytes) -> bytes:
        """Encrypts the plaintext using the provided key and nonce, 
        returning the combined data (nonce + ciphertext + tag)."""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes long.")
        if len(nonce) != 12:
            raise ValueError("Nonce must be 12 bytes long.")
        chacha = ChaCha20Poly1305(key)
        # Encrypt and directly return the combined data
        ciphertext = chacha.encrypt(nonce, plaintext, None)
        return nonce + ciphertext 
# ------------------------------------------------------------------------------------------------   
    @staticmethod
    def doDecrypt(key: bytes, cipher: bytes, nonce:bytes) -> bytes:

        if len(key) != 32:
            raise ValueError("Key must be 32 bytes long.")
        chacha = ChaCha20Poly1305(key)
        return chacha.decrypt(nonce, cipher, None)
# ------------------------------------------------------------------------------------------------
    @staticmethod
    def doDecryptCombined(key: bytes, combined: bytes) -> bytes:
        """Decrypts the combined data (nonce + ciphertext + tag) using the provided key, 
        returning the plaintext."""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes long.")
        nonce = combined[:12]  # Extract the nonce from the beginning
        cipher = combined[12:]  # The rest is ciphertext + tag
        chacha = ChaCha20Poly1305(key)
        return chacha.decrypt(nonce, cipher, None)
# ------------------------------------------------------------------------------------------------