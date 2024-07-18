#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation	https://github.com/cyborg-ai-git # 
#========================================================================================================================================

from evo_framework.core import *
import lz4.frame
import gzip
from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
from evo_framework.core.evo_core_api.entity import *

from evo_framework.core.evo_core_api.entity.EnumApiAction import EnumApiAction
from evo_framework.core.evo_core_api.entity.EnumApiCrypto import EnumApiCrypto
from evo_framework.core.evo_core_api.entity.EnumApiCompress import EnumApiCompress
from evo_framework.core.evo_core_api.utility.IuApi import IuApi
from evo_framework.core.evo_core_crypto import *
from evo_framework.core.evo_core_log import *
from evo_framework.core.evo_core_key import *
from evo_framework.core.evo_core_system import *

from evo_framework.core.evo_core_binary.utility.IuBinary import IuBinary
from evo_framework.core.evo_core_setting.control.CSetting import CSetting
from evo_framework.core.evo_core_text.utility.IuText import IuText
from PIL import Image
#import magic
import importlib
import subprocess

# ---------------------------------------------------------------------------------------------------------------------------------------
class IuFoundation(object):
# ---------------------------------------------------------------------------------------------------------------------------------------       
    @staticmethod
    def toPack(data:bytes ) -> bytes:
        try:
          
           return None
           
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception
        
# ---------------------------------------------------------------------------------------------------------------------------------------      
    @staticmethod
    def fromPack(data:bytes ) -> bytes:
        try:
          
           return None
           
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise exception