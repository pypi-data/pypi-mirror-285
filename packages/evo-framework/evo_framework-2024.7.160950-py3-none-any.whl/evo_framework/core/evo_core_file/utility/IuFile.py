#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git |
#========================================================================================================================================
import os
class IuFile:
    @staticmethod
    def doCreateDirs(path:str):
        if not os.path.exists(path):
            os.makedirs(path)