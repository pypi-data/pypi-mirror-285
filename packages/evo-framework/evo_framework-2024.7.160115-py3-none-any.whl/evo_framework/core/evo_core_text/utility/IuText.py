#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git |
#========================================================================================================================================

from evo_framework.core.evo_core_log.utility.IuLog import IuLog

import pyotp
class IuText:
    @staticmethod
    def StringEmpty(string:str) -> bool:
        if string is None or string == "":
            return True
        return False
        