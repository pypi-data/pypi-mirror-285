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
# CActionApi
# ------------------------------------------------------------------------------------------------
class CApi():

# ------------------------------------------------------------------------------------------------
    def __init__(self):
            super().__init__()
            self.mapEApi = EvoMap()
            self.mapEApiMap = EvoMap()
            self.current_path = os.path.dirname(os.path.abspath(__file__))
            
            
# ------------------------------------------------------------------------------------------------          
    @abstractmethod
    def doAddApi(self):
        pass
# ------------------------------------------------------------------------------------------------
    async def doAction(self, eAction):
        try:
            IuLog.doVerbose(__name__, f"doAction: {eAction}")
            
            await CApiFlow.getInstance().doActionCallBack(eAction)
            
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise
# ------------------------------------------------------------------------------------------------
    
    def newApi(self, id:str, callback, input:Type, output:Type, isEnabled=True, description:str="") -> EApi:
        try: 
            eApi = EApi()
            eApi.id = IuKey.generateId(id)

            eApi.callback = callback
            eApi.description = description
            eApi.isEnabled = isEnabled
            
            if hasattr(input, "VERSION"):
                 eApi.input = f"{input.__module__}|{input.VERSION}"
            else:
                raise Exception(f"ERROR_NOT_VALID_INPUT_ECLASS_{input.__module__}")
            
            if hasattr(output, "VERSION"):
                 eApi.output = f"{output.__module__}|{output.VERSION}"
            else:
                raise Exception(f"ERROR_NOT_VALID_OUTPUT_ECLASS_{output.__module__}")
            
            if eApi.isEnabled:
                self.mapEApi.doSet(eApi)
                self.doSetEApi(eApi)
            
            return eApi     
        except Exception as exception:
            IuLog.doException(__name__,exception)
            raise exception

# ---------------------------------------------------------------------------------------------------------------------------------------
    def doSetEApi(self, eApi: EApi):
        try:
            CApiFlow.getInstance().eApiConfig.mapEApi.doSet(eApi)
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise
'''
    # ---------------------------------------------------------------------------------------------------------------------------------------
    def doGetEApi(self, action) -> EApi:
        try:
            eApi = CApiFlow.getInstance().eApiConfig.mapEApi.doGet(IuKey.generateId(action))

            if isinstance(eApi, EApi):
                return eApi

            else:
                raise Exception(f"ERROR_NOT_VALID|api|{action}")
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise 

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
'''