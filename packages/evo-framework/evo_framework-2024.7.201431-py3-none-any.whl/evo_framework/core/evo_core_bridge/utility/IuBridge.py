import asyncio
import sys
from evo_framework.core.evo_core_bridge.utility.UBridge import UBridge
class IuBridge:
    @staticmethod
    async def doGetEApiConfig():
        pass
    
    @staticmethod
    def DoPathAppend(packageName:str):
        pass
    
    @staticmethod
    def doGetTotp(pathEnv:str):
        UBridge.getInstance().doGetTotp(pathEnv)