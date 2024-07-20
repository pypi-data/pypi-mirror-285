#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git |
#========================================================================================================================================
from evo_framework.core.evo_core_crypto.utility.IuCryptHash import IuCryptHash
from evo_framework.core.evo_core_crypto.utility.IuCryptChacha import IuCryptChacha
from evo_framework.core.evo_core_text.utility.IuText import IuText
import lz4.frame
import yaml
import lz4
import base64
import os
import re
class IuSettings:
# ------------------------------------------------------------------------------------------------
    @staticmethod
    def doEncryptSettings(mapSettings:dict) ->str:
        secretEnv =os.environ.get('CYBORGAI_SECRET')
        if secretEnv is None:
            raise Exception("ERROR_CYBORGAI_SECRET_REQUIRED")
        
        if mapSettings is None:
            raise Exception("ERROR_mapSettings_REQUIRED")
        
        strYaml=yaml.dump(mapSettings)
        dataYaml=strYaml.encode()
        arraySecret=secretEnv.split("~")
        dataKey =  base64.b64decode(arraySecret[0])
        dataNonce= base64.b64decode(arraySecret[1])
        dataCrypt=IuCryptChacha.doEncrypt(dataKey, dataYaml, dataNonce)
        dataCompress = lz4.frame.compress(dataCrypt)
        dataBase64 = base64.b64encode(dataCompress)
        return dataBase64.decode('utf-8')
    
# ------------------------------------------------------------------------------------------------   
    @staticmethod
    def doDecryptSettings(strBase64:str) ->dict:
        secretEnv =os.environ.get('CYBORGAI_SECRET')
        if secretEnv is None:
            raise Exception("ERROR_CYBORGAI_SECRET_REQUIRED")

        if strBase64 is None:
            raise Exception("ERROR_strBase64_NONE")
        
        arraySecret=secretEnv.split("~")
        dataKey =  base64.b64decode(arraySecret[0])
        ## dataNonce= base64.b64decode(arraySecret[1])
        dataCompress = base64.b64decode(strBase64)
        dataDecompress = lz4.frame.decompress(dataCompress)
        dataPlain = IuCryptChacha.doDecryptCombined(dataKey, dataDecompress)
        strPlain= dataPlain.decode()
        
        return yaml.safe_load(strPlain)
# ------------------------------------------------------------------------------------------------
    @staticmethod
    def doEncrypt(mapSettings:dict, secretBase64:str) ->str:
        
        if secretBase64 is None:
            raise Exception("ERROR_CYBORGAI_SECRET_REQUIRED")
        
        if mapSettings is None:
            raise Exception("ERROR_mapSettings_REQUIRED")
        
        strYaml=yaml.dump(mapSettings)
        dataYaml=strYaml.encode()
        arraySecret=secretBase64.split("~")
        dataKey =  base64.b64decode(arraySecret[0])
        dataNonce= base64.b64decode(arraySecret[1])
        dataCrypt=IuCryptChacha.doEncrypt(dataKey, dataYaml, dataNonce)
        dataCompress = lz4.frame.compress(dataCrypt)
        dataBase64 = base64.b64encode(dataCompress)
        return dataBase64.decode('utf-8')
    
# ------------------------------------------------------------------------------------------------   
    @staticmethod
    def doDecrypt(strBase64:str, secretBase64:str) ->dict:
       
        if secretBase64 is None:
            raise Exception("ERROR_CYBORGAI_SECRET_REQUIRED")

        if strBase64 is None:
            raise Exception("ERROR_strBase64_NONE")
        
        arraySecret=secretBase64.split("~")
        dataKey =  base64.b64decode(arraySecret[0])
        ## dataNonce= base64.b64decode(arraySecret[1])
        dataCompress = base64.b64decode(strBase64)
        dataDecompress = lz4.frame.decompress(dataCompress)
        dataPlain = IuCryptChacha.doDecryptCombined(dataKey, dataDecompress)
        strPlain= dataPlain.decode()
        
        return yaml.safe_load(strPlain)

# ------------------------------------------------------------------------------------------------   
    @staticmethod   
    def doGenerateSettingsBase64(file_path) :
        with open(file_path, 'r') as file:
            env_content = file.read()

        # Regular expression pattern to match key-value pairs
        pattern = r"(\w+)\s*=\s*'([^']*)'"

        # Find all matches using re.findall, which returns a list of tuples (key, value)
        key_value_pairs = re.findall(pattern, env_content)

        # Convert the list of tuples to a dictionary
        mapSettings = {key: value for key, value in key_value_pairs}
        CYBORGAI_SECRET=mapSettings["CYBORGAI_SECRET"]
        
        CYBORGAI_EXTERNAL_PORT=443
        if CYBORGAI_EXTERNAL_PORT in mapSettings:
            CYBORGAI_EXTERNAL_PORT=mapSettings["CYBORGAI_EXTERNAL_PORT"]
        
    
        if "CYBORGAI_SETTINGS" in mapSettings:
            settings=mapSettings["CYBORGAI_SETTINGS"]
        
            if not IuText.StringEmpty(settings):
            
                mapSettingSecret = IuSettings.doDecrypt(settings, CYBORGAI_SECRET)
                
            
                #print(mapSettingSecret)
                CYBORGAI_ID=mapSettingSecret["CYBORGAI_ID"]
                CYBORGAI_SK=mapSettingSecret["CYBORGAI_SK"]
                
                mapSettings["CYBORGAI_ID"]=CYBORGAI_ID
                mapSettings["CYBORGAI_SK"]=CYBORGAI_SK
                
                del mapSettings["CYBORGAI_SETTINGS"]
                #del mapSettings["ACCESS_TOKEN_OPENAI"]
                #del mapSettings["DIRECTORY_AUTOMATION"]
                del mapSettings["CYBORGAI_SECRET"]
                

                CYBORGAI_SETTINGS = IuSettings.doEncrypt(mapSettings, CYBORGAI_SECRET)
                
                return CYBORGAI_SECRET, CYBORGAI_SETTINGS, CYBORGAI_EXTERNAL_PORT
        
        return CYBORGAI_SECRET, "", CYBORGAI_EXTERNAL_PORT
   