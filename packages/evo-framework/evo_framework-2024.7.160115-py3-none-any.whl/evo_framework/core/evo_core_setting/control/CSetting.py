#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git |
#========================================================================================================================================

import base64
import json
import os
import lz4.frame
from evo_framework.core.evo_core_setting.entity.ESetting import ESetting
from evo_framework.core.evo_core_log.utility.IuLog import IuLog
from evo_framework.core.evo_core_system.utility.IuSystem import IuSystem
from evo_framework.core.evo_core_setting.utility.IuSettings import IuSettings
from evo_framework.core.evo_core_text.utility.IuText import IuText
from urllib.parse import unquote
current_path = os.path.dirname(os.path.abspath(__file__))
#----------------------------------------------------------------------------------------------------------------------------------------
class CSetting:
    __instance = None
#----------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getInstance():
        """ Static access method. """
        if CSetting.__instance == None:
            cObject = CSetting()
            cObject.doInit()
        return CSetting.__instance
#----------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        if CSetting.__instance != None:
            raise Exception("ERROR:SINGLETON")
        else:
            CSetting.__instance = self
            self.mapSetting = {}
#----------------------------------------------------------------------------------------------------------------------------------------            
    def doInit(self):
        try:
            self.eSettings = ESetting()
            try:
               self.eSettings.path_output =  IuSystem.do_sanitize_path( f"{current_path}/../../../../assets/")
            except Exception as exception:
                IuLog.doException(__name__,exception)
            
            secretEnv =os.environ.get('CYBORGAI_SECRET')
            
            if IuText.StringEmpty(secretEnv):
                raise Exception("ERROR_CYBORGAI_SECRET_REQUIRED")
            
            settingsEnv =os.environ.get('CYBORGAI_SETTINGS')
            
            if IuText.StringEmpty(settingsEnv):
                IuLog.doError(__name__,"ERROR_CYBORGAI_SETTINGS_environment_EMPTY copy in .env first start")
            else:
                mapSettingsTmp =  IuSettings.doDecryptSettings(settingsEnv)
                
                if mapSettingsTmp is None:
                    raise Exception("ERROR_DECRYPT_CYBORGAI_SETTINGS")
                
                self.mapSetting = mapSettingsTmp
                
                passwordEnv=self.doGet('CYBORGAI_PASSWORD')
                
                if IuText.StringEmpty(passwordEnv):
                    raise Exception("ERROR_CYBORGAI_PASSWORD_REQUIRED")
                
                if len(passwordEnv) <16:
                    raise Exception("ERROR_CYBORGAI_PASSWORD_LENGTH<16")

                self.mapSetting = mapSettingsTmp
                
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise
#---------------------------------------------------------------------------------------------------------------------------------------- 
    def doGet(self, key:str):
        try:
            value = self.mapSetting.get(key)
            
            if value is None:
                value = os.environ.get(key) 
                if value is not None:
                    self.mapSetting[key] = value
                              
            IuLog.doVerbose(__name__,f"{key} => value")
            return value
        except Exception as exception:
            IuLog.doError(__name__,f"{exception}")
            return None
#----------------------------------------------------------------------------------------------------------------------------------------       