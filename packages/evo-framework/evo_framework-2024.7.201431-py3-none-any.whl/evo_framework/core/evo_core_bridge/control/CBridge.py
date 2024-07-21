#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git |
#========================================================================================================================================
from evo_framework.core import *
from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap
from evo_framework.core.evo_core_log.utility.IuLog import IuLog
from evo_framework.core.evo_core_key.utility.IuKey import IuKey
from evo_framework.core.evo_core_api.control.CApiFlow import CApiFlow
from evo_framework.core.evo_core_api.entity.EApi import EApi
from evo_framework.core.evo_core_api.entity.EnumApiType import EnumApiType

# ------------------------------------------------------------------------------------------------
# CBridge
# ------------------------------------------------------------------------------------------------
class CBridge():

# ------------------------------------------------------------------------------------------------
    def __init__(self):
            super().__init__()
            self.mapEApi = EvoMap()
            self.mapEApiMap = EvoMap()
            self.current_path = os.path.dirname(os.path.abspath(__file__))
            
            
# ------------------------------------------------------------------------------------------------          
    @abstractmethod
    def onRequest(self):
        pass
    
# ------------------------------------------------------------------------------------------------          
    @abstractmethod
    def onResponse(self):
        pass

# ---------------------------------------------------------------------------------------------------------------------------------------
    def doPrintMapEApi(self):
        try:
            listStr = ""
            count = 1
            for key in CApiFlow.getInstance().eApiConfig.mapEApi.keys():
                eApi: EApi = CApiFlow.getInstance().eApiConfig.mapEApi.doGet(key)
                callback = eApi.callback
                idApi = eApi.toStringID()
                countStr = str(count).ljust(4, " ")
                listStr = "\n".join(
                    [
                        listStr,
                        (
                            f"{countStr} {idApi}:\n" 
                            + f"\t\tinput: {eApi.input}\n" 
                            + f"\t\toutput: {eApi.output}\n" 
                            + f"\t\tcallback: {callback.__module__}.{callback.__name__}\n"   
                            ),
                    ]
                )
                count += 1

            IuLog.doInfo("api", f"{listStr}\n")

        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise 
# ---------------------------------------------------------------------------------------------------------------------------------------
