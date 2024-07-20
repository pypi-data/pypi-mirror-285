
import os
import asyncio
import sys
import platform
from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_system.utility.IuSystem import IuSystem
from evo_framework.core.evo_core_key.utility.IuKey import IuKey
from evo_framework.core.evo_core_log.utility.IuLog import IuLog
from evo_framework.core.evo_core_crypto.utility.IuCryptHash import IuCryptHash
from evo_framework.core.evo_core_crypto.utility.IuCryptEC import IuCryptEC
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
from evo_framework.core.evo_core_binary.utility.IuBinary import IuBinary
from evo_framework.core.evo_core_yaml.utility.IuYaml import IuYAml
# -------------------------------------------------------------------------
# CBoot
# -------------------------------------------------------------------------
class CBoot():
    __instance = None

    def __init__(self):
        # IuLog.doDebug(__name__,f"CFastApiServer: __init__")
        if CBoot.__instance is not None:
            raise Exception("ERROR_SINGLETON")
        else:
            super().__init__()
            CBoot.__instance = self
            self.versionServer = "20240201"
            self.mapEAction = {}

    @staticmethod
    def getInstance():
        if CBoot.__instance is None:
            CBoot()
        return CBoot.__instance
