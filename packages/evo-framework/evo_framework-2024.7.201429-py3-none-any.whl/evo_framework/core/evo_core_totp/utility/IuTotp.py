#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git |
#========================================================================================================================================

from evo_framework.core.evo_core_log.utility.IuLog import IuLog

import pyotp
class IuTotp:
    @staticmethod
    def doGenerateUrl(randBase32,name, issuerName) -> str:
        try:         
            urlOtp = pyotp.totp.TOTP(randBase32).provisioning_uri(name=name, issuer_name=issuerName)         
            return urlOtp
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
    @staticmethod
    def doGenerateRand() -> str:
        try:
            randBase32=pyotp.random_base32()     
            return randBase32
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception
        
    @staticmethod
    def getTotp(randBase32) -> str:
        try:
            totp = pyotp.TOTP(randBase32)
            return totp.now()
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception